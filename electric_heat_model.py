##### Importing Libraries #####
# Libraries below are used to pull from for the Heat Pump model
from array import array
import math
import numpy as np
import numpy_financial as npf
import pandas as pd
import requests
import csv
import CoolProp
import yaml
from CoolProp.CoolProp import PropsSI 
from CoolProp.Plots import PropertyPlot
from CoolProp.Plots import SimpleCompressionCycle

from libraries import *
from refrigerant_properties import*
from utilities.unit_defs import ureg, Q_
# from uncertainties import ufloat as uf
# from uncertainties import unumpy as unp

class electric_heater:
    def __init__(self):
        ##### 2.Energy and Mass Flow #####
        ## Outputs
        ## Note keeping in line with heat pump model structure, the energy
        ## and mass flow is item number 2. Heat Pump item number 1 is COP 
        ## and electro-resistive heater has no COP.
        self.process_heat_requirement = Q_(np.array([-1.0]*2), 'kW')
        self.power_in = Q_(np.array([-1.0]*2), 'kW') # Gives the Energy into the heat pump in power
        self.thermal_efficiency = Q_('0.92')
        self.average_power_in = Q_('-1.0 kW')
        self.annual_energy_in = Q_('-1.0 MW*hr')

        self.hot_temperature_out = Q_(np.array([90]*8760), 'degC')
        self.cold_temperature_in = Q_(np.array([60]*8760), 'degC')

        ##### 3.Electro-resistive heater costs #####
        self.capital_cost = Q_('-1.0 USD')
        self.year_one_energy_costs = Q_('-1.0 USD/yr')
        self.year_one_fixed_o_and_m = Q_('-1.0 USD/yr')
        self.year_one_variable_o_and_m = Q_('-1.0 USD/yr')
        self.year_one_operating_costs = Q_('-1.0 USD/yr')
        self.LCOH = Q_('-1.0 USD / MMMBtu')
        self.capacity_factor = Q_('-1.0')

    def calculate_energy_and_mass_flow(self):
        print('calculated')

    def calculate_power_needed(self):
        print('calculated')

