import pandas as pd
import numpy as np

supply_data_path = 'inputs/supply_data.xlsx'
xlsx = pd.ExcelFile(supply_data_path)
order_data = pd.read_excel(xlsx, sheet_name='企业的订货量（m³）')
supply_data = pd.read_excel(xlsx, sheet_name='供应商的供货量（m³）')

order_data_id = order_data[['供应商ID']].copy()
supply_data_id = supply_data[['供应商ID']].copy()

# TODO: The average of supplication per week
supply_avg_result = supply_data.iloc[0:,2:].sum(axis=1) / 240

# TODO: The stability of supply
supply_weeks = (supply_data.iloc[0:, 2:] > 0).sum(axis=1)
supply_stability = supply_weeks /240

# TODO: The average of supply rate
avg_supply_rate = (1 - ((order_data.iloc[0:, 2:] - supply_data.iloc[0:, 2:]) / order_data.iloc[:, 2:])).clip(lower=0, upper=1).mean(axis=1)

# TODO: The total supply rate
total_demand = order_data.iloc[0:, 2:].sum(axis=1)
total_supply = supply_data.iloc[0:, 2:].sum(axis=1)
total_supply_rate = 1- (total_demand - total_supply) / total_demand

# TODO: The max supply
max_supply = supply_data.iloc[0:, 2:].max(axis=1)

# TODO: The variance of supply data
variance_supply = supply_data.iloc[0:, 2:].var(axis=1)
inverse_variance_supply = 1 / variance_supply

# TODO: The total demand of company
total_demand = order_data.iloc[0:, 2:].sum(axis=1)

# TODO: The demand rate of company
demand_weeks = (order_data.iloc[0:, 2:] > 0).sum(axis=1)
demand_rate = demand_weeks / 240

results = order_data_id.copy()
results['平均供应量'] = supply_avg_result
results['稳定性'] = supply_stability
results['平均应供率'] = avg_supply_rate
results['总体应供率'] = total_supply_rate
results['最大供应量'] = max_supply
results['供应量方差'] = inverse_variance_supply
results['企业总需求量'] = total_demand
results['企业需求率'] = demand_rate

results.to_excel('outputs/供应商可靠度与信任度指标.xlsx', index=False)

def cal_normalize(column):
    return (column - column.min()) / (column.max() - column.min())

results_normalized = results.copy()
numerical_cols = results.select_dtypes(include=['number']).columns
results_normalized[numerical_cols] = results_normalized[numerical_cols].apply(cal_normalize)

results_normalized.to_excel('outputs/供应商可靠度与信任度指标_标准化.xlsx', index=False)

positive_ideal = results_normalized[numerical_cols].max(axis=0)
negative_ideal = results_normalized[numerical_cols].min(axis=0)

pos_distance = np.sqrt(np.sum((results_normalized[numerical_cols] - positive_ideal)**2, axis=1))
neg_distance = np.sqrt(np.sum((results_normalized[numerical_cols] - negative_ideal)**2, axis=1))

closeness = neg_distance / (pos_distance + neg_distance)

results_normalized['接近度'] = closeness

results_normalized.to_excel('outputs/closeness.xlsx', index=False)

sorted_closeness = results_normalized[['供应商ID', '接近度']].sort_values(by='接近度', ascending=False)

sorted_closeness.to_excel('outputs/closeness_sorted.xlsx', index=False)