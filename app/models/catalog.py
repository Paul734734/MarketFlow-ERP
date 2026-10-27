from app.extensions import db
from app.models.base import TimestampMixin


class Category(TimestampMixin, db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    parent_id = db.Column(db.ForeignKey("categories.id"))


class Product(TimestampMixin, db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(20), unique=True, nullable=False)
    barcode = db.Column(db.String(20), unique=True)
    name = db.Column(db.String(160), nullable=False, index=True)
    category_id = db.Column(db.ForeignKey("categories.id"), nullable=False)
    unit = db.Column(db.String(20), nullable=False, default="unité")
    sale_price = db.Column(db.BigInteger, nullable=False, default=0)  # FCFA TTC
    cost_price = db.Column(db.BigInteger, nullable=False, default=0)  # FCFA
    vat_rate = db.Column(db.Numeric(5, 2), nullable=False, default=19.25)
    min_stock = db.Column(db.Numeric(12, 3), nullable=False, default=0)
    reorder_qty = db.Column(db.Numeric(12, 3), nullable=False, default=0)
    track_lots = db.Column(db.Boolean, nullable=False, default=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    archived_at = db.Column(db.DateTime(timezone=True))

    category = db.relationship("Category")

    @property
    def margin_pct(self):
        if not self.sale_price:
            return 0
        return round((self.sale_price - self.cost_price) / self.sale_price * 100, 1)


class StorePrice(TimestampMixin, db.Model):
    """Prix spécifique à un magasin (écrase le prix catalogue)."""

    __tablename__ = "store_prices"
    __table_args__ = (db.UniqueConstraint("store_id", "product_id", name="uq_price_store_product"),)

    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.ForeignKey("stores.id", ondelete="CASCADE"), nullable=False)
    product_id = db.Column(db.ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    price = db.Column(db.BigInteger, nullable=False)
