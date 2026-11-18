from backend.services.synthetic_data import generate_synthetic_dataset
from backend.services.dataset_builder import FEATURE_COLUMNS

df = generate_synthetic_dataset()

print("========== FEATURE STATISTICS ==========")
print(df[FEATURE_COLUMNS].describe().round(2))

print("\n========== NORMAL VS ANOMALY ==========")
print(
    df.groupby("label")[FEATURE_COLUMNS]
    .mean()
    .round(2)
)

print("\n========== MISSING VALUES ==========")
print(df.isnull().sum())

assert len(df) == 500
assert len(FEATURE_COLUMNS) == 6
assert df.isnull().sum().sum() == 0
assert (df["label"] == "normal").sum() == 450
assert (df["label"] == "anomaly").sum() == 50

print("\nAll synthetic dataset checks passed!")
