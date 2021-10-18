from heat_pump_model import heat_pump
from libraries import * 
import numpy as np

hp_test = heat_pump()
hp_test.hot_temperature_desired = np.array([90]*8760)
hp_test.hot_temperature_minimum = np.array([80]*8760)
hp_test.cold_temperature_available = np.array([60]*8760)
hp_test.gas_price_MMBTU = np.array([4.5] * 8760) 
hp_test.carnot_efficiency_factor = 0.50
hp_test.carnot_efficiency_factor_flag = True

#hp_test.compressor_efficiency = 0.65
print('')
print('Case 1 Carnot Flag')
hp_test.run_all('Case_1')

print('')
print('Case 2 Refrigerant Search')
hp_test.carnot_efficiency_factor_flag = False
hp_test.run_all('Case_2')

print('')
print('Case 3 Refrigerant Specified')
hp_test.refrigerant_flag = True
hp_test.refrigerant = 'R245ca'
hp_test.run_all('Case_3')

#hp_test.carnot_efficiency_factor = 0.4
#hp_test.calculate_COP()
#print(hp_test.actual_COP)
'''
print('')
hp_test.calculate_COP()
print('')
hp_test.calculate_energy_and_mass_flow()
print('')
hp_test.calculate_heat_pump_costs()
print('')
hp_test.calculate_natural_gas_comparison()
print('')
hp_test.write_output('test')
print('')'''

#hp_test.run_all('test')
#hp_test.carbon_price_per_ton = 20
#hp_test.existing_gas = True
#hp_test.run_all('test')
#print(working_fluid['air'])

print('Done')