
import math
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

import CoolProp
from CoolProp.CoolProp import PropsSI 
from CoolProp.Plots import PropertyPlot
from CoolProp.Plots import SimpleCompressionCycle

ref_list = ['Ammonia','R1336MZ', 'Methanol', 'R245', 'R1234ze','R1234ze2', 'R1233zd']
ref_list = ['Ammonia', 'CarbonDioxide', 'Ethanol', 'Methanol', 'R1234ze(E)', 'R1234ze(Z)', 'R245ca', 'R245fa', 'n-Pentane']
ref_list = ['R290', 'R601', 'R717', 'R1234yf']
ref_list = [
    'Ammonia', 'Butane', 'CarbonDioxide', 'Ethanol', 'Ethylene', 'HFE143m', 'Methanol', 'Nitrogen', 
    'R11', 'R113','R114','R115','R115', 'R12','R123', 'R1233zd(E)','R1234yf', 'R1234ze(E)', 
    'R1234ze(Z)', 'R124', 'R1243zf','R125','R13','R134a','R13I1', 'R14', 'R141b', 'R142b', 
    'R143a', 'R152A', 'R161', 'R21', 'R218', 'R22', 'R227EA', 'R23', 'R236EA', 'R236FA', 
    'R245ca', 'R245fa', 'R32', 'R365MFC', 'R40', 'R404A', 'R407C', 'R41', 'R410A', 'R507A',
    'RC318', 'n-Pentane', 'Water'
]

'''ref_list = [
    'Ammonia', 'CarbonDioxide', 'Ethanol', 'Ethylene', 'HFE143m', 'Methanol', 'Nitrogen', 
    'R11', 'R113','R114','R115','R115', 'R12','R123', 'R1233zd(E)','R1234yf', 'R1234ze(E)', 
    'R1234ze(Z)', 'R124', 'R1243zf','R125','R13','R134a','R13I1', 'R14', 'R141b', 'R142b', 
    'R143a', 'R152A', 'R161', 'R21', 'R218', 'R22', 'R227EA', 'R23', 'R236EA', 'R236FA', 
    'R245ca', 'R245fa', 'R32', 'R365MFC', 'R40', 'R404A', 'R407C', 'R41', 'R410A', 'R507A',
    'RC318', 'n-Butane'
]'''

def print_critical_point():
    for fluid in ref_list:
        print(fluid, ': Critical Temp', round(PropsSI(fluid, 'Tcrit')-273.15,2), '°C Critical Press ',round(PropsSI(fluid, 'Pcrit')/1E6,2), ' MPA')

def plot_water():
    fluid = 'Water'
    plot = PropertyPlot(fluid,'Ts', tp_limits='ORC')
    plot.calc_isolines(CoolProp.iQ, num = 2)
    plot.calc_isolines(CoolProp.iP, num = 6)
    plot.show()
    plot.savefig('output/'+fluid+'_TS_plot.png')

def plot_saturation_curve(fluid):
    # Specifying resolution for curve (number of points to collect)
    n = 500

    # Getting critical T, P, and S for 
    t_crit = PropsSI(fluid, 'Tcrit') 
    p_crit = PropsSI(fluid, 'Pcrit') 
    s_crit = PropsSI('S', 'T', t_crit, 'Q', 1, fluid)
    
    t_min = math.ceil(PropsSI(fluid, 'Tmin'))
    t_max = (math.floor(PropsSI(fluid, 'Tcrit')*1E5)/1E5)
    dt = (t_max-t_min)/float(n)

    df = pd.DataFrame(0.0, index=range(2*n), columns = ['S', 'T', 'T_C'])

    for i in range(n):
        df.loc[i,'T'] = t_min+i*dt
        df.loc[i,'S'] = PropsSI('S', 'T', df.loc[i,'T'], 'Q', 0, fluid)
        df.loc[i, 'T_C'] = df.loc[i,'T']-273.15

    for i in range(n,2*n):
        df.loc[i,'T'] = t_max - (i-n)*dt
        df.loc[i,'S'] = PropsSI('S', 'T', df.loc[i,'T'], 'Q', 1, fluid)
        df.loc[i, 'T_C'] = df.loc[i,'T']-273.15

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['S'], 
        y=df['T_C'],
        mode='lines',
        name=fluid+' Saturation Curve',
        line_color = 'black',
        showlegend = False
    ))

    ## Double Check Enthalpy Units
    fig.update_xaxes(title = 'Specific Entropy (kJ/kg)')
    fig.update_yaxes(title = 'Temperature (°C)')
    fig.update_layout(height = 800, width = 800, template = 'simple_white', title = fluid+' Saturation Curve')
    fig.show()
    fig.write_image('output/'+fluid+'.png')

    return 

