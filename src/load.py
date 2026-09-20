import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine

from pseudonymize import pseudonymize_column, DEFAULT_SALT


def build_customers_df(df):
    cols = ["customer_id", "customer_name", "segment", "country",
            "city", "state", "postal_code", "region"]
    customers = df[cols].drop_duplicates(subset=["customer_id"]).copy()


    customers["customer_name"] = pseudonymize_column(customers["customer_name"], DEFAULT_SALT)

    customers = customers.rename(columns={"customer_id": "customerid",
        "customer_name": "customername"})
    return customers



def build_products_df(df):
    cols = ["product_id", "category", "sub_category", "product_name"]
    products = df[cols].drop_duplicates(subset=["product_id"]).copy()
    products = products.rename(columns={"product_id": "productid",
        "sub_category": "subcategory",})
    return products


def build_orders_df(df):
    cols = ["row_id", "order_id", "customer_id", "product_id", "order_date",
            "ship_date", "ship_mode", "sales", "quantity", "discount",
            "profit", "deliverytime", "profit_margin"]
    orders = df[cols].copy()
    orders = orders.rename(columns={
        "row_id": "rowid",
        "order_id": "orderid",
        "customer_id": "customerid",
        "product_id": "productid",
        "ship_mode": "shipmode",
        "order_date": "orderdate",
        "ship_date": "shipdate",
    })
    return orders


def upsert_dataframe(df, table, pk_column, engine, staging_table = "_tmp_upsert"):

    schema = "core"
    columns = list(df.columns)

    with engine.begin() as conn:
        df.to_sql(staging_table, con=conn, schema=schema, if_exists="replace", index=False)

        columns_str = ", ".join(columns)
        update_str = ", ".join(f"{col} = EXCLUDED.{col}" for col in columns if col != pk_column)

        upsert_query = text(f"""
            INSERT INTO {schema}.{table} ({columns_str})
            SELECT {columns_str} FROM {schema}.{staging_table}
            ON CONFLICT ({pk_column})
            DO UPDATE SET {update_str};
        """)
        conn.execute(upsert_query)

        conn.execute(text(f"DROP TABLE IF EXISTS {schema}.{staging_table};"))

    print(f"[load] {len(df)} ligne(s) upsertées dans {schema}.{table}")



def load_pipeline(df_clean, engine):

    customers = build_customers_df(df_clean)
    products = build_products_df(df_clean)
    orders = build_orders_df(df_clean)

    upsert_dataframe(customers, table="customers", pk_column="customerid", engine=engine)
    upsert_dataframe(products, table="products", pk_column="productid", engine=engine)
    upsert_dataframe(orders, table="orders", pk_column="rowid", engine=engine)

    return {"nb_customers": len(customers),
        "nb_products": len(products),
        "nb_orders": len(orders),}
