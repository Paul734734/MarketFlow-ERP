from datetime import date, datetime, time
from zoneinfo import ZoneInfo

import click

from app.extensions import db
from app.models import (
    Account, Category, Employee, FinanceAccount, Permission, Product, PurchaseOrder,
    PurchaseOrderLine, Register, Role, Store, StockLevel, Supplier, User,
)

TZ = ZoneInfo("Africa/Douala")
DEV_PASSWORD = "Marketflow2026!"

MODULES = {
    "products": "Produits", "stocks": "Stocks", "purchases": "Achats", "pos": "Caisse",
    "sales": "Ventes", "accounting": "Comptabilité", "hr": "Ressources humaines",
    "admin": "Administration",
}
PERMISSIONS = [("dashboard.view", "Voir l'accueil")]
for _m, _label in MODULES.items():
    PERMISSIONS += [(f"{_m}.view", f"{_label} : consulter"), (f"{_m}.manage", f"{_label} : gérer")]
PERMISSIONS += [
    ("purchases.approve", "Achats : approuver"),
    ("stocks.adjust", "Stocks : ajuster / inventorier"),
    ("pos.discount", "Caisse : accorder une remise"),
    ("sales.refund", "Ventes : rembourser"),
    ("accounting.validate", "Comptabilité : valider les écritures"),
]

ROLE_PERMS = {
    "Direction": "*",
    "Gestionnaire de stock": ["dashboard.view", "products.view", "stocks.view", "stocks.manage", "stocks.adjust", "purchases.view"],
    "Caissier": ["dashboard.view", "products.view", "pos.view", "pos.manage", "sales.view"],
    "Responsable achats": ["dashboard.view", "products.view", "stocks.view", "purchases.view", "purchases.manage", "purchases.approve"],
    "Comptable": ["dashboard.view", "sales.view", "purchases.view", "accounting.view", "accounting.manage", "accounting.validate"],
    "RH": ["dashboard.view", "hr.view", "hr.manage"],
}

USERS = [
    ("Ariane Nguema", "ariane.nguema@marketflow.test", "Direction", True, []),
    ("Samuel Mbarga", "samuel.mbarga@marketflow.test", "Gestionnaire de stock", False, ["AK"]),
    ("Mireille Foko", "mireille.foko@marketflow.test", "Caissier", False, ["AK"]),
    ("Paul Tchoumi", "paul.tchoumi@marketflow.test", "Responsable achats", True, []),
]

# sku, code-barres, nom, catégorie, unité, prix TTC, seuil min, qté de réappro
PRODUCTS = [
    ("EP-001", "6190001000012", "Riz parfumé 5 kg", "Épicerie", "sac", 6500, 40, 120),
    ("EP-014", "6190001000142", "Huile végétale 1 L", "Épicerie", "bouteille", 1800, 60, 240),
    ("LA-006", "6190002000067", "Lait en poudre 400 g", "Laitiers", "boîte", 2600, 30, 120),
    ("EP-022", "6190001000227", "Sucre blanc 1 kg", "Épicerie", "sachet", 900, 50, 360),
    ("BO-003", "6190003000036", "Eau minérale 1,5 L", "Boissons", "bouteille", 400, 100, 480),
    ("EN-002", "6190005000025", "Savon de ménage", "Entretien", "pain", 550, 40, 200),
    ("EP-031", "6190001000319", "Farine de blé 1 kg", "Épicerie", "sachet", 750, 50, 100),
]
AKWA_STOCK = {"EP-001": 18, "EP-014": 42, "LA-006": 36, "EP-022": 84, "BO-003": 240, "EN-002": 55, "EP-031": 0}

ACCOUNTS = [
    ("311", "Marchandises", "asset"), ("411", "Clients", "asset"),
    ("521", "Banques", "asset"), ("571", "Caisse", "asset"),
    ("401", "Fournisseurs", "liability"), ("4431", "TVA facturée sur ventes", "liability"),
    ("4452", "TVA récupérable sur achats", "asset"),
    ("601", "Achats de marchandises", "expense"), ("661", "Rémunérations du personnel", "expense"),
    ("701", "Ventes de marchandises", "income"),
]


