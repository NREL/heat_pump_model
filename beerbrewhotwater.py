from heat_pump_model import heat_pump
from libraries import * 
import numpy as np
from CoolProp.CoolProp import PropsSI
from utilities.unit_defs import Q_


hp_steam_gen = heat_pump()
hp_steam_gen.hot_temperature_desired = Q_(np.array([115]*8760), 'degC')
hp_steam_gen.hot_temperature_minimum = Q_(np.array([70]*8760), 'degC')
hp_steam_gen.hot_refrigerant = 'Water'
rho_sg = Q_(PropsSI('D', 'T', hp_steam_gen.hot_temperature_minimum.to('degK').m, 'P|liquid', hp_steam_gen.hot_pressure.to('Pa').m, hp_steam_gen.hot_refrigerant), 'kg/m^3')
hp_steam_gen.hot_mass_flowrate = Q_(np.append([1240000/6264] * 6264, [0] * (2496)), 'gal/hr')*rho_sg
hp_steam_gen.cold_temperature_available = Q_(np.array([70]*8760), 'degC')
hp_steam_gen.utility_rate_kwh = Q_(np.array([0.065] * 8760), 'USD / kWh') #$/kWh over an 8760 timeframe
hp_steam_gen.utility_rate_kw = Q_('0 USD / kW')
hp_steam_gen.gas_price_MMBTU = Q_(np.array([6.5] * 8760), 'USD / MMBtu')

hp_water_ht = heat_pump()
hp_water_ht.hot_temperature_desired = Q_(np.array([95]*8760), 'degC')
hp_water_ht.hot_temperature_minimum = Q_(np.array([50]*8760), 'degC')
hp_water_ht.hot_refrigerant = 'Water'
rho_wh = Q_(PropsSI('D', 'T', hp_water_ht.hot_temperature_minimum.to('degK').m, 'P|liquid', hp_water_ht.hot_pressure.to('Pa').m, hp_water_ht.hot_refrigerant), 'kg/m^3')
hp_water_ht.hot_mass_flowrate = Q_(np.append([1700000/6264] * 6264, [0] * (2496)), 'gal/hr')*rho_wh
hp_water_ht.cold_temperature_available = Q_(np.array([40]*8760), 'degC')
hp_water_ht.utility_rate_kwh = Q_(np.array([0.065] * 8760), 'USD / kWh') #$/kWh over an 8760 timeframe
hp_water_ht.utility_rate_kw = Q_('0 USD / kW')
hp_water_ht.gas_price_MMBTU = Q_(np.array([6.5] * 8760), 'USD / MMBtu')

print('Steam Generation Case')
hp_steam_gen.calculate_COP()
print('')
hp_steam_gen.calculate_energy_and_mass_flow()
print('')
hp_steam_gen.calculate_heat_pump_costs()
print('')
hp_steam_gen.calculate_natural_gas_comparison()
print('')

print('Water Heating Case')
hp_water_ht.calculate_COP()
print('')
hp_water_ht.calculate_energy_and_mass_flow()
print('')
hp_water_ht.calculate_heat_pump_costs()
print('')
hp_water_ht.calculate_natural_gas_comparison()
print('')

print('Done')