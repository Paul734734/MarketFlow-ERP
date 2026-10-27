from app.extensions import db
from app.models.base import TimestampMixin


class Employee(TimestampMixin, db.Model):
    __tablename__ = "employees"

    id = db.Column(db.Integer, primary_key=True)
    matricule = db.Column(db.String(12), unique=True, nullable=False)  # RH-014
    full_name = db.Column(db.String(120), nullable=False)
    job_title = db.Column(db.String(80), nullable=False)
    department = db.Column(db.String(60))
    store_id = db.Column(db.ForeignKey("stores.id"), nullable=False)
    user_id = db.Column(db.ForeignKey("users.id"), unique=True)
    phone = db.Column(db.String(30))
    hired_on = db.Column(db.Date)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    store = db.relationship("Store")


class Shift(db.Model):
    __tablename__ = "shifts"
    __table_args__ = (db.UniqueConstraint("employee_id", "shift_date", name="uq_shift_employee_day"),)

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    shift_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)


class Attendance(db.Model):
    __tablename__ = "attendances"
    __table_args__ = (db.UniqueConstraint("employee_id", "work_date", name="uq_attendance_employee_day"),)

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    work_date = db.Column(db.Date, nullable=False)
    clock_in = db.Column(db.Time)
    clock_out = db.Column(db.Time)
    status = db.Column(db.String(20), nullable=False, default="present")  # present | late | absent | leave


class LeaveRequest(TimestampMixin, db.Model):
    __tablename__ = "leave_requests"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    kind = db.Column(db.String(30), nullable=False, default="congé")
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(10), nullable=False, default="pending")  # pending | approved | rejected
