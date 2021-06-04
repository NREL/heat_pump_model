##### Importing Libraries
from heat_pump_model import heat_pump
from libraries import * 
import pandas as pd

def initialize_dict():
    heat_pump_dict = {
        'print_results':False,
        'write_output_file':True,
        'filename': 'base',
        'cold_temperature_available': 45,
        'hot_temperature_desired': 85,
        'hot_temperature_minimum': 80,
        'carnot_efficiency_factor': 0.45,
        'carnot_efficiency_factor_flag': True,
        'capital_cost_per_size': 600,
        'fixed_o_and_m_percent': 2,
        'variable_o_and_m_per_mmbtu' : 0.05,
        'process_heat' : 1.85,
        'process_hours': 20,
        'lifetime_yrs': 20,
        'gas_price': [6.5]*8760,
        'utility_rate_kwh': [0.02]*8760,
        'utility_rate_kw': 10,
        'carbon_price_per_ton': 0.0,
        'kwh_CAGR': -0.0046,
        'gas_CAGR': 0.012782
    }
    return heat_pump_dict


def call_heat_pump(heat_pump_dict):
    # Pulling Data From the Dict
    hp = heat_pump()

    # IO 
    hp.print_results = heat_pump_dict['print_results']
    hp.write_output_file = heat_pump_dict['write_output_file']

    # Temperature Data
    hp.cold_temperature_available = heat_pump_dict['cold_temperature_available']
    hp.hot_temperature_desired = heat_pump_dict['hot_temperature_desired']
    hp.hot_temperature_minimum = heat_pump_dict['hot_temperature_minimum']
    hp.carnot_efficiency_factor = heat_pump_dict['carnot_efficiency_factor']
    hp.carnot_efficiency_factor_flag = heat_pump_dict['carnot_efficiency_factor_flag']

    # Capital Cost
    hp.capital_cost_per_size = heat_pump_dict['capital_cost_per_size']
    hp.fixed_o_and_m_per_size = heat_pump_dict['fixed_o_and_m_percent']*heat_pump_dict['capital_cost_per_size']/100
    hp.variable_o_and_m_per_mmbtu = heat_pump_dict['variable_o_and_m_per_mmbtu']

    # Heat Requirements
    operating_heat = heat_pump_dict['process_heat']
    hp.process_heat_requirement = ([0.0,0.0] + [operating_heat]*20 + [0.0, 0.0])*8760

    # Economics
    hp.lifetime_yrs = heat_pump_dict['lifetime_yrs']
    hp.gas_price_MMBTU = heat_pump_dict['gas_price']
    hp.utility_rate_kwh = heat_pump_dict['utility_rate_kwh']
    hp.utility_rate_kw = heat_pump_dict['utility_rate_kw']
    hp.carbon_price_per_ton = heat_pump_dict['carbon_price_per_ton']
    hp.kwh_CAGR = heat_pump_dict['kwh_CAGR']
    hp.gas_CAGR = heat_pump_dict['gas_CAGR']

    # Some Defaults for this Heat Load
    hp.cold_mass_flow = [100]*8760

    # Running the model
    hp.run_all(heat_pump_dict['filename'])

    return hp
    del hp

##### Setting up Iteration Arrays
# For this work there are a lot of parameters, so setting up arrays that can be 
# iterated over.
#array_heat_exchanger_efficiency = [2.5, 5.0, 7.5]
#array_carnot_factors = [0.4, 0.45, 0.5, 0.55]
array_compressor_efficiency = [0.6, 0.65, 0.7, 0.75, 0.8]

array_capital_cost =[*range(300,950,50)]
array_lifetime_years = [10, 15, 20]
array_FOM_percent = [2, 3, 4, 5, 6, 7, 8, 9, 10]
array_VOM = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10]
array_carbon_price = [*range(15, 125, 5)]

#array_discount_rate = []
#for i in [*range(4,21)]:
#    array_discount_rate.append(i/100)

# Setting up temperature arrays
#array_cold_stream = [*range(15, 55, 5)]
#array_cold_stream.append(120)
#array_hot_stream = [*range(70, 155, 5)]

##### Setting up electricity and gas prices per state
cases = ['CA', 'ID', 'NY', 'TX', 'WA', 'WI', 'WA_Grant_County', 'WI_WE_Energies']
state_kwh_prices = {
    'CA': 0.1312,
    'ID': 0.0560,
    'NY': 0.0602,
    'TX': 0.0540,
    'WA': 0.0592,
    'WI': 0.0797,
    'WA_Grant_County': 0.01857,
    'WI_WE_Energies': 0.05589
}
state_kw_prices = {
    'CA': 15.0,
    'ID': 15.0,
    'NY': 15.0,
    'TX': 15.0,
    'WA': 15.0,
    'WI': 15.0,
    'WA_Grant_County': 17.73,
    'WI_WE_Energies': 4.96
}
state_mmbtu_prices = {
    'CA': 7.62,
    'ID': 3.61,
    'NY': 7.29,
    'TX': 2.86,
    'WA': 6.94,
    'WI': 4.83,
    'WA_Grant_County': 6.94,
    'WI_WE_Energies': 4.83 
}

