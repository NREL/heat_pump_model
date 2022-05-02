import numpy as np
from CoolProp.CoolProp import PropsSI 
from libraries import *
from refrigerant_properties import*
from utilities.unit_defs import ureg, Q_

def calc_SOC(temperatures):
    node_volume = Q_('1000 m^3')/len(temperatures)
    reference_temperature = Q_(33, ureg.degC).to('kelvin')

    water_densities = Q_(PropsSI('D', 'T', temperatures.m, 'Q', 0, 'water'), 'kg/m^3')
    reference_water_density = Q_(PropsSI('D', 'T', reference_temperature.m, 'Q', 0, 'water'), 'kg/m^3')
    specific_internal_energies = Q_(PropsSI('U', 'T', temperatures.m, 'Q', 0, 'water'), 'J/kg')
    reference_specific_internal_energy = Q_(PropsSI('U', 'T', reference_temperature.m, 'Q', 0, 'water'), 'J/kg')

    masses = water_densities*node_volume
    reference_mass = reference_water_density*node_volume
    internal_energies = specific_internal_energies*masses
    reference_internal_energy = reference_specific_internal_energy*reference_mass
    energy_stored = internal_energies - reference_internal_energy
    return sum(energy_stored).to('MWh')

node_temperatures = Q_(np.array([67.7, 67.5, 67.4, 67.4, 67.0, 64.7, 59.3, 47.7, 39.5, 33.4, 33.3, 33.2, 30.0, 28.2]), ureg.degC).to(ureg.kelvin)
E = calc_SOC(node_temperatures)
print(f'{E:.2f~P}')