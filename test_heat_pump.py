from heat_pump_model import heat_pump
from libraries import * 
import numpy as np
import pandas as pd
from utilities.unit_defs import Q_
from timeit import default_timer as timer

start = timer()
hp_test = heat_pump()

hp_test.construct_yaml_input_quantities('model_inputs.yml')

df = pd.DataFrame(np.array([4.5]*hp_test.n_hrs))

#hp_test.make_input_quantity("hot_mass_flowrate: {val: 95.0, unit: 'kg/s'}")
#hp_test.gas_price_MMBTU = Q_(np.array([4.5] * hp_test.n_hrs), 'USD / MMBtu')
hp_test.gas_price_MMBTU = Q_(df, 'USD / MMBtu')
hp_test.run_all_commercial_electric_utility_rates()


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
print('')

hp_test.run_all('test')
hp_test.carbon_price_per_ton = 20
hp_test.existing_gas = True
hp_test.run_all('test')
print(working_fluid['air'])
end = timer()
print(end - start)
print('Done')

print(hp_test.hourly_utility_rate)