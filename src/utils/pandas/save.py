import os
import time
import pandas as pd

# pylint: disable-next=import-error
from utils.hints.property_result import PropertyResult


def to_csv(rows: list[PropertyResult]):
    """Saves the scraped rows as a csv with good format.

    Args:
        rows (list[PropertyResult]): scraped rows.
    """
    save_dir = "./output"
    filename = f"{save_dir}/m2-{time.time()}.csv"
    columns = [
        "building",
        "modality",
        "neighborhood",
        "city",
        "price (COP)",
        "area (m²)",
        "bathrooms",
    ]

    df = pd.DataFrame(rows)
    df[:] = df[:].astype(str)
    df[["price", "area", "bathrooms"]] = df[["price", "area", "bathrooms"]].apply(pd.to_numeric)
    df = df.convert_dtypes()
    df.columns = columns

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    df.to_csv(filename, index=False, sep="|", encoding="utf8")
    print(f"Saved results @ {os.path.abspath(filename)}")
