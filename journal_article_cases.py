##### Importing Libraries
from heat_pump_model import heat_pump
from libraries import * 

def call_heat_pump(filename, gas_price, electricity_price, carbon_price, high_T, low_T):
    hp = heat_pump()
    hp.cold_temperature_available = low_T
    hp.hot_temperature_desired = high_T
    hp.hot_temperature_minimum = hp.hot_temperature_desired-10
    hp.carnot_efficiency_factor = 0.45
    hp.carnot_efficiency_factor_flag = False

    hp.capital_cost_per_size = 590
    hp.fixed_o_and_m_per_size = 0.02*hp.capital_cost_per_size

    # Assuming a 20 hour operation
    operating_heat = 1.85
    hp.process_heat_requirement = ([0.0,0.0] + [operating_heat]*20 + [0.0, 0.0])*8760

    hp.lifetime_yrs = 10
    hp.gas_price_MMBTU = gas_price
    hp.utility_rate_kwh = electricity_price

    hp.run_all(filename)
    del hp

##### Setting up Iteration Arrays
# For this work there are a lot of parameters, so setting up arrays that can be 
# iterated over.
#array_heat_exchanger_efficiency = [2.5, 5.0, 7.5]
array_compressor_efficiency = [0.6, 0.65, 0.7, 0.75, 0.8]
array_carnot_factors = [0.4, 0.45, 0.5, 0.55]
array_capital_cost =[*range(300,900,50)]
array_lifetime_years = [10, 15, 20]
array_FOM_percent = [0.02, 0.03, 0.04]
array_VOM = [0.05, 0.10]
array_carbon_price = [*range(15, 125, 5)]

array_discount_rate = []
for i in [*range(4,21)]:
    array_discount_rate.append(i/100)

# Setting up temperature arrays
array_cold_stream = [*range(15, 55, 5)]
array_cold_stream.append(120)
array_hot_stream = [*range(70, 155, 5)]

##### Setting up electricity prices
flat_CA_electricity_price = [0.1312]*8760
flat_ID_electricity_price = [0.0560]*8760
flat_NY_electricity_price = [0.0602]*8760
flat_TX_electricity_price = [0.0540]*8760
flat_WA_electricity_price = [0.0592]*8760
flat_WI_electricity_price = [0.0797]*8760

array_electricity_prices = []
for i in [*range(1, 20)]:
    array_electricity_prices.append(i)

##### Default Values
default_electricity_prices = [0.02]*8760
default_gas_prices = [6.5]*8760
default_carbon_price = 0
default_waste_stream_T = 45
default_hot_stream_T = 85
filename = 'test_output'


call_heat_pump(filename, default_gas_prices, default_electricity_prices, default_carbon_price, default_hot_stream_T, default_waste_stream_T)

call_heat_pump('CA_flat', default_gas_prices, flat_CA_electricity_price, default_carbon_price, default_hot_stream_T, default_waste_stream_T)
call_heat_pump('ID_flat', default_gas_prices, flat_ID_electricity_price, default_carbon_price, default_hot_stream_T, default_waste_stream_T)
call_heat_pump('NY_flat', default_gas_prices, flat_NY_electricity_price, default_carbon_price, default_hot_stream_T, default_waste_stream_T)
call_heat_pump('TX_flat', default_gas_prices, flat_TX_electricity_price, default_carbon_price, default_hot_stream_T, default_waste_stream_T)
call_heat_pump('WA_flat', default_gas_prices, flat_WA_electricity_price, default_carbon_price, default_hot_stream_T, default_waste_stream_T)
call_heat_pump('WI_flat', default_gas_prices, flat_WI_electricity_price, default_carbon_price, default_hot_stream_T, default_waste_stream_T)

print('done')
# Setting up TOU rates
#tou_CA_electricty_price = []
#tou_CA_electricty_price.append([0.117336]*5*24)
#tou_CA_electricty_price.append([0.108]*2*24)
#print(tou_CA_electricty_price)
