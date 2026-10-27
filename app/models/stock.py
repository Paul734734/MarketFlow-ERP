from app.extensions import db
from app.models.base import TimestampMixin

MOVEMENT_KINDS = (
    "reception",
    "sale",
    "return",
    "transfer_in",
    "transfer_out",
    "adjustment",
    "inventory",
    "loss",
)


class StockLevel(TimestampMixin, db.Model):
    __tablename__ = "stock_levels"
    __table_args__ = (db.UniqueConstraint("store_id", "product_id", name="uq_stock_store_product"),)

    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.ForeignKey("stores.id", ondelete="CASCADE"), nullable=False)
    product_id = db.Column(db.ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    quantity = db.Column(db.Numeric(12, 3), nullable=False, default=0)
    min_quantity = db.Column(db.Numeric(12, 3))  # surcharge du seuil produit

    store = db.relationship("Store")
    product = db.relationship("Product")


class Lot(TimestampMixin, db.Model):
    __tablename__ = "lots"
    __table_args__ = (
        db.UniqueConstraint("store_id", "product_id", "lot_number", name="uq_lot"),
    )

    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.ForeignKey("stores.id", ondelete="CASCADE"), nullable=False)
    product_id = db.Column(db.ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    lot_number = db.Column(db.String(40), nullable=False)
    expiry_date = db.Column(db.Date)
    quantity = db.Column(db.Numeric(12, 3), nullable=False, default=0)


class StockMovement(db.Model):
    __tablename__ = "stock_movements"
    __table_args__ = (db.Index("ix_movement_store_product_date", "store_id", "product_id", "created_at"),)

    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.ForeignKey("stores.id"), nullable=False)
    product_id = db.Column(db.ForeignKey("products.id"), nullable=False)
    lot_id = db.Column(db.ForeignKey("lots.id"))
    kind = db.Column(db.String(20), nullable=False)
    quantity = db.Column(db.Numeric(12, 3), nullable=False)  # signé : + entrée, - sortie
    unit_cost = db.Column(db.BigInteger)
    ref_type = db.Column(db.String(30))
    ref_id = db.Column(db.Integer)
    user_id = db.Column(db.ForeignKey("users.id"))
    note = db.Column(db.String(255))
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), nullable=False)


class Inventory(TimestampMixin, db.Model):
    __tablename__ = "inventories"

    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.ForeignKey("stores.id"), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="open")  # open | closed
    created_by_id = db.Column(db.ForeignKey("users.id"))
    closed_at = db.Column(db.DateTime(timezone=True))

    lines = db.relationship("InventoryLine", back_populates="inventory", cascade="all, delete-orphan")


class InventoryLine(db.Model):
    __tablename__ = "inventory_lines"

    id = db.Column(db.Integer, primary_key=True)
    inventory_id = db.Column(db.ForeignKey("inventories.id", ondelete="CASCADE"), nullable=False)
    product_id = db.Column(db.ForeignKey("products.id"), nullable=False)
    expected_qty = db.Column(db.Numeric(12, 3), nullable=False, default=0)
    counted_qty = db.Column(db.Numeric(12, 3))

    inventory = db.relationship("Inventory", back_populates="lines")
