import pytest

from app import create_app
from app.extensions import db
from app.models import Product, Category, Role, Store, User


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


def test_user_password_and_store_access(app):
    store = Store(code="AK", name="Akwa", city="Douala")
    role = Role(name="Caissier")
    user = User(email="a@test.cm", full_name="Ariane Nguema", role=role, stores=[store])
    user.set_password("secret")
    db.session.add_all([store, role, user])
    db.session.commit()

    assert user.check_password("secret")
    assert not user.check_password("autre")
    assert user.can_access_store(store.id)
    assert user.initials == "AN"
    assert store.display_name == "Douala · Akwa"


def test_product_margin(app):
    cat = Category(name="Épicerie")
    p = Product(sku="EP-001", name="Riz", category=cat, sale_price=1000, cost_price=770)
    db.session.add(p)
    db.session.commit()
    assert p.margin_pct == 23.0
