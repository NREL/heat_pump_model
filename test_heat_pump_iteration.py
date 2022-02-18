from heat_pump_model import heat_pump
import numpy as np
from utilities.unit_defs import Q_

from libraries import * 

sector = 'dairy'
for j in process:
    for i in process[j]:
        values = process[j][i]
        print(values)
        test_heat_pump = heat_pump()
        test_heat_pump.gas_price_MMBTU = Q_(np.array([1.8] * 8760), 'USD/MMBtu')
        test_heat_pump.initialize_heat_pump(j,i)
        test_heat_pump.run_all(i)

for i in range(40,51):
    test_heat_pump = heat_pump()
    test_heat_pump.initialize_heat_pump(sector, 'pasteurization_low')
    test_heat_pump.carnot_efficiency_factor = Q_(i/100, 'dimensionless')
    test_heat_pump.carnot_efficiency_factor_flag = True
    test_heat_pump.run_all('pasteurization_low_COP_'+str(i))