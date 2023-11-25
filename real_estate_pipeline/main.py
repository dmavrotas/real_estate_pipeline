import json
from io import StringIO

import pandas as pd
from pandas import DataFrame


def main():
    try:
        # Load the file
        df = load_dataset("resources/sample.json")

        # Clean the dataset by removing rows that have invalid values
        df = clean_dataset(df)

        # Clean the rows that have NaN values.
        df = df.dropna()

        # Normalize dataset to make sure that the values make sense
        df = normalize_dataset(df)

        # Apply the criteria of our ETL
        df = filter_dataset(df, ["apartment", "house"], 500.0, 15000.0)

        # Prepare to send the file to storage
        df = prepare_dataset_for_send(df)

        # Save to storage
        save_to_destination(df, "resources/sample_clean.csv")

        print(df)
        print("\nOperation succeeded!")
    except Exception as err:
        print(f"Operation failed with error: {err}")


def load_dataset(path: str) -> DataFrame:
    with open(path) as dataset_data:
        json_file = dataset_data.read()

    return pd.read_json(StringIO(json.loads(json_file)))


def clean_dataset(df: DataFrame) -> DataFrame:
    # Make sure that we only keep the valid rows that contain numeric values.
    df["raw_price"] = (
        df["raw_price"]
        .astype("str")
        .str.extract(r"(-{0,1}\d+\.\d+)", expand=False)
        .astype(float, errors="ignore")
    )
    df["living_area"] = (
        df["living_area"]
        .astype("str")
        .str.extract(r"(-{0,1}\d+\.\d+)", expand=False)
        .astype(float, errors="ignore")
    )
    # Make sure we only keep valid dates.
    df["scraping_date"] = pd.to_datetime(
        df["scraping_date"], format="%Y-%M-%d", errors="coerce"
    ).apply(lambda x: pd.Period(x, freq="d"))

    return df


def normalize_dataset(df: DataFrame) -> DataFrame:
    # The prices were very high, I think the dataset contains the prices in cents and not euros, so we need to adapt it.
    df["raw_price"] = df["raw_price"] / 100.0
    # To make sure that our criteria work, let's put this value to lowercase
    df["property_type"] = df["property_type"].apply(str.lower)

    return df


def filter_dataset(
    df: DataFrame, property_types: list[str], min_price: float, max_price: float
) -> DataFrame:
    return df[
        df["property_type"].isin(property_types)
        & (df["raw_price"] >= min_price)
        & (df["raw_price"] <= max_price)
    ]


def prepare_dataset_for_send(df: DataFrame) -> DataFrame:
    df = df.rename(columns={"raw_price": "price"})
    return df.drop(columns=["municipality"])


def save_to_destination(df: DataFrame, path: str):
    df.to_csv(path, index=False)


if __name__ == "__main__":
    main()
