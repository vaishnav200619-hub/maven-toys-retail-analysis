from pathlib import Path
import pandas as pd

root = Path('C:/Users/gopak/maven-toys-retail-analysis/data/raw')
files = sorted(root.glob('*.csv'))
print('FILES:')
for p in files:
    print('-', p.name)

print('\n--- SUMMARY ---')
for p in files:
    df = pd.read_csv(p)
    print(f'\nFILE: {p.name}')
    print('shape:', df.shape)
    print('columns:', list(df.columns))
    print('dtypes:')
    print(df.dtypes.to_string())
    print('missing_values:')
    print(df.isna().sum().to_string())
    print('duplicate_rows:', int(df.duplicated().sum()))
    print('null_rows:', int(df.isna().any(axis=1).sum()))
    for c in df.columns:
        if pd.api.types.is_numeric_dtype(df[c]):
            s = pd.to_numeric(df[c], errors='coerce')
            print(f'NUMERIC {c}: min={s.min()}, max={s.max()}, mean={s.mean()}, median={s.median()}')
    print('sample_head:')
    print(df.head(3).to_string(index=False))
