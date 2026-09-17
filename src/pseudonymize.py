import hashlib
import os
from dotenv import load_dotenv


load_dotenv()
DEFAULT_SALT = os.getenv("PSEUDONYMIZATION_SALT")


def pseudonymize_name(name, salt= DEFAULT_SALT):

    if name is None or (isinstance(name, float)):  # gère les NaN de pandas
        return None
    texte_a_hasher = f"{salt}{str(name).strip().lower()}"
    hash_object = hashlib.sha256(texte_a_hasher.encode("utf-8"))
    return hash_object.hexdigest()


def pseudonymize_column(series, salt):
    return series.apply(lambda x: pseudonymize_name(x, salt))


if __name__ == "__main__":
    print(pseudonymize_name("Claire Gute"))
    print(pseudonymize_name("Claire Gute"))