def seed_all():
    if Store.query.first():
        click.echo("La base contient déjà des données : rien à faire.")
        return

    stores = {}
    for code, name, city, kind, n_regs in [
        ("AK", "Akwa", "Douala", "Magasin principal", 5),
        ("BO", "Bonamoussadi", "Douala", "Supermarché", 4),
        ("BA", "Bastos", "Yaoundé", "Supermarché", 3),
    ]:
        s = Store(code=code, name=name, city=city, kind=kind)
        s.registers = [Register(number=i, label=f"Caisse {i:02d}") for i in range(1, n_regs + 1)]
        db.session.add(s)
        stores[code] = s

    perms = {c: Permission(code=c, module=c.split(".")[0], label=l) for c, l in PERMISSIONS}
    db.session.add_all(perms.values())
    roles = {}
    for name, codes in ROLE_PERMS.items():
        r = Role(name=name)
        r.permissions = list(perms.values()) if codes == "*" else [perms[c] for c in codes]
        db.session.add(r)
        roles[name] = r

    users = {}
    for full_name, email, role, all_stores, codes in USERS:
        u = User(email=email, full_name=full_name, role=roles[role], all_stores=all_stores)
        u.set_password(DEV_PASSWORD)
        u.stores = [stores[c] for c in codes]
        db.session.add(u)
        users[full_name] = u

    cats = {n: Category(name=n) for n in ("Épicerie", "Boissons", "Laitiers", "Frais", "Entretien")}
    db.session.add_all(cats.values())
    products = {}
    for sku, barcode, name, cat, unit, price, min_stock, reorder in PRODUCTS:
        p = Product(
            sku=sku, barcode=barcode, name=name, category=cats[cat], unit=unit,
            sale_price=price, cost_price=round(price * 0.77),
            min_stock=min_stock, reorder_qty=reorder,
        )
        db.session.add(p)
        products[sku] = p
    db.session.flush()

    for code, mult in (("AK", 1), ("BO", 2), ("BA", 3)):
        for sku, base in AKWA_STOCK.items():
            qty = base if code == "AK" else (base or 80) * mult
            db.session.add(StockLevel(store_id=stores[code].id, product_id=products[sku].id, quantity=qty))

    suppliers = {}
    for name, contact, phone, addr in [
        ("Centrale Littoral", "Pauline Essomba", "+237 6 90 12 34 56", "Zone industrielle de Bassa, Douala"),
        ("Agro Distribution Centre", None, None, "Yaoundé"),
        ("Boissons du Wouri", None, None, "Douala"),
    ]:
        suppliers[name] = Supplier(name=name, contact_name=contact, phone=phone, address=addr)
        db.session.add(suppliers[name])
    db.session.flush()

    order = PurchaseOrder(
        number="BC-2026-0842", supplier_id=suppliers["Centrale Littoral"].id,
        store_id=stores["AK"].id, status="confirmed",
        expected_at=datetime(2026, 10, 27, 15, 0, tzinfo=TZ),
        payment_terms="Virement à 30 jours",
        created_by_id=users["Paul Tchoumi"].id, responsible_id=users["Samuel Mbarga"].id,
        approved_by_id=users["Ariane Nguema"].id,
        approved_at=datetime(2026, 10, 26, 16, 20, tzinfo=TZ),
        confirmed_at=datetime(2026, 10, 27, 9, 15, tzinfo=TZ),
    )
    for sku, qty, cost in (("EP-001", 120, 5000), ("EP-014", 240, 1300), ("EP-022", 360, 835)):
        order.lines.append(PurchaseOrderLine(product_id=products[sku].id, quantity=qty, unit_cost=cost))
    order.total = sum(int(l.quantity) * l.unit_cost for l in order.lines)
    db.session.add(order)

    for matricule, name, job, code, uname in [
        ("RH-014", "Mireille Foko", "Caissière", "AK", "Mireille Foko"),
        ("RH-008", "Samuel Mbarga", "Stock", "AK", "Samuel Mbarga"),
        ("RH-031", "Yvan Njoya", "Caissier", "BO", None),
    ]:
        db.session.add(Employee(
            matricule=matricule, full_name=name, job_title=job, store_id=stores[code].id,
            user_id=users[uname].id if uname else None, hired_on=date(2024, 1, 15),
        ))

    db.session.add_all([
        FinanceAccount(name="Banque", kind="bank", opening_balance=18_200_000),
        FinanceAccount(name="Caisses magasins", kind="cash", opening_balance=4_380_000),
        FinanceAccount(name="Mobile Money", kind="mobile", opening_balance=2_100_000),
    ])
    db.session.add_all([Account(code=c, name=n, kind=k) for c, n, k in ACCOUNTS])

    db.session.commit()
    click.echo(f"Données de démo créées. Mot de passe de tous les comptes : {DEV_PASSWORD}")


def register_cli(app):
    @app.cli.command("seed")
    def seed():
        """Peuple la base avec des données de démonstration."""
        seed_all()
