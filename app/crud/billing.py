from sqlalchemy.orm import Session, joinedload
from app.models.billing import Bill, BillItem
from app.schemas.billing import BillCreate, BillUpdate
from typing import Optional, List


def generate_bill_code(db: Session) -> str:
    """Generate a unique bill code"""
    last_bill = db.query(Bill).order_by(Bill.id.desc()).first()
    next_num = (last_bill.id + 1) if last_bill else 1
    return f"BILL-{next_num:04d}"


def calculate_totals(items: List, discount_percent: float, tax_percent: float, paid_amount: float):
    """
    Core billing calculation:
      subtotal   = sum(quantity * unit_price) for every item
      discount   = subtotal * discount_percent / 100
      taxable    = subtotal - discount
      tax        = taxable * tax_percent / 100
      total      = taxable + tax
      due        = total - paid_amount
    """
    subtotal = 0.0
    computed_items = []
    for item in items:
        amount = round(float(item.quantity) * float(item.unit_price), 2)
        computed_items.append({
            "description": item.description,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "amount": amount
        })
        subtotal += amount

    subtotal = round(subtotal, 2)
    discount_percent = discount_percent or 0.0
    tax_percent = tax_percent or 0.0
    paid_amount = paid_amount or 0.0

    discount_amount = round(subtotal * discount_percent / 100, 2)
    taxable_amount = subtotal - discount_amount
    tax_amount = round(taxable_amount * tax_percent / 100, 2)
    total_amount = round(taxable_amount + tax_amount, 2)
    due_amount = round(total_amount - paid_amount, 2)

    if due_amount <= 0:
        payment_status = "paid"
        due_amount = 0.0
    elif paid_amount > 0:
        payment_status = "partial"
    else:
        payment_status = "unpaid"

    return {
        "items": computed_items,
        "subtotal": subtotal,
        "discount_amount": discount_amount,
        "tax_amount": tax_amount,
        "total_amount": total_amount,
        "due_amount": due_amount,
        "payment_status": payment_status
    }


def get_bill(db: Session, bill_id: int):
    """Get a single bill with patient, doctor and items"""
    return db.query(Bill).options(
        joinedload(Bill.patient),
        joinedload(Bill.doctor),
        joinedload(Bill.appointment),
        joinedload(Bill.items)
    ).filter(Bill.id == bill_id).first()


def get_bill_by_code(db: Session, bill_code: str):
    return db.query(Bill).filter(Bill.bill_code == bill_code).first()


def get_bills(db: Session, skip: int = 0, limit: int = 100,
              patient_id: Optional[int] = None,
              doctor_id: Optional[int] = None,
              payment_status: Optional[str] = None):
    """Get bills with optional filters"""
    query = db.query(Bill).options(
        joinedload(Bill.patient),
        joinedload(Bill.doctor),
        joinedload(Bill.items)
    )
    if patient_id:
        query = query.filter(Bill.patient_id == patient_id)
    if doctor_id:
        query = query.filter(Bill.doctor_id == doctor_id)
    if payment_status:
        query = query.filter(Bill.payment_status == payment_status)

    return query.order_by(Bill.id.desc()).offset(skip).limit(limit).all()


def get_bills_by_patient(db: Session, patient_id: int):
    return db.query(Bill).filter(Bill.patient_id == patient_id).order_by(Bill.id.desc()).all()


def create_bill(db: Session, bill: BillCreate):
    """Create a bill along with its line items"""
    calc = calculate_totals(bill.items, bill.discount_percent, bill.tax_percent, bill.paid_amount)

    db_bill = Bill(
        bill_code=generate_bill_code(db),
        patient_id=bill.patient_id,
        doctor_id=bill.doctor_id,
        appointment_id=bill.appointment_id,
        bill_date=bill.bill_date,
        subtotal=calc["subtotal"],
        discount_percent=bill.discount_percent,
        discount_amount=calc["discount_amount"],
        tax_percent=bill.tax_percent,
        tax_amount=calc["tax_amount"],
        total_amount=calc["total_amount"],
        paid_amount=bill.paid_amount,
        due_amount=calc["due_amount"],
        payment_status=calc["payment_status"],
        payment_method=bill.payment_method,
        notes=bill.notes
    )
    db.add(db_bill)
    db.commit()
    db.refresh(db_bill)

    for item in calc["items"]:
        db.add(BillItem(bill_id=db_bill.id, **item))
    db.commit()
    db.refresh(db_bill)
    return db_bill


class _ItemLike:
    """Small helper so existing BillItem rows can be re-run through calculate_totals()"""
    def __init__(self, description, quantity, unit_price):
        self.description = description
        self.quantity = quantity
        self.unit_price = unit_price


def update_bill(db: Session, bill_id: int, bill: BillUpdate):
    """Update a bill. If new items are supplied, old items are replaced and totals recalculated."""
    db_bill = get_bill(db, bill_id)
    if not db_bill:
        return None

    if bill.items is not None:
        # Replace items entirely
        db.query(BillItem).filter(BillItem.bill_id == bill_id).delete()
        items_for_calc = bill.items
    else:
        # Recalculate using existing items (e.g. only discount/tax/paid changed)
        items_for_calc = [_ItemLike(i.description, i.quantity, i.unit_price) for i in db_bill.items]

    discount_percent = bill.discount_percent if bill.discount_percent is not None else db_bill.discount_percent
    tax_percent = bill.tax_percent if bill.tax_percent is not None else db_bill.tax_percent
    paid_amount = bill.paid_amount if bill.paid_amount is not None else db_bill.paid_amount

    calc = calculate_totals(items_for_calc, discount_percent, tax_percent, paid_amount)

    update_data = bill.model_dump(exclude_unset=True, exclude={"items"})
    for key, value in update_data.items():
        setattr(db_bill, key, value)

    db_bill.discount_percent = discount_percent
    db_bill.tax_percent = tax_percent
    db_bill.paid_amount = paid_amount
    db_bill.subtotal = calc["subtotal"]
    db_bill.discount_amount = calc["discount_amount"]
    db_bill.tax_amount = calc["tax_amount"]
    db_bill.total_amount = calc["total_amount"]
    db_bill.due_amount = calc["due_amount"]
    db_bill.payment_status = calc["payment_status"]

    if bill.items is not None:
        for item in calc["items"]:
            db.add(BillItem(bill_id=db_bill.id, **item))

    db.commit()
    db.refresh(db_bill)
    return db_bill


def delete_bill(db: Session, bill_id: int):
    db_bill = get_bill(db, bill_id)
    if db_bill:
        db.delete(db_bill)
        db.commit()
        return True
    return False


def record_payment(db: Session, bill_id: int, amount: float):
    """Add a payment towards a bill and recalculate due amount / status"""
    db_bill = get_bill(db, bill_id)
    if not db_bill:
        return None

    db_bill.paid_amount = round((db_bill.paid_amount or 0) + amount, 2)
    db_bill.due_amount = round(db_bill.total_amount - db_bill.paid_amount, 2)

    if db_bill.due_amount <= 0:
        db_bill.due_amount = 0.0
        db_bill.payment_status = "paid"
    elif db_bill.paid_amount > 0:
        db_bill.payment_status = "partial"
    else:
        db_bill.payment_status = "unpaid"

    db.commit()
    db.refresh(db_bill)
    return db_bill