# Base Case
heat_pump_dict = initialize_dict()
call_heat_pump(heat_pump_dict)

# Base Case with Refrigerant
heat_pump_dict['filename'] = 'base_refrigerant'
heat_pump_dict['carnot_efficiency_factor_flag'] = False
call_heat_pump(heat_pump_dict)

# Capital Cost
for i in array_capital_cost:
    heat_pump_dict = initialize_dict()
    heat_pump_dict['filename'] = 'capital_cost_'+str(i)
    print('case: ',  heat_pump_dict['filename'])
    heat_pump_dict['capital_cost_per_size'] = float(i)
    call_heat_pump(heat_pump_dict)

# Lifetime Years
for i in array_lifetime_years:
    heat_pump_dict = initialize_dict()
    heat_pump_dict['filename'] = 'lifetime_years_'+str(i)
    print('case: ',  heat_pump_dict['filename'])
    heat_pump_dict['lifetime_yrs'] = float(i)
    call_heat_pump(heat_pump_dict)

# FOM costs
for i in array_FOM_percent:
    heat_pump_dict = initialize_dict()
    heat_pump_dict['filename'] = 'FOM_pct_'+str(i)
    print('case: ',  heat_pump_dict['filename'])
    heat_pump_dict['fixed_o_and_m_percent'] = float(i)
    call_heat_pump(heat_pump_dict)

# VOM Costs
for i in array_VOM:
    heat_pump_dict = initialize_dict()
    heat_pump_dict['filename'] = 'VOM_pct_'+str(i)
    print('case: ',  heat_pump_dict['filename'])
    heat_pump_dict['variable_o_and_m_per_mmbtu'] = i
    call_heat_pump(heat_pump_dict)

# Carbon Price
for i in array_carbon_price:
    heat_pump_dict = initialize_dict()
    heat_pump_dict['filename'] = 'carbon_price_'+str(i)
    print('case: ',  heat_pump_dict['filename'])
    heat_pump_dict['carbon_price_per_ton'] = float(i)
    call_heat_pump(heat_pump_dict)

# Beginning Case Studies
for i in cases:
    heat_pump_dict = initialize_dict()
    heat_pump_dict['filename'] = i
    print('case: ',  heat_pump_dict['filename'])
    heat_pump_dict['utility_rate_kwh'] = [state_kwh_prices[i]]*8760
    heat_pump_dict['utility_rate_kw'] = state_kw_prices[i]
    heat_pump_dict['gas_price'] = [state_mmbtu_prices[i]]*8760
    call_heat_pump(heat_pump_dict)

## For the Break-even cases we will not be making an output file but will be filling in a Pandas DataFrame
array_electricity_price = []
for i in range(10, 210):array_electricity_price.append(float(i/1000))
array_gas_price = []
for i in range(10,101):array_gas_price.append(float(i/10))
columns = ['Capital Cost', 'Gas_Price', 'Electricity_Price', 'HP_LCOH', 'Gas_LCOH', 'NPV', 'IRR', 'PBP']
array_capital_cost = [300, 600, 900]
df_break_even = pd.DataFrame(0.0, index = range(len(array_capital_cost)*len(array_electricity_price)*len(array_gas_price)), columns = columns) 

# Building the dataframe
i = 0
for capital_cost in array_capital_cost:
    for electricity_price in array_electricity_price:
        for gas_price in array_gas_price:
            df_break_even.loc[i,'Capital Cost'] = capital_cost
            df_break_even.loc[i,'Electricity_Price'] = electricity_price
            df_break_even.loc[i,'Gas_Price'] = gas_price
            i += 1

# Calling the heat pump model
heat_pump_dict = initialize_dict()
heat_pump_dict['filename'] = 'break_even_temp'
heat_pump_dict['write_output_file'] = False
for i in df_break_even.index:
    heat_pump_dict['capital_cost'] = df_break_even.loc[i,'Capital Cost']
    heat_pump_dict['utility_rate_kwh'] = [df_break_even.loc[i,'Electricity_Price']]*8760
    heat_pump_dict['gas_price'] = [df_break_even.loc[i,'Gas_Price']]*8760

    print('case: Capital Cost: ', heat_pump_dict['capital_cost'], ' kWh Cost: ', df_break_even.loc[i,'Electricity_Price'], ' Gas Cost: ', df_break_even.loc[i,'Gas_Price'])
    hp_result = call_heat_pump(heat_pump_dict)
    df_break_even.loc[i, 'HP_LCOH'] = hp_result.LCOH
    df_break_even.loc[i, 'Gas_LCOH'] = hp_result.gas_LCOH
    df_break_even.loc[i, 'NPV'] = hp_result.net_present_value
    df_break_even.loc[i, 'IRR'] = hp_result.internal_rate_of_return
    df_break_even.loc[i, 'PBP'] = hp_result.payback_period

print(df_break_even)
df_break_even.to_excel('output/break_even.xlsx')

print('done')
