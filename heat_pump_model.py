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

## Note: Default values set to -1.0 need to be calculated and are initialized, but will 
## return an error if not calculated first.

##### Initialization #####
## This class calls the heat pump model and initializes it to dummy values.
class heat_pump:
    ##### Model Variables #####
    def __init__(self):

        ##### 1.COP #####
        ## Outputs
        self.ideal_COP = np.array([-1.0]*2)*ureg.dimensionless
        self.actual_COP = np.array([-1.0]*2)*ureg.dimensionless
        self.refrigerant = []

        ##### 2.Energy and Mass Flow #####
        ## Outputs
        self.cold_final_temperature = Q_(np.array([-1.0]*2), 'degC')
        self.power_in = Q_(np.array([-1.0]*2), 'kW') # Gives the Energy into the heat pump in power
        self.average_power_in = Q_('-1.0 kW')
        self.annual_energy_in = Q_('-1.0 MW*hr')

        ##### 3.Heat Pump Costs #####
        ## Outputs
        self.capital_cost = Q_('-1.0 USD')
        self.year_one_energy_costs = Q_('-1.0 USD/yr')
        self.year_one_fixed_o_and_m = Q_('-1.0 USD/yr')
        self.year_one_variable_o_and_m = Q_('-1.0 USD/yr')
        self.year_one_operating_costs = Q_('-1.0 USD/yr')
        self.LCOH = Q_('-1.0 USD / MMMBtu')
        self.capacity_factor = Q_('-1.0')
        
        ##### 4. Natural Gas Costs #####
        ## Outputs
        self.gas_capital_cost = Q_('-1.0 USD')
        self.gas_year_one_energy_costs = Q_('-1.0 USD/yr')
        self.gas_year_one_fixed_o_and_m = Q_('-1.0 USD/yr')
        self.gas_year_one_variable_o_and_m = Q_('-1.0 USD/yr')
        self.gas_year_one_operating_costs = Q_('-1.0 USD/yr')
        self.gas_LCOH = Q_('-1.0 USD / (MW * hr)')

        ##### 5. Cash Flow Model #####
        self.net_present_value = Q_('0.0 USD')
        self.internal_rate_of_return = Q_('-1.0')
        self.payback_period = Q_('100.0 yr')

        self.construct_yaml_input_quantities('model_inputs.yml')

    
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


    def make_input_quantity(self, input_yaml_str):
        input_dict = yaml.safe_load(input_yaml_str)
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
        if isinstance(array_or_float, array):
            return np.sum(array_or_float)
        else:
            return self.n_hrs*array_or_float


    ## This subroutine within the heat pump class Initializes the heat pump to a process in the process library.
    ## This initialization is not essential as all values can be input individually, but this module is built to 
    ## simplify the building of the models.
    def initialize_heat_pump(self,sector,process_name):
        self.hot_temperature_desired = Q_(np.array([process[sector][process_name]['hot_temperature_desired']]*self.n_hrs), 'degC')
        self.hot_temperature_minimum = Q_(np.array([process[sector][process_name]['hot_temperature_minimum']]*self.n_hrs), 'degC')
        self.hot_specific_heat = Q_(working_fluid[process[sector][process_name]['hot_working_fluid']]['specific_heat'], 'kJ / kg / degK')
        self.cold_temperature_available = Q_(np.array([process[sector][process_name]['waste_temperature']]*self.n_hrs), 'degC')

    ##### Model Calculations #####
    ## Calculating the COP
    def calculate_COP(self):
        
        # Calculating the ideal COP to begin with, this will be independent of the future anlaysis.
        self.ideal_COP = ((self.hot_temperature_desired.to('degK') + self.hot_buffer.to('degK')) )/((self.hot_temperature_desired.to('degK') + self.hot_buffer.to('degK')) - (self.cold_temperature_available.to('degK') - self.cold_buffer.to('degK')))

        if self.second_law_efficiency_flag == True:
            # If the carnot efficiency factor is true calculation the actual COP
            self.actual_COP = self.ideal_COP * self.second_law_efficiency
        else:
            # If the carnot efficiency factor is false requires more work in several steps
            # 1. If no refrigerant is selected pick one
            # 2. Using selected refrigerant calculate compressor efficiency
            # 3. Calculate actual COP from compressor efficiency
            # 4. Throw an error if calculation could not be completed.

            # Below will attempt to choose a refrigerant and calculate a realistic compressor efficiency from it, if this fails, it will revert to the carnot efficiency factor methodology
            ## Estimating Refrigerant Performance
            if self.refrigerant_flag != True:
                self.refrigerant = []
                for test_refrigerant in refrigerants:
                    t_crit = Q_(PropsSI(test_refrigerant, 'Tcrit'), 'kelvin').to('degC')
                    ## Checking if the refrigerant's critical temperature is at least 30°C > than the process temp.
                    if t_crit > (np.amax(self.hot_temperature_desired) + self.t_crit_delta):
                        self.refrigerant.append(test_refrigerant)
                
                print('Potential refrigerants include: ', self.refrigerant)
                ## Here the refrigerant with the lowest critical pressure, and therefore hopefully the lowest compression ratio
                ## is found and that will be recommended
                ## Need to update to reflect the fact that best refrigerant might not be the one with the lowest critical pressure
                min_p_crit = Q_('1e9 Pa')
                for test_refrigerant in self.refrigerant:
                    p_crit = Q_(PropsSI(test_refrigerant, 'Pcrit'), 'Pa')
                    if p_crit < min_p_crit:
                        min_p_crit = p_crit
                        self.refrigerant = test_refrigerant

            print('Selected refrigerant (based on user selection or minimual p_crit) is: ', self.refrigerant)

            ## Adjust such that this is below the Carnot Efficiency Factor 
            # Cycle calculation
            # Here the cycle points will be calculated. These points are:
            #  1. Compressor inlet
            #  2. Compressor outlet
            #  3. Expansion valve inlet
            #  4. Expansion valve outlet
            #  2-3 is the condenser where heat is expelled from the heat pump condenser to the heat sink or high temperature working fluid stream
            #  4-1 is the evaporator where heat is absorbed from the heat source or cold temperature working fluid to the heat pump evaporator
            self.refrigerant_high_temperature = self.hot_temperature_desired.to(ureg.degK) + self.hot_buffer.to(ureg.degK)
            self.refrigerant_low_temperature = self.cold_temperature_available.to(ureg.degK) - self.cold_buffer.to(ureg.degK)

            try:
                T_1 = np.array(self.refrigerant_low_temperature.m)
                T_3 = np.array(self.refrigerant_high_temperature.m)

                # Calculating Cycle Parameters
                P_1 = PropsSI('P', 'T', T_1, 'Q', 1, self.refrigerant)
                S_1 = PropsSI('S', 'T', T_1, 'Q', 1, self.refrigerant)
                H_1 = PropsSI('H', 'T', T_1, 'Q', 1, self.refrigerant)

                P_3 = PropsSI('P', 'T', T_3, 'Q', 0, self.refrigerant)
                S_3 = PropsSI('S', 'T', T_3, 'Q', 0, self.refrigerant)
                H_3 = PropsSI('H', 'T', T_3, 'Q', 0, self.refrigerant)

                T_2 = PropsSI('T', 'S', S_1, 'P', P_3, self.refrigerant)
                H_2 = PropsSI('H', 'S', S_1, 'P', P_3, self.refrigerant)

                P_2 = P_3
                H_2_prime = PropsSI('H', 'S', S_1, 'P', P_3, self.refrigerant)
                H_2 = H_1 + (H_2_prime - H_1)/(self.compressor_efficiency.m) # Remark, it should be tested if the state 2 (H_2, P_2) is in the 2-phase region or not
                T_2 = PropsSI('T', 'H', H_2, 'P', P_2, self.refrigerant)
                self.actual_COP = (np.divide((H_2 - H_3), (H_2 - H_1)))*ureg.dimensionless

                # There is an efficiency associated with the pressure ratio and an efficiency association with the volume ratio
                # The VR is taken from experimental values which we do not fully have, so will integrate as part of year 2
                # For now the VR is set to a constant value.
                # The compressor efficiency can also be set by the user
                # PR = P_2/P_1
                # eta_pr = 0.95-0.01*PR
                # eta_vr = 0.70
                # self.compressor_efficiency[i] = round(eta_vr*eta_pr, 3)
                # self.actual_COP = self.ideal_COP * self.compressor_efficiency

            except:
                print('There was an error calling refrigerant properties. Please check inputs and try again.')
                quit()

        if self.print_results: print('Calculate COP Called')
        if self.print_results: print('Average Theoretical COP: ', np.mean(self.ideal_COP))
        if self.print_results: print('Average Estimated COP: ', np.mean(self.actual_COP))

    ## Calculating working fluid energy and mass balance
    def calculate_energy_and_mass_flow(self):
        if self.print_results: print('Calculate Energy and Mass Called')

        # Initializing Temporary Arrays
        h_hi = Q_(np.array([-1.0]*self.n_hrs), 'J/kg')
        h_ho = Q_(np.array([-1.0]*self.n_hrs), 'J/kg')
        h_ci = Q_(np.array([-1.0]*self.n_hrs), 'J/kg')
        h_co = Q_(np.array([-1.0]*self.n_hrs), 'J/kg')

        # Converting MMBTU to kWh/hr (as it is expressed for the full hours of the year)
        # self.process_heat_requirement_kw = self.process_heat_requirement.to(ureg.kW)

        # Calculating the Hot and Cold Mass Flow Parameters
        ## Hot
        h_hi = Q_(PropsSI('H', 'T', self.hot_temperature_minimum.to('degK').m, 'P', self.hot_pressure.to('Pa').m, self.hot_refrigerant), 'J/kg')
        h_ho = Q_(PropsSI('H', 'T', self.hot_temperature_desired.to('degK').m, 'P', self.hot_pressure.to('Pa').m, self.hot_refrigerant), 'J/kg')
        try:
            if (self.hot_mass_flowrate == None) and (self.process_heat_requirement != None):
                self.hot_mass_flowrate = (self.process_heat_requirement.to('W')/(h_ho - h_hi)).to('kg/s')
            else:
                self.process_heat_requirement = (self.hot_mass_flowrate.to('kg/s')*(h_ho - h_hi)).to('kW')
        except:
            print('Provide either .hot_mass_flowrate or .process_heat_requirement.')
            quit()

        ## Cold
        cold_dT_array = self.cold_buffer - self.cold_deltaT

        h_ci = Q_(PropsSI('H', 'T', self.cold_temperature_available.to('degK').m, 'P', self.cold_pressure.to('Pa').m, self.cold_refrigerant), 'J/kg')
        self.cold_final_temperature = self.cold_temperature_available - cold_dT_array
        h_co = Q_(PropsSI('H', 'T', self.cold_final_temperature.to('degK').m, 'P', self.cold_pressure.to('Pa').m, self.cold_refrigerant), 'J/kg')
        self.cold_mass_flowrate = self.process_heat_requirement.to('W')/(h_ci - h_co)
    
        # Getting average values for reporting
        self.hot_mass_flowrate_average = np.mean(self.hot_mass_flowrate).to('kg /s')
        
        if self.print_results: 
            print('Hot Mass Flow Average: {:~.3P}'.format(self.hot_mass_flowrate_average))
            print('Cold Average Outlet Temperature: {:~.2fP}'.format(np.mean(self.cold_final_temperature)))

        # Calculating the Work into the heat pump
        self.power_in = self.process_heat_requirement.to('kW')/self.actual_COP
        #for i in range(0,8760):
        #    self.power_in[i] = self.process_heat_requirement_kw[i]/self.actual_COP
        self.average_power_in = np.mean(self.power_in)
        self.annual_energy_in = self.mysum(self.power_in*Q_('1 hour')).to('kWh')

        if self.print_results: 
            print('Average Power Draw of Heat Pump: {:~.3fP}'.format(self.average_power_in))
            print('Maximum Power Draw of Heat Pump: {:~.3fP}'.format(np.amax(self.power_in)))
            print('Annual Electricity in: {:,~.1fP}'.format(self.annual_energy_in))

    ## Calculating Heat Pump Costs
    def calculate_heat_pump_costs(self):
        if self.print_results: print('Calculate Heat Pump Costs')
        # Heat pump costs are estimated based on the maximum electrical power in.
        #self.capital_cost = self.specific_capital_cost * max(self.power_in)
        # Heat pump costs are estimated based on the maximum thermal power required in kW

        self.capital_cost = self.specific_capital_cost * np.max(self.process_heat_requirement.to('kW'))
        self.year_one_fixed_o_and_m = self.fixed_o_and_m_per_size*np.max(self.process_heat_requirement.to('MMBtu/hr'))/Q_('1 yr')
        self.year_one_fixed_o_and_m = self.year_one_fixed_o_and_m
        self.year_one_variable_o_and_m = self.variable_o_and_m*self.mysum(self.process_heat_requirement.to('MMBtu/hr')*Q_('1 hr'))/Q_('1 yr')
        self.year_one_variable_o_and_m = self.year_one_variable_o_and_m

        # Calculating the Capacity Factor
        self.capacity_factor = self.mysum(self.process_heat_requirement.to('kW'))/(self.n_hrs*np.max(self.process_heat_requirement.to('kW')))

        # Calculating the kWh costs
        kwh_costs = Q_(np.array([0.0]*self.n_hrs), 'USD')
        kwh_costs = self.hourly_utility_rate*self.power_in*Q_('1 hr')
        # Currently demand charges are taken from the largest demand
        kw_costs = 12*self.utility_rate*np.amax(self.power_in) # What is this 12? What are the units?

        self.year_one_energy_costs = (np.sum(kwh_costs)+kw_costs)/Q_('1 yr')
        self.year_one_operating_costs = self.year_one_fixed_o_and_m + self.year_one_variable_o_and_m + self.year_one_energy_costs
        self.year_one_operating_costs = self.year_one_operating_costs

        self.LCOH = (self.capital_cost + self.lifetime*self.year_one_operating_costs)/(self.lifetime*self.mysum(self.process_heat_requirement.to('MMBtu/hr')*Q_('1 hr'))/Q_('1 yr'))

        if self.print_results: 
            print('Capital Cost: {:,~.2fP}'.format(self.capital_cost))
            print('Capacity Factor: {:~.3fP}'.format(self.capacity_factor))
            print('One Year Fixed O&M Costs: {:,~.2fP}'.format(self.year_one_fixed_o_and_m))
            print('One Year Variable O&M Costs: {:,~.2fP}'.format(self.year_one_variable_o_and_m))
            print('One Year Energy Costs: {:,~.2fP}'.format(self.year_one_energy_costs))
            print('One Year Operating Costs: {:,~.2fP}'.format(self.year_one_operating_costs))
            print('Lifetime LCOH: {:,~.2fP}'.format(self.LCOH))

    ## Calculating Natural Gas Prices (might remake to be a repeat of heat pump and make ubiquitous)
    def calculate_natural_gas_comparison(self):
        if self.print_results: print('Calculate Natural Gas Comparison')
        if self.existing_gas == True:
            self.gas_capital_cost = Q_('0.0 USD')
        else:
            self.gas_capital_cost = self.specific_gas_capital_cost * np.max(self.process_heat_requirement.to('MMBtu/hr'))/self.gas_efficiency
            self.gas_capital_cost = self.gas_capital_cost
        self.gas_year_one_fixed_o_and_m = self.gas_fixed_o_and_m_per_size*np.max(self.process_heat_requirement.to('MMBtu/hr'))
        self.gas_year_one_fixed_o_and_m = self.gas_year_one_fixed_o_and_m
        self.gas_year_one_variable_o_and_m = self.gas_variable_o_and_m_per_mmbtu*self.mysum(self.process_heat_requirement.to('MMBtu/hr')*Q_('1 hr'))/(Q_('1 yr')*self.gas_efficiency)
        self.gas_year_one_variable_o_and_m = self.gas_year_one_variable_o_and_m

        # Calculating Emissions
        # 1020 from 1 MMSCF/1020 MMBTU
        # 2000 from 1 ton/2000 lb
        # Calculated using EPA estimate: https://www.epa.gov/sites/production/files/2016-09/boilers_and_emergency_engines_pte_calculator_version_1.0.xlsx 

        self.gas_year_one_emissions = (self.mysum(self.process_heat_requirement.to('MMBtu/yr'))/self.gas_efficiency) * self.gas_emissions_factor.to('ton / MMSCF')*self.gas_emissions_volume_per_energy
        self.gas_year_one_cost_of_emissions =   (self.carbon_price * self.gas_year_one_emissions)

        # fuel_costs = Q_(np.array([0.0]*self.n_hrs), 'USD/hr')
        fuel_costs = self.gas_price*self.process_heat_requirement.to('MMBtu/hr')
        self.gas_year_one_energy_costs = (self.mysum(fuel_costs*Q_('1 hr')))/Q_('1 yr')
        self.gas_year_one_operating_costs = self.gas_year_one_fixed_o_and_m + self.gas_year_one_variable_o_and_m + self.gas_year_one_energy_costs + self.gas_year_one_cost_of_emissions 
        self.gas_year_one_operating_costs = self.gas_year_one_operating_costs

        self.gas_LCOH = (self.gas_capital_cost+ self.lifetime*self.gas_year_one_operating_costs)/(self.lifetime*self.mysum(self.process_heat_requirement.to('MMBtu/hr')*Q_('1 hr'))/Q_('1 yr'))

        self.gas_LCOH = self.gas_LCOH.to('USD/MMBtu')

        if self.print_results: 
            print('Gas Capital Cost: {:,~.2fP}'.format(self.gas_capital_cost))
            print('Gas One Year Fixed O&M Costs: {:,~.2fP}'.format(self.gas_year_one_fixed_o_and_m))
            print('Gas One Year Variable O&M Costs: {:,~.2fP}'.format(self.gas_year_one_variable_o_and_m))
            print('Gas One Year Energy Costs: {:,~.2fP}'.format(self.gas_year_one_energy_costs))
            print('Gas One Year Operating Costs: {:,~.2fP}'.format(self.gas_year_one_operating_costs))
            print('Gas Lifetime LCOH: {:,~.2fP}'.format(self.gas_LCOH))

    def calculate_cash_flow(self):  
        if self.print_results: print('Calculate Cash Flow')
        # Compare to a new build natural gas plant
        annual_cashflow = []
        # If true, the full cost of the heat pump is included, if false, than 
        # the cost of the natural gas plant is subtracted from the capital cost of the heat pump to compare.
        if self.existing_gas == True:
            annual_cashflow.append(-1*(self.capital_cost.m))
        else:
            annual_cashflow.append(-1*(self.capital_cost.m - self.gas_capital_cost.m))
        
        # The Cashflow model is always the cost saved by using the heat pump. 
        # The price of carbon is included in the cost of the natural gas plant.
        for i in range(1, int(self.lifetime.magnitude+1)):
            gas_CAGR_energy_costs = self.gas_year_one_energy_costs*math.e**(i*math.log(1+self.gas_CAGR))
            kwh_CAGR_energy_costs = self.year_one_energy_costs*math.e**(i*math.log(1+self.kwh_CAGR))
            annual_gas_operating_cost = self.gas_year_one_fixed_o_and_m + self.gas_year_one_variable_o_and_m + self.gas_year_one_cost_of_emissions + gas_CAGR_energy_costs
            annual_kwh_operating_cost = self.year_one_fixed_o_and_m + self.year_one_variable_o_and_m + kwh_CAGR_energy_costs
            annual_cashflow.append(annual_gas_operating_cost.m - annual_kwh_operating_cost.m)
            #print(i, 'gas', gas_CAGR_energy_costs, 'total', annual_gas_operating_cost)

        # Calculating and outputting (pint not working well with npf, so using some workarounds for now)
        self.net_present_value = Q_(npf.npv(self.discount_rate.m, annual_cashflow), 'USD')
        if self.print_results: print('NPV: {:,~.2fP}'.format(self.net_present_value))
        self.internal_rate_of_return = Q_(npf.irr(annual_cashflow), 'dimensionless').to('pct')
        if self.print_results: print('IRR: {:~.3fP}'.format(self.internal_rate_of_return))
        # Need to calcuate year 1 energy Savings
        try:
            self.payback_period = math.log(1/(1-(self.capital_cost-self.gas_capital_cost)*self.discount_rate/annual_cashflow[1]))/math.log(1+self.discount_rate)
            if self.print_results: print('PBP: {:~.2fP}'.format(self.payback_period))
        except:
            self.payback_period = 'NA'
            if self.print_results: print('PBP: {:~P}'.format(Q_(self.payback_period, 'yr')))
        
    def write_output(self, filename):
        data = [
            ['Cold Temperature Available', '{:~.2fP}'.format(self.cold_temperature_available)],
            ['Cold Temperature Final', '{:~.2fP}'.format(self.cold_final_temperature)],
            ['Cold Mass Flowrate', '{:~.3fP}'.format(np.mean(self.cold_mass_flowrate).to('kg / s'))],
            ['Hot Temperature Desired', '{:~.2fP}'.format(self.hot_temperature_desired)],
            ['Hot Temperature Minimum', '{:~.2fP}'.format(self.hot_temperature_minimum)],
            ['Hot Mass Flowrate', '{:~.3fP}'.format(self.hot_mass_flowrate_average)],
            ['Ideal COP Calculated', '{:~.3fP}'.format(self.ideal_COP)],
            ['Selected Refrigerant', self.refrigerant],
            ['Estimated Compressor Efficiency', '{:~.3fP}'.format(self.compressor_efficiency)],
            ['Second Law Efficiency', '{:~.3fP}'.format(self.second_law_efficiency)],
            ['Carnot Efficiency Factor Flag ', self.second_law_efficiency_flag],
            ['Actual COP Calculated', '{:~.3fP}'.format(self.actual_COP)],
            ['Process Heat Average', '{:~.2fP}'.format(np.mean(self.process_heat_requirement.to('MMBtu/hr')))],
            ['Process Heat Average', '{:~.2fP}'.format(np.mean(self.process_heat_requirement.to('kW')))],
            ['Utility Rate Average', '{:,~.2fP}'.format(np.mean(self.hourly_utility_rate))],
            ['Capacity Factor', '{:~.3fP}'.format(np.mean(self.capacity_factor))],
            ['Project Lifetime', '{:~.2fP}'.format(self.lifetime)],
            ['HP Power in Average', '{:~.2fP}'.format(self.average_power_in)],
            ['HP Annual Energy In', '{:~.2fP}'.format(self.annual_energy_in)],
            ['HP Capital Cost Per Unit', '{:,~.2fP}'.format(self.specific_capital_cost)],
            ['HP Fixed O&M Costs', '{:,~.2fP}'.format(self.fixed_o_and_m_per_size)],
            ['HP Variable O&M Costs', '{:,~.2fP}'.format(self.variable_o_and_m)],
            ['HP Capital Cost', '{:,~.2fP}'.format(self.capital_cost)],
            ['HP Year One Energy Costs', '{:,~.2fP}'.format(self.year_one_energy_costs)],
            ['HP Year One Fixed O&M Costs', '{:,~.2fP}'.format(self.year_one_fixed_o_and_m)],
            ['HP Year One Variable O&M Costs', '{:,~.2fP}'.format(self.year_one_variable_o_and_m)],
            ['HP Year One Total Operating Costs', '{:,~.2fP}'.format(self.year_one_operating_costs)],
            ['HP LCOH', '{:,~.2fP}'.format(self.LCOH)],
            ['Gas Capital Cost Per Unit', '{:,~.2fP}'.format(self.specific_gas_capital_cost)],
            ['Gas Fixed O&M Costs', '{:,~.2fP}'.format(self.gas_fixed_o_and_m_per_size)],
            ['Gas Variable O&M Costs', '{:,~.2fP}'.format(self.gas_variable_o_and_m_per_mmbtu)],
            ['Gas Average Price', '{:,~.2fP}'.format(np.mean(self.gas_price))],
            ['Gas Capital Cost', '{:,~.2fP}'.format(self.gas_capital_cost)],
            ['Gas Year One Energy Costs', '{:,~.2fP}'.format(self.gas_year_one_energy_costs)],
            ['Gas Year One Fixed O&M Costs', '{:,~.2fP}'.format(self.gas_year_one_fixed_o_and_m)],
            ['Gas Year One Variable O&M Costs', '{:,~.2fP}'.format(self.gas_year_one_variable_o_and_m)],
            ['Gas Year One Total Operating Costs', '{:,~.2fP}'.format(self.gas_year_one_operating_costs)],
            ['Gas LCOH', '{:,~.2fP}'.format(self.gas_LCOH)],
            ['Gas Emissions', '{:~.2fP}'.format(self.gas_year_one_emissions)],
            ['Gas Social Cost of Emissions', '{:,~.2fP}'.format(self.gas_year_one_cost_of_emissions)],
            ['Net Present Value', '{:,~.2fP}'.format(self.net_present_value)],
            ['Internal Rate of Return pct', '{:~.3fP}'.format(self.internal_rate_of_return)],
            ['Payback Period', '{:~P}'.format(Q_(self.payback_period, 'yr'))]
            ]
        
        df_output = pd.DataFrame(data,columns=['Variable','Value'])
        df_output.to_csv('output/'+filename+'.csv')
        if self.print_results: print('Writing all output to a file')

    def run_all(self,filename):
        self.calculate_COP()
        self.calculate_energy_and_mass_flow()
        self.calculate_heat_pump_costs()
        self.calculate_natural_gas_comparison()
        self.calculate_cash_flow()
        if self.write_output_file: self.write_output(filename)

