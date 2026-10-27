from app.extensions import db
from app.models.base import TimestampMixin

ORDER_STATUSES = ("draft", "pending_approval", "approved", "confirmed", "in_delivery", "received", "closed", "cancelled")


class Supplier(TimestampMixin, db.Model):
    __tablename__ = "suppliers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), unique=True, nullable=False)
    contact_name = db.Column(db.String(120))
    phone = db.Column(db.String(30))
    email = db.Column(db.String(160))
    address = db.Column(db.String(255))
    payment_terms = db.Column(db.String(80), default="Virement à 30 jours")
    is_active = db.Column(db.Boolean, nullable=False, default=True)


class PurchaseRequest(TimestampMixin, db.Model):
    __tablename__ = "purchase_requests"

    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(20), unique=True, nullable=False)
    store_id = db.Column(db.ForeignKey("stores.id"), nullable=False)
    requested_by_id = db.Column(db.ForeignKey("users.id"), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="open")  # open | converted | rejected
    note = db.Column(db.String(255))

    lines = db.relationship("PurchaseRequestLine", cascade="all, delete-orphan")


class PurchaseRequestLine(db.Model):
    __tablename__ = "purchase_request_lines"

    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.ForeignKey("purchase_requests.id", ondelete="CASCADE"), nullable=False)
    product_id = db.Column(db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Numeric(12, 3), nullable=False)


class PurchaseOrder(TimestampMixin, db.Model):
    __tablename__ = "purchase_orders"

    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(20), unique=True, nullable=False)  # BC-2026-0842
    supplier_id = db.Column(db.ForeignKey("suppliers.id"), nullable=False)
    store_id = db.Column(db.ForeignKey("stores.id"), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="draft")
    expected_at = db.Column(db.DateTime(timezone=True))
    payment_terms = db.Column(db.String(80))
    total = db.Column(db.BigInteger, nullable=False, default=0)  # FCFA TTC
    created_by_id = db.Column(db.ForeignKey("users.id"), nullable=False)
    responsible_id = db.Column(db.ForeignKey("users.id"))
    approved_by_id = db.Column(db.ForeignKey("users.id"))
    approved_at = db.Column(db.DateTime(timezone=True))
    confirmed_at = db.Column(db.DateTime(timezone=True))

    supplier = db.relationship("Supplier")
    store = db.relationship("Store")
    lines = db.relationship("PurchaseOrderLine", back_populates="order", cascade="all, delete-orphan")


class PurchaseOrderLine(db.Model):
    __tablename__ = "purchase_order_lines"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.ForeignKey("purchase_orders.id", ondelete="CASCADE"), nullable=False)
    product_id = db.Column(db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Numeric(12, 3), nullable=False)
    unit_cost = db.Column(db.BigInteger, nullable=False)
    received_qty = db.Column(db.Numeric(12, 3), nullable=False, default=0)

    order = db.relationship("PurchaseOrder", back_populates="lines")
    product = db.relationship("Product")


class Receipt(TimestampMixin, db.Model):
    __tablename__ = "receipts"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.ForeignKey("purchase_orders.id"), nullable=False)
    store_id = db.Column(db.ForeignKey("stores.id"), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="draft")  # draft | validated
    received_by_id = db.Column(db.ForeignKey("users.id"), nullable=False)
    validated_at = db.Column(db.DateTime(timezone=True))

    order = db.relationship("PurchaseOrder")
    lines = db.relationship("ReceiptLine", cascade="all, delete-orphan")


class ReceiptLine(db.Model):
    __tablename__ = "receipt_lines"

    id = db.Column(db.Integer, primary_key=True)
    receipt_id = db.Column(db.ForeignKey("receipts.id", ondelete="CASCADE"), nullable=False)
    order_line_id = db.Column(db.ForeignKey("purchase_order_lines.id"), nullable=False)
    accepted_qty = db.Column(db.Numeric(12, 3), nullable=False, default=0)
    refused_qty = db.Column(db.Numeric(12, 3), nullable=False, default=0)
    lot_number = db.Column(db.String(40))
    expiry_date = db.Column(db.Date)
    reject_reason = db.Column(db.String(255))
