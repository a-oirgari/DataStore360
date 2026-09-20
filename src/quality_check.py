from sqlalchemy import text
from sqlalchemy.engine import Engine


def run_quality_checks(engine):
    checks = {}

    with engine.connect() as conn:
        checks["nb_customers"] = conn.execute(text("SELECT COUNT(*) FROM core.customers")).scalar()
        checks["nb_products"] = conn.execute(text("SELECT COUNT(*) FROM core.products")).scalar()
        checks["nb_orders"] = conn.execute(text("SELECT COUNT(*) FROM core.orders")).scalar()


        nb_orders_sans_fk = conn.execute(text("""
            SELECT COUNT(*) FROM core.orders
            WHERE customerid IS NULL OR productid IS NULL
        """)).scalar()
        checks["nb_orders_sans_fk"] = nb_orders_sans_fk


        nb_noms_non_hashes = conn.execute(text("""
            SELECT COUNT(*) FROM core.customers
            WHERE LENGTH(customername) != 64
        """)).scalar()
        checks["nb_noms_non_hashes"] = nb_noms_non_hashes


        nb_orders_invalides = conn.execute(text("""
            SELECT COUNT(*) FROM core.orders
            WHERE discount > 1 OR quantity < 0
        """)).scalar()
        checks["nb_orders_invalides"] = nb_orders_invalides

    if checks["nb_orders_sans_fk"] > 0:
        raise ValueError(f"{checks['nb_orders_sans_fk']} commande(s) sans client/produit associé !")
    if checks["nb_noms_non_hashes"] > 0:
        raise ValueError(f"{checks['nb_noms_non_hashes']} nom(s) de client NON pseudonymisé(s) détecté(s) !")
    if checks["nb_orders_invalides"] > 0:
        raise ValueError(f"{checks['nb_orders_invalides']} commande(s) invalide(s) détectée(s) en base !")

    print("[quality_check] Tous les contrôles sont OK :", checks)
    return checks
