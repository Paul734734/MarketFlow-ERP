from app.extensions import db
from app.models.base import TimestampMixin

PAYMENT_METHODS = ("cash", "mobile", "card")
SALE_STATUSES = ("held", "paid", "to_reconcile", "refunded")


class Customer(TimestampMixin, db.Model):
    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False, index=True)
    phone = db.Column(db.String(30))
    email = db.Column(db.String(160))
    credit_limit = db.Column(db.BigInteger, nullable=False, default=0)


class CashSession(TimestampMixin, db.Model):
    __tablename__ = "cash_sessions"

    id = db.Column(db.Integer, primary_key=True)
    register_id = db.Column(db.ForeignKey("registers.id"), nullable=False)
    opened_by_id = db.Column(db.ForeignKey("users.id"), nullable=False)
    opened_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), nullable=False)
    closed_at = db.Column(db.DateTime(timezone=True))
    opening_float = db.Column(db.BigInteger, nullable=False, default=0)
    counted_amount = db.Column(db.BigInteger)
    status = db.Column(db.String(10), nullable=False, default="open")  # open | closed

    register = db.relationship("Register")


class Sale(TimestampMixin, db.Model):
    __tablename__ = "sales"
    __table_args__ = (db.Index("ix_sale_store_date", "store_id", "sold_at"),)

    id = db.Column(db.Integer, primary_key=True)
    ticket_number = db.Column(db.String(20), unique=True, nullable=False)  # T-AK-0321
    store_id = db.Column(db.ForeignKey("stores.id"), nullable=False)
    register_id = db.Column(db.ForeignKey("registers.id"), nullable=False)
    session_id = db.Column(db.ForeignKey("cash_sessions.id"))
    cashier_id = db.Column(db.ForeignKey("users.id"), nullable=False)
    customer_id = db.Column(db.ForeignKey("customers.id"))
    status = db.Column(db.String(20), nullable=False, default="paid")
    subtotal = db.Column(db.BigInteger, nullable=False, default=0)
    discount = db.Column(db.BigInteger, nullable=False, default=0)
    vat_amount = db.Column(db.BigInteger, nullable=False, default=0)
    total = db.Column(db.BigInteger, nullable=False, default=0)  # FCFA TTC
    sold_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), nullable=False)

    store = db.relationship("Store")
    customer = db.relationship("Customer")
    lines = db.relationship("SaleLine", back_populates="sale", cascade="all, delete-orphan")
    payments = db.relationship("Payment", back_populates="sale", cascade="all, delete-orphan")


class SaleLine(db.Model):
    __tablename__ = "sale_lines"

    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.ForeignKey("sales.id", ondelete="CASCADE"), nullable=False)
    product_id = db.Column(db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Numeric(12, 3), nullable=False)
    unit_price = db.Column(db.BigInteger, nullable=False)
    discount = db.Column(db.BigInteger, nullable=False, default=0)
    total = db.Column(db.BigInteger, nullable=False)

    sale = db.relationship("Sale", back_populates="lines")
    product = db.relationship("Product")


class Payment(TimestampMixin, db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.ForeignKey("sales.id", ondelete="CASCADE"), nullable=False)
    method = db.Column(db.String(10), nullable=False)
    amount = db.Column(db.BigInteger, nullable=False)
    received = db.Column(db.BigInteger)  # montant reçu (espèces)
    change_given = db.Column(db.BigInteger, nullable=False, default=0)
    reference = db.Column(db.String(60))
    reconciled = db.Column(db.Boolean, nullable=False, default=True)

    sale = db.relationship("Sale", back_populates="payments")


class SaleReturn(TimestampMixin, db.Model):
    __tablename__ = "sale_returns"

    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.ForeignKey("sales.id"), nullable=False)
    amount = db.Column(db.BigInteger, nullable=False)
    reason = db.Column(db.String(255))
    created_by_id = db.Column(db.ForeignKey("users.id"), nullable=False)
