import pandas as pd
from app.services.charts_service import build_current_value_timeseries, build_allocation_pie_data

# Mock DF mimicking what PortfolioService.get_user_portfolio_df returns
data = {
    'purchase_date': ['2023-01-01', '2023-06-01', '2023-01-01'],
    'current_value': [1000.0, 2000.0, 500.0],
    'quantity': [10, 20, 5],
    'purchase_price': [100.0, 100.0, 100.0],
    'bond_type': ['Skarbowe', 'Korporacyjne', 'Skarbowe']
}
df = pd.DataFrame(data)

print("\nTesting build_current_value_timeseries...")
ts = build_current_value_timeseries(df, freq='D')
print("Keys:", ts.keys())
print("Labels sample:", ts['labels'][:5])
print("Values sample:", ts['values'][:5])
print("Costs sample:", ts['costs'][:5])

print("\nTesting build_allocation_pie_data...")
alloc = build_allocation_pie_data(df, group_by_candidates=['bond_type'], value_column='current_value')
print("Allocation:", alloc)
