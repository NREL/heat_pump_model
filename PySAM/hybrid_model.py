from PySSC import PySSC
from heat_pump_model import heat_pump
import csv
from libraries import * 


def swh(inputs_dict, outputs_dict):
    ssc = PySSC()
    ssc.module_exec_set_print(0)
    data = ssc.data_create()

    # FPC Performance
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

    # LCOE Performance
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

    # Getting single values
    outputs_dict['annual_energy'] = ssc.data_get_number(data, b'annual_energy')
    outputs_dict['solar_fraction'] = ssc.data_get_number(data, b'solar_fraction')
    outputs_dict['annual_Q_aux'] = ssc.data_get_number(data, b'annual_Q_aux')
    outputs_dict['annual_Q_aux_only'] = ssc.data_get_number(data, b'annual_Q_auxonly')
    outputs_dict['capacity_factor'] = ssc.data_get_number(data, b'capacity_factor')

    # Getting arrays
    outputs_dict['t_delivered'] = ssc.data_get_array(data, b'T_deliv')
    outputs_dict['v_cold'] = ssc.data_get_array(data, b'V_cold')
    outputs_dict['v_hot'] = ssc.data_get_array(data, b'V_hot')
    outputs_dict['q_aux'] = ssc.data_get_array(data, b'Q_aux')
    outputs_dict['q_auxonly'] = ssc.data_get_array(data, b'Q_auxonly')
    outputs_dict['q_deliv'] = ssc.data_get_array(data, b'Q_deliv')
    #outputs_dict['']




inputs = {
    'test':1,
    'blank':2
}
outputs = {}

swh(inputs, outputs)

print(outputs['annual_energy'])
#print(outputs['Q_aux'])
























