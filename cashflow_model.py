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

def calculate_cash_flow(dict1, dict2, project_lifetime, discount_rate):
    # dict1 and dict2 are the costs. dict1 should be the baseline costs while dict1 is the 
    # upgraded costs. The objects will be responsible for returning the dictionary. 

    # Setting up the annual cashflow list
    annual_cashflow = []

    # Here the capital costs are appended
    annual_cashflow.append(dict1['capital_cost']-dict2['capital_cost'])

    for i in range(1, project_lifetime):
        # Getting adjusted energy prices
        dict1_CAGR_energy_costs = dict1['year_one_energy_cost']*math.e**(i*math.log(1+dict1['CAGR']))
        dict2_CAGR_energy_costs = dict2['year_one_energy_cost']*math.e**(i*math.log(1+dict2['CAGR']))

        # Getting operating costs
        dict1_operating_costs = dict1['year_one_fixed_o_and_m'] + dict1['year_one_variable_o_and_m'] + dict1['year_one_cost_of_emissions'] + dict1_CAGR_energy_costs
        dict2_operating_costs = dict2['year_one_fixed_o_and_m'] + dict2['year_one_variable_o_and_m'] + dict2['year_one_cost_of_emissions'] + dict2_CAGR_energy_costs

        # Appending to the annual cashflow
        annual_cashflow.append(dict1_operating_costs-dict2_operating_costs)
    
    net_present_value = Q_(npf.npv(discount_rate, annual_cashflow), 'USD')
    print('NPV: {:,~.2fP}'.format(net_present_value))

    if net_present_value.m > 0.0:
        internal_rate_of_return = Q_(npf.irr(annual_cashflow), 'dimensionless').to('pct')
        payback_period          = math.log(1/(1-(annual_cashflow[0])*discount_rate/annual_cashflow[1]))/math.log(1+discount_rate)
    else:
        internal_rate_of_return = 'NA'
        payback_period          = 'NA'


    print('IRR: ', internal_rate_of_return)
    print('PBP: ', payback_period)


