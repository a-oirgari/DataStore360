import pandas as pd
from sqlalchemy.engine import Engine

COLUMN_MAPPING = {
    "Row ID": "row_id",
    "Order ID": "order_id",
    "Order Date": "order_date",
    "Ship Date": "ship_date",
    "Ship Mode": "ship_mode",
    "Customer ID": "customer_id",
    "Customer Name": "customer_name",
    "Segment": "segment",
    "Country": "country",
    "City": "city",
    "State": "state",
    "Postal Code": "postal_code",
    "Region": "region",
    "Product ID": "product_id",
    "Category": "category",
    "Sub-Category": "sub_category",
    "Product Name": "product_name",
    "Sales": "sales",
    "Quantity": "quantity",
    "Discount": "discount",
    "Profit": "profit",
}

def read_source_csv(csv_path):
    df = pd.read_csv(csv_path, encoding="latin-1", dtype=str)
    return df


def rename_columns_for_staging(df):
    return df.rename(columns=COLUMN_MAPPING)



def load_to_staging(df, engine, table_name = "superstore_raw"):
    df.to_sql(name=table_name, con=engine,
        schema="staging",
        if_exists="replace",
        index=False)
    return len(df)


def extract_and_load(csv_path , engine):
    df_raw = read_source_csv(csv_path)
    df_renamed = rename_columns_for_staging(df_raw)
    nb_lignes = load_to_staging(df_renamed, engine)
    print(f"[extract] {nb_lignes} lignes chargées dans staging.superstore_raw")
    return df_renamed

if __name__ == "__main__":
    from db import get_engine

    engine = get_engine()
    extract_and_load("data/raw/Sample - Superstore.csv", engine)


