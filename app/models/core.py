from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db
from app.models.base import TimestampMixin

role_permissions = db.Table(
    "role_permissions",
    db.Column("role_id", db.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    db.Column(
        "permission_id", db.ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True
    ),
)

user_stores = db.Table(
    "user_stores",
    db.Column("user_id", db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    db.Column("store_id", db.ForeignKey("stores.id", ondelete="CASCADE"), primary_key=True),
)


class Store(TimestampMixin, db.Model):
    __tablename__ = "stores"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(4), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(80), nullable=False)
    kind = db.Column(db.String(40), nullable=False, default="Supermarché")
    address = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    registers = db.relationship(
        "Register", back_populates="store", cascade="all, delete-orphan", order_by="Register.number"
    )

    @property
    def display_name(self):
        return f"{self.city} · {self.name}"

    def __repr__(self):
        return f"<Store {self.code}>"


class Register(TimestampMixin, db.Model):
    __tablename__ = "registers"
    __table_args__ = (db.UniqueConstraint("store_id", "number", name="uq_register_store_number"),)

    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.ForeignKey("stores.id", ondelete="CASCADE"), nullable=False)
    number = db.Column(db.Integer, nullable=False)
    label = db.Column(db.String(40), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    store = db.relationship("Store", back_populates="registers")


class Permission(db.Model):
    __tablename__ = "permissions"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(60), unique=True, nullable=False)
    module = db.Column(db.String(30), nullable=False)
    label = db.Column(db.String(120), nullable=False)


class Role(TimestampMixin, db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True, nullable=False)
    description = db.Column(db.String(255))

    permissions = db.relationship("Permission", secondary=role_permissions, lazy="selectin")


class User(UserMixin, TimestampMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(160), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.ForeignKey("roles.id"), nullable=False)
    all_stores = db.Column(db.Boolean, nullable=False, default=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    last_login_at = db.Column(db.DateTime(timezone=True))

    role = db.relationship("Role")
    stores = db.relationship("Store", secondary=user_stores)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_permission(self, code):
        return any(p.code == code for p in self.role.permissions)

    def can_access_store(self, store_id):
        return self.all_stores or any(s.id == store_id for s in self.stores)

    @property
    def initials(self):
        return "".join(w[0] for w in self.full_name.split()[:2]).upper()
