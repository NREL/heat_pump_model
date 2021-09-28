from CoolProp.CoolProp import PropsSI 
from CoolProp.Plots import PropertyPlot

print('')

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


for fluid in ref_list:
    print(fluid, ': Critical Temp', round(PropsSI(fluid, 'Tcrit'),2), '°C Critical Press ',round(PropsSI(fluid, 'Pcrit')/1000,2), ' MPA')

print('')

fluid = 'R1243zf'
plot = PropertyPlot(fluid, 'TS')
#plot.show()
#print(PropsSI('H','T',180, 'P',5000, 'Ammonia'))
