import pandas as pd
import os

DATA_PATH = "data/raw/"

def load_all_data():
    """Load all 9 CSVs"""
    data = {}
    files = os.listdir(DATA_PATH)

    for file in files:
        if file.endswith('.csv'):
            name = file.replace('.csv', '')
            data[name] = pd.read_csv(os.path.join(DATA_PATH, file))
            print(f"\n{name}:")
            print(f"  Shape: {data[name].shape}")
            print(f"  Columns: {list(data[name].columns)}")

    return data

if __name__ == "__main__":
    data = load_all_data()
