from heat_pump_model import heat_pump
from libraries import * 
import numpy as np
from utilities.unit_defs import Q_
from uncertainties import ufloat as uf
from timeit import default_timer as timer

import tkinter as tk
from tkinter import ttk

# User interface work
root = tk.Tk()
frm = ttk.Frame(root, padding=10)
frm.grid()
ttk.Label(frm, text="Thermal Inputs").grid(column=0, row=0)
selected_deg_unit = tk.StringVar()
deg_cb = ttk.Combobox(root, textvariable=selected_deg_unit)

deg_cb['values'] = ['degC', 'degF', 'degK']
deg_cb['state'] = 'readonly'
deg_cb.grid(column=1, row=0)
ttk.Button(frm, text="Quit", command=root.destroy).grid(column=2, row=0)

the_T_units = selected_deg_unit.get()
root.mainloop()

print(str(the_T_units))

start = timer()
hp_test = heat_pump()
hp_test.hot_temperature_desired = Q_(np.array([90]*8760), 'degC')
hp_test.hot_temperature_minimum = Q_(np.array([80]*8760), 'degC')
# hp_test.process_heat_requirement = Q_(np.array([1]*8760), 'MW')
hp_test.hot_mass_flowrate = Q_(np.array([uf(99,0.5)]*8760), 'kg/s')
hp_test.cold_temperature_available = Q_(np.array([60]*8760), 'degC')
hp_test.gas_price_MMBTU = Q_(np.array([4.5] * 8760), 'USD / MMBtu')
hp_test.carnot_efficiency_factor = Q_('0.50')
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
end = timer()
print(end - start)
print('Done')