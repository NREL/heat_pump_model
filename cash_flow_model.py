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

def calculate_cash_flow_v2(self, discount rate, annual_cashflow_system_1, annual_cashflow_system_2):
    #annual_cashflow_system_1 = []
    #annual_cashflow_system_2 = []
    annual_cashflow = annual_cashflow_system_1 - annual_cashflow_system_2

    self.net_present_value = Q_('0.0 USD')
    self.internal_rate_of_return = Q_('-1.0')
    self.payback_period = Q_('100.0 yr')


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