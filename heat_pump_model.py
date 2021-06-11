##### Importing Libraries #####
# Libraries below are used to pull from for the Heat Pump model
import math
import numpy as np
import numpy_financial as npf
import pandas as pd 
import requests
import csv
import CoolProp
from CoolProp.CoolProp import PropsSI 
from CoolProp.Plots import PropertyPlot
from CoolProp.Plots import SimpleCompressionCycle

from libraries import *

## Note: Default values set to -1.0 need to be calculated and are initialized, but will 
## return an error if not calculated first.

## Define Libraries
# Specific Heat (kJ/kgK) and Density (kg/m^3) at atmosphere

##### Initialization #####
## This class calls the heat pump model and initializes it to dummy values.
class heat_pump:
    ##### Model Variables #####
    def __init__(self):
        ##### IO #####
        self.print_results = True
        self.write_output_file = True

        ##### 1.COP #####
        ## Inputs
        self.cold_temperature_available = 50 # Common hot water waste Temp making up the 'cold stream avilable'
        self.hot_temperature_desired = 160  # Theoretical maximum of heat pumps as defaults
        self.carnot_efficiency_factor = 0.5 # Ratio of Actual Efficiency to Carnot Efficiency (to be deprecated by better compressor model)
        # If the refrigerant selection process fails, the flag is changed to true so that it can be automatically analyzed post processing
        self.carnot_efficiency_factor_flag = False
        ## Outputs
        self.ideal_COP = -1.0
        self.actual_COP = -1.0
        self.refrigerant = []
        # The hot and cold buffer are the temperature difference between the working fluid and the hot and cold streams, a measure of the heat exchanger efficiency
        self.cold_buffer = 5.0
        self.hot_buffer = 5.0
        self.compressor_efficiency = -1.0
        # Setting a default refrigerant
        self.refrigerant = 'R1234ze(Z)'
        self.refrigerant_flag = False

        ##### 2.Energy and Mass Flow #####
        ## Inputs
        self.cold_specific_heat = 4.187 #kJ/kgK (Water)
        self.cold_mass_flow = [1]*8760 #kg/S 
        self.hot_specific_heat = 1.009 #kJ/kgK (Air)
        self.hot_temperature_minimum = 145 # minimum allowable temperature of the hot stream
        self.process_heat_requirement = [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0] * 365 # Meant to be in terms of MMBUT per hour
        self.process_heat_requirement_kw = [-1.0] * 8760 
        #self.process_power_kW = 1.055e6*self.process_heat_requirement/3600
        ## Outputs
        self.cold_final_temperature = -1.0
        self.hot_mass_flowrate = [-1.0]*8760
        self.power_in = [-1.0]*8760 # Gives the Energy into the heat pump in power
        self.average_power_in = -1.0
        self.annual_energy_in = -1.0


        ##### 3.Heat Pump Costs #####
        ## Inputs
        # 200 euro/kW -> $240/kW
        # 600 euro/kW -> $710/kW
        # 900 euro/kW -> $1070/kW
        self.capital_cost_per_size = 590 # $/kW sizing
        # Yearly O&M is assumed at 2.0% of capital cost
        self.fixed_o_and_m_per_size = 0.02*self.capital_cost_per_size # $/MMBTU/hr/year (Assuming here that it is based on the maximum heating load size)
        self.variable_o_and_m_per_mmbtu = 0.05 #$/MMBTU (Per MMBTU delivered, but likely will be based on hours and capacity factors)
        self.utility_rate_kwh = [0.02] * 8760 #$/kWh over an 8760 timeframe
        self.utility_rate_kw = 10
        # Because Power can be specified hourly, currently capacity factor is not used.
        self.capacity_factor = [1.0] * 8760 # Default to 8 hours per day 365
        self.lifetime_yrs = 20
        self.discount_rate = 0.04
        ## Outputs
        self.capital_cost = -1.0
        self.year_one_energy_costs = -1.0
        self.year_one_fixed_o_and_m = -1.0
        self.year_one_variable_o_and_m = -1.0
        self.year_one_operating_costs = -1.0
        self.LCOH = -1.0
        
        ##### 4. Natural Gas Costs #####
        ## Inputs
        self.gas_capital_cost_per_size = 90000 #$/MMBTU/hr
        self.gas_fixed_o_and_m_per_size = 50 # $/MMBTU/hr/year
        self.gas_variable_o_and_m_per_mmbtu = 0.01 # $/MMBTU
        self.gas_price_MMBTU = [3.5] * 8760 
        self.gas_efficiency = 0.8
        self.gas_emissions_factor = 120000
        ## Outputs
        self.gas_capital_cost = -1.0
        self.gas_year_one_energy_costs = -1.0
        self.gas_year_one_fixed_o_and_m = -1.0
        self.gas_year_one_variable_o_and_m = -1.0
        self.gas_year_one_operating_costs = -1.0
        self.gas_LCOH = -1.0
        # Emissions
        self.carbon_price_per_ton = 0.0
        self.gas_year_one_emissions = 0.0

        ##### 5. Cash Flow Model #####
        self.kwh_CAGR = 0.00
        self.gas_CAGR = 0.00
        self.net_present_value = -1.0
        self.internal_rate_of_return = -1.0
        self.payback_period = 100.0
        self.existing_gas = False

        ##### Future Work #####
        # Latitude and Longitude is to use the Utility Rate Database
        # Currently not used but is set to an 'industrial' electricity schedule in Oregon
        self.lat = 39.74077
        self.long = -105.16888
        self.schedule = 'industrial'
    
    ## This subroutine within the heat pump class Initializes the heat pump to a process in the process library.
    ## This initialization is not essential as all values can be input individually, but this modul is built to 
    ## simplify the building of the models.
    def initialize_heat_pump(self,sector,process_name):
        self.hot_temperature_desired = process[sector][process_name]['hot_temperature_desired']
        self.hot_temperature_minimum = process[sector][process_name]['hot_temperature_minimum']
        self.hot_specific_heat = working_fluid[process[sector][process_name]['hot_working_fluid']]['specific_heat']
        self.cold_temperature_available = process[sector][process_name]['waste_temperature']

    ##### Model Calculations #####
    ## Calculating the COP
    def calculate_COP(self):
        
        # Calculating the ideal COP to begin with, this will be independent of the future anlaysis.
        self.ideal_COP = (self.hot_temperature_desired + 273.0)/(self.hot_temperature_desired - self.cold_temperature_available)

        # Below will attempt to choose a refrigerant and calculate a realistic compressor efficiency from it, if this fails, it will revert to the carnot efficiency factor methodology
        ## Estimating Refrigerant Performance
        if self.refrigerant_flag != True:
            self.refrigerant = []
            for test_refrigerant in refrigerants:
                t_crit = PropsSI(test_refrigerant, 'Tcrit') - 273.15
                ## Checking if the refrigerant's critical temperature is at least 5°C > than the process temp.
                if t_crit > (self.hot_temperature_desired + 10):
                    self.refrigerant.append(test_refrigerant)
            
            ## Here the refrigerant with the lowest critical pressure, and therefore hopefully the lowest compression ratio
            ## is found and that will be recommended
            min_p_crit = 1e9
            for test_refrigerant in refrigerants:
                p_crit = PropsSI(test_refrigerant, 'Pcrit') 
                if p_crit < min_p_crit:
                    min_p_crit = p_crit
                    self.refrigerant = test_refrigerant
        else:
            if self.print_results: print(self.refrigerant)

        # Cycle calculation
        # Here the cycle points will be calculated. These points are:
        #  1. Compressor inlet
        #  2. Compressor outlet
        #  3. Expansion valve inlet
        #  4. Expansion valve outlet
        #  2-3 is the condenser where heat is expelled from the heat pump condenser to the heat sink or high temperature working fluid stream
        #  4-1 is the evaporator where heat is absorbed from the heat source or cold temperature working fluid to the heat pump evaporator

        self.refrigerant_high_temperature_kelvin = self.hot_temperature_desired + self.hot_buffer + 273.15
        self.refrigerant_low_temperature_kelvin = self.cold_temperature_available - self.cold_buffer + 273.15
        
        T_1 = 273.15+self.cold_temperature_available - self.cold_buffer
        T_3 = 273.15+self.hot_temperature_desired + self.hot_buffer

        # Calculating Cycle Parameters
        try:
            try:
                P_1 = PropsSI('P', 'T', T_1, 'Q', 1, self.refrigerant)
                S_1 = PropsSI('S', 'T', T_1, 'Q', 1, self.refrigerant)
                H_1 = PropsSI('H', 'T', T_1, 'Q', 1, self.refrigerant)

                P_3 = PropsSI('P', 'T', T_3, 'Q', 0, self.refrigerant)
                S_3 = PropsSI('S', 'T', T_3, 'Q', 0, self.refrigerant)
                H_3 = PropsSI('H', 'T', T_3, 'Q', 0, self.refrigerant)

                T_2 = PropsSI('T', 'S', S_1, 'P', P_3, self.refrigerant)
                H_2 = PropsSI('H', 'S', S_1, 'P', P_3, self.refrigerant)
                P_2 = P_3
            
            except:
                #print('The refrigerant previously selected went super critical or did not meet \nother parameters, for the purposes of the COP calculation the refrigerant \nwill be replaced with R245ca.')
                self.refrigerant = 'R245ca'
                P_1 = PropsSI('P', 'T', T_1, 'Q', 1, self.refrigerant)
                S_1 = PropsSI('S', 'T', T_1, 'Q', 1, self.refrigerant)
                H_1 = PropsSI('H', 'T', T_1, 'Q', 1, self.refrigerant)

                P_3 = PropsSI('P', 'T', T_3, 'Q', 0, self.refrigerant)
                S_3 = PropsSI('S', 'T', T_3, 'Q', 0, self.refrigerant)
                H_3 = PropsSI('H', 'T', T_3, 'Q', 0, self.refrigerant)

                T_2 = PropsSI('T', 'S', S_1, 'P', P_3, self.refrigerant)
                H_2 = PropsSI('H', 'S', S_1, 'P', P_3, self.refrigerant)
                P_2 = P_3
        
            PR = P_2/P_1
            # There is an efficiency associated with the pressure ratio and an efficiency association with the volume ratio
            # The VR is taken from experimental values which we do not fully have, so will integrate as part of year 2
            # For now the VR is set to a constant value.
            # The compressor efficiency can also be set by the user
            eta_pr = 0.95-0.01*PR
            eta_vr = 0.70
            if self.compressor_efficiency < 0.0:
                self.compressor_efficiency = round(eta_vr*eta_pr, 3)
            
        except:
            if self.print_results: print('Flag: A Carnot Efficiency Factor was used here as there was an error with the refrigerant selections')
            self.carnot_efficiency_factor_flag = True
            self.actual_COP = self.ideal_COP * self.carnot_efficiency_factor

        # if the User manually defines the carnot efficincy flag as true, then the calculation will always convert to this.
        if self.carnot_efficiency_factor_flag == True:
            self.actual_COP = self.ideal_COP * self.carnot_efficiency_factor
        else:
            if self.print_results: print('Estimated Compressor Efficiency:', round(eta_pr,2))
            #print('')
            #print('Warning: This program recommends a refrigerant for use. This recommendation is only a first step. \nRefrigerant selection should be further analyzed before implementation.')
            ## If no refrigerants are found, will use R245ca
            if len(self.refrigerant) > 0: 
                if self.print_results: print('Potential refigerants for this process include: ', self.refrigerant)
            else:
                self.refrigerant.append('R245ca')
                #print('Your process temperature was too high for known refrigerants, \nwill use R245ca for Analysis')
            if self.print_results: print('The recommended refrigerant for this process is: ', self.refrigerant)
            self.actual_COP = self.ideal_COP * self.compressor_efficiency

        
        self.ideal_COP = round(self.ideal_COP,2)
        self.actual_COP = round(self.actual_COP,2)
        if self.print_results: print('Calculate COP Called')
        if self.print_results: print('Theoretical COP: ', self.ideal_COP)
        if self.print_results: print('Estimated COP: ', self.actual_COP)

    ## Calculating working fluid energy and mass balance
    def calculate_energy_and_mass_flow(self):
        if self.print_results: print('Calculate Energy and Mass Called')

        # Converting MMBTU to kWh/hr (as it is expressed for the full hours of the year)
        for i in range(0,8760):
            self.process_heat_requirement_kw[i] = self.process_heat_requirement[i] * 1.055e6/3600

        # Calculating the Hot and Cold Mass Flow Parameters
        hot_dT = self.hot_temperature_desired - self.hot_temperature_minimum 
        cold_dT_array = [-1.0]*8760
        for i in range(0,8760):
            self.hot_mass_flowrate[i] = self.process_heat_requirement_kw[i]/(hot_dT*self.hot_specific_heat)/3600
            cold_dT_array[i] = self.process_heat_requirement_kw[i]/(self.cold_mass_flow[i]*self.cold_specific_heat)
    
        self.hot_mass_flowrate_average = round(np.average(self.hot_mass_flowrate),3)
        cold_dT_average = np.average(cold_dT_array)
        self.cold_final_temperature = round(self.cold_temperature_available - cold_dT_average,2)

        if self.print_results: 
            print('Hot Mass Flow Average: ', self.hot_mass_flowrate_average, ' kg/s')
            print('Cold Average Outlet Temperature: ', self.cold_final_temperature, '°C')

        # Calculating the Work into the heat pump
        for i in range(0,8760):
            self.power_in[i] = self.process_heat_requirement_kw[i]/self.actual_COP
        self.average_power_in = round(np.average(self.power_in),2)
        self.annual_energy_in = round(sum(self.power_in),1)

        if self.print_results: 
            print('Average Power Draw of Heat Pump: ', self.average_power_in, ' kW')
            print('Maximum Power Draw of Heat Pump: ', round(max(self.process_heat_requirement_kw)/self.actual_COP,1), ' kW')
            print('Annual Electricity in: ', self.annual_energy_in, 'kWh')

    ## Calculating Heat Pump Costs
    def calculate_heat_pump_costs(self):
        if self.print_results: print('Calculate Heat Pump Costs')
        # Heat pump costs are estimated based on the maximum electrical power in.
        #self.capital_cost = self.capital_cost_per_size * max(self.power_in)
        # Heat pump costs are estimated based on the maximum thermal power required in kW
        self.capital_cost = self.capital_cost_per_size * max(self.process_heat_requirement_kw)
        self.capital_cost = round(self.capital_cost,2)
        self.year_one_fixed_o_and_m = self.fixed_o_and_m_per_size*max(self.process_heat_requirement_kw)
        self.year_one_fixed_o_and_m = round(self.year_one_fixed_o_and_m,2)
        self.year_one_variable_o_and_m = self.variable_o_and_m_per_mmbtu*sum(self.process_heat_requirement)
        self.year_one_variable_o_and_m = round(self.year_one_variable_o_and_m,2)

        # Calculating the Capacity Factor
        for i in range(0,8760):
            self.capacity_factor[i] = self.process_heat_requirement_kw[i]/max(self.process_heat_requirement_kw)

        # Calculating the kWh costs
        kwh_costs = []
        for i in range(0,8760):
            kwh_costs.append(self.utility_rate_kwh[i]*self.power_in[i])
        kw_costs = 12*self.utility_rate_kw*max(self.process_heat_requirement)/self.actual_COP

        self.year_one_energy_costs = round(sum(kwh_costs)+kw_costs,2)
        self.year_one_operating_costs = self.year_one_fixed_o_and_m + self.year_one_variable_o_and_m + self.year_one_energy_costs
        self.year_one_operating_costs = round(self.year_one_operating_costs,2)

        self.LCOH = (self.capital_cost+ self.lifetime_yrs*self.year_one_operating_costs)/(self.lifetime_yrs*sum(self.process_heat_requirement))
        self.LCOH = round(self.LCOH,3)

        if self.print_results: 
            print('Capital Cost: $',self.capital_cost)
            print('One Year Fixed O&M Costs: $',self.year_one_fixed_o_and_m)
            print('One Year Variable O&M Costs: $',self.year_one_variable_o_and_m)
            print('One Year Energy Costs: $',self.year_one_energy_costs)
            print('One Year Operating Costs: $', self.year_one_operating_costs)
            print('Lifetime LCOH: ', self.LCOH, ' $/MMBTU')

    ## Calculating Natural Gas Prices (might remake to be a repeat of heat pump and make ubiquitous)
    def calculate_natural_gas_comparison(self):
        if self.print_results: print('Calculate Natural Gas Comparison')
        if self.existing_gas == True:
            self.gas_capital_cost = 0.0
        else:
            self.gas_capital_cost = self.gas_capital_cost_per_size * max(self.process_heat_requirement)/self.gas_efficiency
            self.gas_capital_cost = round(self.gas_capital_cost,2)
        self.gas_year_one_fixed_o_and_m = self.gas_fixed_o_and_m_per_size*max(self.process_heat_requirement)
        self.gas_year_one_fixed_o_and_m = round(self.gas_year_one_fixed_o_and_m,2)
        self.gas_year_one_variable_o_and_m = self.gas_variable_o_and_m_per_mmbtu*sum(self.process_heat_requirement)/self.gas_efficiency
        self.gas_year_one_variable_o_and_m = round(self.gas_year_one_variable_o_and_m,2)

        # Calculating Emissions
        # 1020 from 1 MMSCF/1020 MMBTU
        # 2000 form 1 ton/2000 lb
        # Calculated using EPA estimate: https://www.epa.gov/sites/production/files/2016-09/boilers_and_emergency_engines_pte_calculator_version_1.0.xlsx 
        self.gas_year_one_emissions = (sum(self.process_heat_requirement)/self.gas_efficiency) * self.gas_emissions_factor /(1020*2000)
        self.gas_year_one_cost_of_emissions =   round((self.carbon_price_per_ton * self.gas_year_one_emissions),2)

        costs = 0.0
        for i in range(0,8760):
            costs = costs + (self.gas_price_MMBTU[i]*self.process_heat_requirement[i])
        self.gas_year_one_energy_costs = round(costs,2)
        self.gas_year_one_operating_costs = self.gas_year_one_fixed_o_and_m + self.gas_year_one_variable_o_and_m + self.gas_year_one_energy_costs +self.gas_year_one_cost_of_emissions 
        self.gas_year_one_operating_costs = round(self.gas_year_one_operating_costs,2)

        self.gas_LCOH = (self.gas_capital_cost+ self.lifetime_yrs*self.gas_year_one_operating_costs)/(self.lifetime_yrs*sum(self.process_heat_requirement))
        self.gas_LCOH = round(self.gas_LCOH,3)

        if self.print_results: 
            print('Gas Capital Cost: $',self.gas_capital_cost)
            print('Gas One Year Fixed O&M Costs: $',self.gas_year_one_fixed_o_and_m)
            print('Gas One Year Variable O&M Costs: $',self.gas_year_one_variable_o_and_m)
            print('Gas One Year Energy Costs: $',self.gas_year_one_energy_costs)
            print('Gas One Year Operating Costs: $', self.gas_year_one_operating_costs)
            print('Gas Lifetime LCOH: ', self.gas_LCOH, ' $/MMBTU')

    def calculate_cash_flow(self):  
        if self.print_results: print('Calculate Cash Flow')
        # Compare to a new build natural gas plant
        annual_cashflow = []
        # If true, the full cost of the heat pump is included, if false, than 
        # the cost of the natural gas plant is subtracted from the capital cost of the heat pump to compare.
        if self.existing_gas == True:
            annual_cashflow.append(-1*(self.capital_cost))
        else:
            annual_cashflow.append(-1*(self.capital_cost - self.gas_capital_cost))
        
        # The Cashflow model is always the cost saved by using the heat pump. 
        # The price of carbon is included in the cost of the natural gas plant.
        for i in range(1, int(self.lifetime_yrs+1)):
            gas_CAGR_energy_costs = self.gas_year_one_energy_costs*math.e**(i*math.log(1+self.gas_CAGR))
            kwh_CAGR_energy_costs = self.year_one_energy_costs*math.e**(i*math.log(1+self.kwh_CAGR))
            annual_gas_operating_cost = self.gas_year_one_fixed_o_and_m + self.gas_year_one_variable_o_and_m + self.gas_year_one_cost_of_emissions + gas_CAGR_energy_costs
            annual_kwh_operating_cost = self.year_one_fixed_o_and_m + self.year_one_variable_o_and_m + kwh_CAGR_energy_costs
            annual_cashflow.append(annual_gas_operating_cost - annual_kwh_operating_cost)
            #print(i, 'gas', gas_CAGR_energy_costs, 'total', annual_gas_operating_cost)

        # Calculating and outputting
        self.net_present_value = round(npf.npv(self.discount_rate, annual_cashflow),2)
        if self.print_results: print('NPV: $', self.net_present_value)
        self.internal_rate_of_return = round(npf.irr(annual_cashflow),3)*100
        if self.print_results: print('IRR: ',round(self.internal_rate_of_return,2), '%')
        # Need to calcuate year 1 energy Savings
        try:
            self.payback_period = math.log(1/(1-(self.capital_cost-self.gas_capital_cost)*self.discount_rate/annual_cashflow[1]))/math.log(1+self.discount_rate)
            if self.print_results: print('PBP: ', round(self.payback_period,2))
        except:
            self.payback_period = 'NA'
            if self.print_results: print('PBP: ', self.payback_period)
        
    def write_output(self, filename):
        data = [
            ['Cold Temperature Available (C)',self.cold_temperature_available],
            ['Cold Temperature Final (C)',self.cold_final_temperature],
            ['Cold Mass Flowrate (kg/s)', np.average(self.cold_mass_flow)],
            ['Hot Temperature Desired (C)', self.hot_temperature_desired],
            ['Hot Temperature Minimum (C)', self.hot_temperature_minimum],
            ['Hot Mass Flowrate (kg/s)', self.hot_mass_flowrate_average],
            ['Ideal COP Calculated', self.ideal_COP],
            ['Selected Refrigerant', self.refrigerant],
            ['Estimated Compressor Efficiency', self.compressor_efficiency],
            ['Carnot Efficiency Factor', self.carnot_efficiency_factor],
            ['Carnot Efficiency Factor Flag', self.carnot_efficiency_factor_flag],
            ['Actual COP Calculated',self.actual_COP],
            ['Process Heat Average (MMBTu)', np.average(self.process_heat_requirement)],
            ['Process Heat Average (kW)', np.average(self.process_heat_requirement_kw)],
            ['Utility Rate Average ($/kWh)', np.average(self.utility_rate_kwh)],
            ['Capacity Factor', np.average(self.capacity_factor)],
            ['Project Lifetime', self.lifetime_yrs],
            ['HP Power in Average (kW)',self.average_power_in],
            ['HP Annual Energy In (kWh)', self.annual_energy_in],
            ['HP Capital Cost Per Unit ($/MMBTU/hr)', self.capital_cost_per_size],
            ['HP Fixed O&M Costs ($/MMBTU/hr/yr)', self.fixed_o_and_m_per_size],
            ['HP Variable O&M Costs ($/MMBTU)', self.variable_o_and_m_per_mmbtu],
            ['HP Capital Cost ($)',self.capital_cost],
            ['HP Year One Energy Costs ($)',self.year_one_energy_costs],
            ['HP Year One Fixed O&M Costs ($)', self.year_one_fixed_o_and_m],
            ['HP Year One Variable O&M Costs ($)', self.year_one_variable_o_and_m],
            ['HP Year One Total Operating Costs ($)', self.year_one_operating_costs],
            ['HP LCOH ($/MMBTU)', self.LCOH],
            ['Gas Capital Cost Per Unit ($/MMBTU/hr)', self.gas_capital_cost_per_size],
            ['Gas Fixed O&M Costs ($/MMBTU/hr/yr)', self.gas_fixed_o_and_m_per_size],
            ['Gas Variable O&M Costs ($/MMBTU)', self.gas_variable_o_and_m_per_mmbtu],
            ['Gas Average Price ($/MMBTU)', np.average(self.gas_price_MMBTU)],
            ['Gas Capital Cost ($)', self.gas_capital_cost],
            ['Gas Year One Energy Costs ($)',self.gas_year_one_energy_costs],
            ['Gas Year One Fixed O&M Costs ($)', self.gas_year_one_fixed_o_and_m],
            ['Gas Year One Variable O&M Costs ($)', self.gas_year_one_variable_o_and_m],
            ['Gas Year One Total Operating Costs ($)', self.gas_year_one_operating_costs],
            ['Gas LCOH ($/MMBTU)', self.gas_LCOH],
            ['Gas Emissions',self.gas_year_one_emissions],
            ['Gas Social Cost of Emissions', self.gas_year_one_cost_of_emissions],
            ['Net Present Value', self.net_present_value],
            ['Internal Rate of Return pct', self.internal_rate_of_return],
            ['Payback Period', self.payback_period]
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


