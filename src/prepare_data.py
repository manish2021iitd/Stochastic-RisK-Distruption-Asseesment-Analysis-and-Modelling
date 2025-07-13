import pandas as pd
import os
from pandas_profiling import ProfileReport

def prepare_data(input_csv_path, output_dir, version="v1"):
    # Load data
    df = pd.read_csv(input_csv_path, encoding='ISO-8859-1')

    # Drop columns with high/null values
    df.drop(columns=["Product Description", "Order Zipcode"], inplace=True)

    # Impute missing values
    df['Customer Lname'].fillna("Unknown", inplace=True)
    if df['Customer Zipcode'].isnull().any():
        mode_zip = df['Customer Zipcode'].mode()[0]
        df['Customer Zipcode'].fillna(mode_zip, inplace=True)

    # Convert dates
    df['order date (DateOrders)'] = pd.to_datetime(df['order date (DateOrders)'], errors='coerce')
    df['shipping date (DateOrders)'] = pd.to_datetime(df['shipping date (DateOrders)'], errors='coerce')

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Save as tidy Parquet
    parquet_path = os.path.join(output_dir, f"supplygraph_clean_{version}.parquet")
    df.to_parquet(parquet_path, index=False)

    # Generate profiling report
    report_path = os.path.join(output_dir, f"profile_report_{version}.html")
    profile = ProfileReport(df, title=f"Supply Chain Profiling Report ({version})", explorative=True)
    profile.to_file(report_path)

    print(f"Data saved to: {parquet_path}")
    print(f"Profiling report saved to: {report_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Clean and profile supply chain dataset")
    parser.add_argument("--input", required=True, help="DataCoSupplyChainDataset.csv")
    parser.add_argument("--output", required=True, help="/code")
    parser.add_argument("--version", default="v1", help="Version tag for output files")
    args = parser.parse_args()

    prepare_data(args.input, args.output, args.version)

