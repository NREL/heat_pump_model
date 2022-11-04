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

class gas_heater:
    def __init__(self):
        self.n_hrs = 8760
        ##### 2.Energy and Mass Flow #####
        ## Outputs
        ## Note keeping in line with heat pump model structure, the energy
        ## and mass flow is item number 2. Heat Pump item number 1 is COP 
        ## and electro-resistive heater has no COP.
        self.process_heat_requirement = Q_(np.array([-1.0]*2), 'kW')
        self.power_in = Q_(np.array([-1.0]*2), 'kW') # Gives the Energy into the heat pump in power
        self.thermal_efficiency = np.array([1.0]*self.n_hrs)*ureg.dimensionless
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

        #self.construct_yaml_input_quantities('gas_model_inputs.yml')
    
    def construct_yaml_input_quantities(self, file_path):
        with open(file_path, "r") as file_desc:
            input_dict = yaml.safe_load(file_desc)

        for key in input_dict:
            var = input_dict[key]
            try:
                if not isinstance(var, dict):
                    continue
                else:
                    quant = Q_(var['val'], var['unit'])
                input_dict[key] = quant
            except KeyError:
                print('Something is wrong with input variable ' + key)
                quit()
        self.__dict__.update(input_dict)

    def mysum(self, array_or_float):
        try:
            if len(array_or_float.magnitude) > 1.0:
                return np.sum(array_or_float)
            else:
                return self.n_hrs*array_or_float
        except(TypeError):
            return self.n_hrs*array_or_float

    def calculate_energy_and_mass_flow(self):
        if self.print_results: print('Calculate Energy and Mass Called')

        # Calculating working fluid enthalpy change
        h_i = Q_(np.array([-1.0]*self.n_hrs), 'J/kg')
        h_o = Q_(np.array([-1.0]*self.n_hrs), 'J/kg')
        h_i = Q_(PropsSI('H', 'T', self.cold_temperature.to('degK').m, 'P', self.cold_pressure.to('Pa').m, self.working_fluid), 'J/kg')
        h_o = Q_(PropsSI('H', 'T', self.hot_temperature.to('degK').m, 'P', self.hot_pressure.to('Pa').m, self.working_fluid), 'J/kg')
        
        # Calculating the working fluid flowrate
        self.working_fluid_flowrate = (self.process_heat_requirement.to('W')/(h_o - h_i)).to('kg/s')
        self.working_fluid_flowrate_average = np.mean(self.working_fluid_flowrate).to('kg /s')
        if self.print_results: 
            print('Hot Mass Flow Average: {:~.3P}'.format(self.working_fluid_flowrate_average))

        # Calculating the Work into the Gas Heater
        self.power_in = self.process_heat_requirement.to('kW')/self.thermal_efficiency
        self.average_power_in = np.mean(self.power_in)
        self.annual_energy_in = self.mysum(self.power_in*Q_('1 hour')).to('kWh')

        self.fuel_consumed = self.emissions_volume_per_energy*self.annual_energy_in.to('MMBtu')

        if self.print_results: 
            print('Average Power Draw of Gas Heater: {:~.3fP}'.format(self.average_power_in))
            print('Maximum Power Draw of Gas Heater: {:~.3fP}'.format(np.amax(self.power_in)))
            print('Annual Gas in: {:,~.1fP}'.format(self.fuel_consumed))


    def calculate_costs(self):

        self.capital_cost = self.specific_capital_cost * np.max(self.process_heat_requirement.to('kW'))
        self.capital_cost = self.capital_cost.to('USD')
        self.year_one_fixed_o_and_m = self.fixed_o_and_m_per_size*np.max(self.process_heat_requirement.to('MMBtu/hr'))/Q_('1 yr')
        self.year_one_fixed_o_and_m = self.year_one_fixed_o_and_m
        self.year_one_variable_o_and_m = self.variable_o_and_m*self.mysum(self.process_heat_requirement.to('MMBtu/hr')*Q_('1 hr'))/Q_('1 yr')
        self.year_one_variable_o_and_m = self.year_one_variable_o_and_m

        self.capacity_factor = self.mysum(self.process_heat_requirement.to('kW'))/(self.n_hrs*np.max(self.process_heat_requirement.to('kW')))

        # Calculating emissions costs
        self.year_one_emissions = (self.mysum(self.process_heat_requirement.to('MMBtu/yr'))/self.thermal_efficiency) * self.emissions_factor.to('ton / MMSCF')*self.emissions_volume_per_energy
        self.year_one_cost_of_emissions =   (self.emissions_carbon_price * self.year_one_emissions)

        # Calculating Fuel Costs
        self.year_one_fuel_costs = self.gas_price*self.process_heat_requirement.to('MMBtu/hr')/self.thermal_efficiency
        self.year_one_energy_costs = (self.mysum(self.year_one_fuel_costs*Q_('1 hr')))/Q_('1 yr')
        
        # Combinging
        self.year_one_operating_costs = self.year_one_fixed_o_and_m + self.year_one_variable_o_and_m + self.year_one_energy_costs + self.year_one_cost_of_emissions
        self.year_one_operating_costs = self.year_one_operating_costs


        ## Need to edit from here, and add gas increase cost rate
        self.LCOH = (self.capital_cost + self.lifetime*self.year_one_operating_costs)/(self.lifetime*self.mysum(self.process_heat_requirement.to('MMBtu/hr')*Q_('1 hr'))/Q_('1 yr'))

        if self.print_results: 
            print('Capital Cost: {:,~.2fP}'.format(self.capital_cost))
            print('Capacity Factor: {:~.3fP}'.format(self.capacity_factor))
            print('One Year Fixed O&M Costs: {:,~.2fP}'.format(self.year_one_fixed_o_and_m))
            print('One Year Variable O&M Costs: {:,~.2fP}'.format(self.year_one_variable_o_and_m))
            print('One Year Energy Costs: {:,~.2fP}'.format(self.year_one_energy_costs))
            print('One Year Operating Costs: {:,~.2fP}'.format(self.year_one_operating_costs))
            print('Lifetime LCOH: {:,~.2fP}'.format(self.LCOH.to('USD/MMBtu')))

    def write_output(self, filename):
        data = [
            ['Cold Temperature Available', '{:~.2fP}'.format(self.cold_temperature)],
            ['Mass Flowrate', '{:~.3fP}'.format(np.mean(self.working_fluid_flowrate).to('kg / s'))],
            ['Hot Temperature Desired', '{:~.2fP}'.format(self.hot_temperature)],
            ['Hot Mass Flowrate', '{:~.3fP}'.format(self.working_fluid_flowrate_average)],
            ['Gas Heater Efficiency', '{:~.3fP}'.format(self.thermal_efficiency)],
            ['Process Heat Average', '{:~.2fP}'.format(np.mean(self.process_heat_requirement.to('MMBtu/hr')))],
            ['Process Heat Average', '{:~.2fP}'.format(np.mean(self.process_heat_requirement.to('kW')))],
            ['Gas Price', '{:~.2fP}'.format(self.gas_price)],
            ['Capacity Factor', '{:~.3fP}'.format(np.mean(self.capacity_factor))],
            ['Project Lifetime', '{:~.2fP}'.format(self.lifetime)],
            ['Power in Average', '{:~.2fP}'.format(self.average_power_in)],
            ['Annual Energy In', '{:~.2fP}'.format(self.annual_energy_in)],
            ['Fuel Used', '{:~.2fP}'.format(self.fuel_consumed)],
            ['Capital Cost Per Unit', '{:,~.2fP}'.format(self.specific_capital_cost)],
            ['Fixed O&M Costs', '{:,~.2fP}'.format(self.fixed_o_and_m_per_size)],
            ['Variable O&M Costs', '{:,~.2fP}'.format(self.variable_o_and_m)],
            ['Capital Cost', '{:,~.2fP}'.format(self.capital_cost)],
            ['Emissions', '{:~.2fP}'.format(self.year_one_emissions)],
            ['Year One Energy Costs', '{:,~.2fP}'.format(self.year_one_energy_costs)],
            ['Year One Fixed O&M Costs', '{:,~.2fP}'.format(self.year_one_fixed_o_and_m)],
            ['Year One Variable O&M Costs', '{:,~.2fP}'.format(self.year_one_variable_o_and_m)],
            ['Year One Total Operating Costs', '{:,~.2fP}'.format(self.year_one_operating_costs)],
            ['LCOH', '{:,~.2fP}'.format(self.LCOH)]
            ]
        
        df_output = pd.DataFrame(data,columns=['Variable','Value'])
        df_output.to_csv('output/'+filename+'.csv')
        if self.print_results: print('Writing all output to a file')


    def run_all(self,filename):
        self.calculate_energy_and_mass_flow()
        self.calculate_costs()
        if self.write_output_file: self.write_output(filename)


