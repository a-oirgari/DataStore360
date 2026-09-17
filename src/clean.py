import pandas as pd
import numpy as np


def convert_types(df):
    df = df.copy()
    df["order_date"] = pd.to_datetime(df["order_date"], format="%m/%d/%Y", errors="coerce")
    df["ship_date"] = pd.to_datetime(df["ship_date"], format="%m/%d/%Y", errors="coerce")

    for col in ["sales", "discount", "profit"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in ["quantity", "row_id", "postal_code"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

    return df


def remove_duplicates(df):
    before = len(df)
    df = df.drop_duplicates(subset=["row_id"], keep="first")
    removed = before - len(df)
    print(f"[clean] {removed} doublon(s) supprimé(s) (sur row_id)")
    return df


def handle_missing_values(df):
    before = len(df)
    df = df.dropna(subset=["row_id", "customer_id", "product_id", "order_id", "order_date"]).copy()
    removed = before - len(df)
    print(f"[clean] {removed} ligne(s) supprimée(s) pour clés/dates manquantes obligatoires")

    df["postal_code"] = df["postal_code"].astype("object")
    df["postal_code"] = df["postal_code"].fillna("UNKNOWN")

    return df


def handle_invalid_values(df):
    before = len(df)

    masque_discount_invalide = df["discount"] > 1
    masque_quantity_invalide = df["quantity"] < 0
    masque_dates_invalides = df["ship_date"] < df["order_date"]

    masque_invalide = masque_discount_invalide | masque_quantity_invalide | masque_dates_invalides
    nb_invalides = masque_invalide.sum()

    df = df[~masque_invalide].copy()

    print(f"[clean] {nb_invalides} ligne(s) invalide(s) supprimée(s) "
          f"(discount>100% / quantity<0 / ship_date<order_date)")
    print(f"[clean] total lignes supprimées à cette étape : {before - len(df)}")

    return df


def add_derived_variables(df):
    df = df.copy()

    denominateur = df["quantity"] * (1 - df["discount"])
    df["prix_unitaire"] = np.where((df["sales"].notna()) & (denominateur > 0),
        df["sales"] / denominateur, np.nan)

    prix_unitaire_par_produit = (df.groupby("product_id")["prix_unitaire"].transform("median"))
    df["prix_unitaire"] = df["prix_unitaire"].fillna(prix_unitaire_par_produit)

    sales_calcule = (df["prix_unitaire"] * df["quantity"] * (1 - df["discount"]))
    df["sales"] = df["sales"].fillna(sales_calcule)

    df["deliverytime"] = (df["ship_date"] - df["order_date"]).dt.days

    df["profit_margin"] = ((df["profit"] / df["sales"])
    .where(df["sales"].notna() & (df["sales"] != 0),
        0.0))
    return df


def clean_pipeline(df_raw):
    df = convert_types(df_raw)
    df = remove_duplicates(df)
    df = handle_missing_values(df)
    df = handle_invalid_values(df)
    df = add_derived_variables(df)
    return df


if __name__ == "__main__":
    from extract import read_source_csv, rename_columns_for_staging

    df_raw = read_source_csv("data/raw/Sample - Superstore.csv")
    df_raw = rename_columns_for_staging(df_raw)
    df_clean = clean_pipeline(df_raw)
    print(df_clean.info())
