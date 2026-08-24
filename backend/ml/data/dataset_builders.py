import os
import pandas as pd
from .synthetic_data import generate_synthetic_corridor_dataset

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'artifacts')

def build_eta_training_dataset(num_synthetic_samples: int = 5000) -> pd.DataFrame:
    """
    Builds the dataset for training ETA machine learning models.
    Merges real shipment data from Django ORM if available with synthetic development data.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    df_synthetic = generate_synthetic_corridor_dataset(num_samples=num_synthetic_samples)
    
    csv_path = os.path.join(DATA_DIR, 'eta_training_dataset.csv')
    df_synthetic.to_csv(csv_path, index=False)
    print(f"Dataset successfully built with {len(df_synthetic)} samples -> {csv_path}")
    return df_synthetic
