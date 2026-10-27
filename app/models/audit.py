from app.extensions import db
from app.models.base import TimestampMixin


class AuditLog(TimestampMixin, db.Model):
    """Journal d'audit : qui a fait quoi, sur quelle entité, depuis quelle IP."""

    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey("users.id", ondelete="SET NULL"), index=True)
    action = db.Column(db.String(60), nullable=False, index=True)  # ex: sale.create
    entity = db.Column(db.String(60))  # ex: Sale, Product
    entity_id = db.Column(db.Integer)
    details = db.Column(db.JSON)
    ip_address = db.Column(db.String(45))

    user = db.relationship("User")
