from PySSC import PySSC
from heat_pump_model import heat_pump
from libraries import * 

if __name__ == "__main__":
	ssc = PySSC()
	print ('Current folder = /Users/jcox/Desktop/PySAM')
	print ('SSC Version = ', ssc.version())
	print ('SSC Build Information = ', ssc.build_info().decode("utf - 8"))
	ssc.module_exec_set_print(0)
	data = ssc.data_create()
	ssc.data_set_string( data, b'solar_resource_file', b'/Users/jcox/Desktop/PySAM/weather_files/denver_co_39.738453_-104.984853_psm3-tmy_60_tmy.csv' );
	ssc.data_set_array_from_csv( data, b'scaled_draw', b'/Users/jcox/Desktop/PySAM/scaled_draw.csv');
	ssc.data_set_number( data, b'system_capacity', 3.4180600643157959 )
	ssc.data_set_number( data, b'tilt', 30 )
	ssc.data_set_number( data, b'azimuth', 180 )
	ssc.data_set_number( data, b'albedo', 0.20000000000000001 )
	ssc.data_set_number( data, b'irrad_mode', 0 )
	ssc.data_set_number( data, b'sky_model', 0 )
	ssc.data_set_number( data, b'mdot', 0.091055999999999998 )
	ssc.data_set_number( data, b'ncoll', 2 )
	ssc.data_set_number( data, b'fluid', 1 )
	ssc.data_set_number( data, b'area_coll', 2.9800000190734863 )
	ssc.data_set_number( data, b'FRta', 0.68900001049041748 )
	ssc.data_set_number( data, b'FRUL', 3.8499999046325684 )
	ssc.data_set_number( data, b'iam', 0.20000000298023224 )
	ssc.data_set_number( data, b'test_fluid', 1 )
	ssc.data_set_number( data, b'test_flow', 0.045527998358011246 )
	ssc.data_set_number( data, b'pipe_length', 10 )
	ssc.data_set_number( data, b'pipe_diam', 0.019 )
	ssc.data_set_number( data, b'pipe_k', 0.029999999999999999 )
	ssc.data_set_number( data, b'pipe_insul', 0.0060000000000000001 )
	ssc.data_set_number( data, b'tank_h2d_ratio', 2 )
	ssc.data_set_number( data, b'U_tank', 1 )
	ssc.data_set_number( data, b'V_tank', 0.29999999999999999 )
	ssc.data_set_number( data, b'hx_eff', 0.75 )
	ssc.data_set_number( data, b'T_room', 20 )
	ssc.data_set_number( data, b'T_tank_max', 99 )
	ssc.data_set_number( data, b'T_set', 55 )
	ssc.data_set_number( data, b'pump_power', 45 )
	ssc.data_set_number( data, b'pump_eff', 0.84999999999999998 )
	ssc.data_set_number( data, b'use_custom_mains', 0 )
	ssc.data_set_array_from_csv( data, b'custom_mains', b'/Users/jcox/Desktop/PySAM/custom_mains.csv');
	ssc.data_set_number( data, b'use_custom_set', 0 )
	ssc.data_set_array_from_csv( data, b'custom_set', b'/Users/jcox/Desktop/PySAM/custom_set.csv');
	ssc.data_set_number( data, b'adjust:constant', 0 )
	module = ssc.module_create(b'swh')	
	ssc.module_exec_set_print( 0 );
	if ssc.module_exec(module, data) == 0:
		print ('swh simulation error')
		idx = 1
		msg = ssc.module_log(module, 0)
		while (msg != None):
			print ('	: ' + msg.decode("utf - 8"))
			msg = ssc.module_log(module, idx)
			idx = idx + 1
		SystemExit( "Simulation Error" );
	ssc.module_free(module)
	ssc.data_set_number( data, b'capital_cost', 13672.240234375 )
	ssc.data_set_number( data, b'fixed_operating_cost', 170.90299987792969 )
	ssc.data_set_number( data, b'variable_operating_cost', 0 )
	ssc.data_set_number( data, b'fixed_charge_rate', 0.097999997437000275 )
	module = ssc.module_create(b'lcoefcr')	
	ssc.module_exec_set_print( 0 );
	if ssc.module_exec(module, data) == 0:
		print ('lcoefcr simulation error')
		idx = 1
		msg = ssc.module_log(module, 0)
		while (msg != None):
			print ('	: ' + msg.decode("utf - 8"))
			msg = ssc.module_log(module, idx)
			idx = idx + 1
		SystemExit( "Simulation Error" );
	ssc.module_free(module)
	
	annual_energy = ssc.data_get_number(data, b'annual_energy');
	print ('Annual energy saved (year 1) = ', annual_energy)
	solar_fraction = ssc.data_get_number(data, b'solar_fraction');
	print ('Solar fraction (year 1) = ', solar_fraction)
	annual_Q_aux = ssc.data_get_number(data, b'annual_Q_aux');
	print ('Aux with solar (year 1) = ', annual_Q_aux)
	annual_Q_auxonly = ssc.data_get_number(data, b'annual_Q_auxonly');
	print ('Aux without solar (year 1) = ', annual_Q_auxonly)
	capacity_factor = ssc.data_get_number(data, b'capacity_factor');
	
	lcoe_fcr = ssc.data_get_number(data, b'lcoe_fcr');
	
	t_delivered = ssc.data_get_array(data, b'T_deliv');
	v_cold = ssc.data_get_array(data, b'V_cold');
	v_hot = ssc.data_get_array(data, b'V_hot');

	print()
	print('Average Delivered Temperature, ', round(sum(t_delivered)/len(t_delivered),2))
	print ('Capacity factor (year 1) = ', round(capacity_factor,2))
	print('Levelized cost of energy = ', round(lcoe_fcr,2))
	#print('Cold Volume = ', v_cold)
	#print('Hot Volume =',v_hot)
	t_average = sum(t_delivered)/len(t_delivered)
	print()
	ssc.data_free(data);

	hp_test = heat_pump()
	hp_test.hot_temperature_desired = 90
	hp_test.hot_temperature_minimum = 80
	hp_test.cold_temperature_available = t_average
	hp_test.gas_price_MMBTU = [3.5] * 8760 
	hp_test.carnot_efficiency_factor = 0.45
	hp_test.carnot_efficiency_factor_flag = False

	#hp_test.compressor_efficiency = 0.65

	hp_test.calculate_COP()
	#hp_test.carnot_efficiency_factor = 0.4
	#hp_test.calculate_COP()
	hp_test.calculate_energy_and_mass_flow()
	hp_test.calculate_heat_pump_costs()
	
	print()
	print('Estimated LCOH with Solar Heater ', round(hp_test.LCOH+lcoe_fcr*293,3), ' $/MMBTU')
	print()