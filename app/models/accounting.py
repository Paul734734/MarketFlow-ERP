from app.extensions import db
from app.models.base import TimestampMixin


class FinanceAccount(TimestampMixin, db.Model):
    """Compte de trésorerie : banque, caisses magasins, Mobile Money."""

    __tablename__ = "finance_accounts"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    kind = db.Column(db.String(10), nullable=False)  # bank | cash | mobile
    store_id = db.Column(db.ForeignKey("stores.id"))
    opening_balance = db.Column(db.BigInteger, nullable=False, default=0)


class Account(db.Model):
    """Plan comptable (SYSCOHADA)."""

    __tablename__ = "accounts"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(160), nullable=False)
    kind = db.Column(db.String(10), nullable=False)  # asset | liability | expense | income


class JournalEntry(TimestampMixin, db.Model):
    __tablename__ = "journal_entries"

    id = db.Column(db.Integer, primary_key=True)
    journal = db.Column(db.String(4), nullable=False)  # VT, AC, BQ, CA, OD
    entry_date = db.Column(db.Date, nullable=False)
    reference = db.Column(db.String(40))
    label = db.Column(db.String(255))
    store_id = db.Column(db.ForeignKey("stores.id"))
    status = db.Column(db.String(10), nullable=False, default="draft")  # draft | validated
    created_by_id = db.Column(db.ForeignKey("users.id"))

    lines = db.relationship("JournalLine", back_populates="entry", cascade="all, delete-orphan")


class JournalLine(db.Model):
    __tablename__ = "journal_lines"

    id = db.Column(db.Integer, primary_key=True)
    entry_id = db.Column(db.ForeignKey("journal_entries.id", ondelete="CASCADE"), nullable=False)
    account_id = db.Column(db.ForeignKey("accounts.id"), nullable=False)
    debit = db.Column(db.BigInteger, nullable=False, default=0)
    credit = db.Column(db.BigInteger, nullable=False, default=0)
    label = db.Column(db.String(255))

    entry = db.relationship("JournalEntry", back_populates="lines")
    account = db.relationship("Account")