# Currently plot_cycle is mostly a repeat of the saturation curve. Would like to combine into one routine or call the
# plot_saturation_curve routine from within plot_cycle so there is less code duplication, but will have update later
def plot_cycle(cold_T, hot_T, fluid):

    ## Getting Data for Saturation Curve
    # Specifying resolution for curve (number of points to collect)
    n = 500
    # Getting critical T, P, and S for 
    t_crit = PropsSI(fluid, 'Tcrit') 
    p_crit = PropsSI(fluid, 'Pcrit') 
    s_crit = PropsSI('S', 'T', t_crit, 'Q', 1, fluid)
    
    t_min = math.ceil(PropsSI(fluid, 'Tmin'))
    t_max = (math.floor(PropsSI(fluid, 'Tcrit')*1E5)/1E5)
    dt = (t_max-t_min)/float(n)
    df = pd.DataFrame(0.0, index=range(2*n), columns = ['S', 'T', 'T_C'])

    for i in range(n):
        df.loc[i,'T'] = t_min+i*dt
        df.loc[i,'S'] = PropsSI('S', 'T', df.loc[i,'T'], 'Q', 0, fluid)
        df.loc[i, 'T_C'] = df.loc[i,'T']-273.15

    for i in range(n,2*n):
        df.loc[i,'T'] = t_max - (i-n)*dt
        df.loc[i,'S'] = PropsSI('S', 'T', df.loc[i,'T'], 'Q', 1, fluid)
        df.loc[i, 'T_C'] = df.loc[i,'T']-273.15

    ## Getting Data for Cycle
    T_1 = cold_T+273.15
    T_2 = hot_T+273.15
    T_4 = T_1

    ## Calculating points around the curve
    S_1 = PropsSI('S', 'T', T_1, 'Q', 1, fluid)
    S_2 = S_1
    P_2 = PropsSI('P', 'T', T_2, 'S', S_2, fluid)
    T_3 = PropsSI('T', 'P', P_2, 'Q', 0, fluid)
    S_3 = PropsSI('S', 'P', P_2, 'Q', 0, fluid)
    # These Enthalpies rely on the above calculated points
    H_3 = PropsSI('H', 'P', P_2, 'Q', 0, fluid)
    H_4 = H_3
    P_1 = PropsSI('P', 'T', T_1, 'Q', 1, fluid)
    P_4 = P_1
    # Assume isentropic expansion here but not actually, PropsSI just doesn't support calc that I know of.
    # Should involve another PropSI call but unclear on how that is done as of now.
    S_4 = S_3 
    # Creating artifical point for T_2a to create line between T_2 and saturation curve
    T_2a = T_3
    S_2a = PropsSI('S', 'T', T_2a, 'Q', 1, fluid)

    # Putting points into an array for plotting
    # Make sure to repeat last point to complete the 'box'
    s_array = [S_1, S_2, S_2a, S_3, S_4, S_1]
    t_array = [T_1-273.15, T_2-273.15, T_2a-273.15, T_3-273.15, T_4-273.15, T_1-273.15]

    fig = go.Figure()
    # Plotting the T-S diagram
    fig.add_trace(go.Scatter(
        x=df['S'], 
        y=df['T_C'],
        mode='lines',
        name=fluid+' Saturation Curve',
        line_color = 'black',
        showlegend = False
    ))

    fig.add_trace(go.Scatter(
        x = s_array,
        y = t_array, 
        mode = 'markers+lines',
        name = 'Compression Cycle',
        marker_color = 'firebrick',
        showlegend = True
    ))

    ## Double Check Enthalpy Units
    fig.update_xaxes(title = 'Specific Entropy (kJ/kg)')
    fig.update_yaxes(title = 'Temperature (°C)')
    fig.update_layout(height = 800, width = 800, template = 'simple_white', title = fluid+' Saturation Curve')
    fig.show()
    fig.write_image('output/'+fluid+'.png')


