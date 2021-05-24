working_fluid = {
    'air': {'specific_heat': 1.009, 'density': 1.225}, 
    'ammonia': {'specific_heat': 2.175, 'density': 0.699},
    'water': {'specific_heat': 4.184, 'density': 1000},
}

# Process Library
process = {
    'dairy':{
        'pasteurization_low':   {'hot_working_fluid':'water',   'hot_temperature_desired': 80,     'hot_temperature_minimum': 75,  'waste_temperature': 50},
        'pasteurization_high':  {'hot_working_fluid':'water',   'hot_temperature_desired': 90,     'hot_temperature_minimum': 85,  'waste_temperature': 50},
        'concentrating':        {'hot_working_fluid':'water',   'hot_temperature_desired': 70,     'hot_temperature_minimum': 60,  'waste_temperature': 50},
        'yogurt':               {'hot_working_fluid':'water',   'hot_temperature_desired': 95,     'hot_temperature_minimum': 90,  'waste_temperature': 50},
        'water_heating':        {'hot_working_fluid':'water',   'hot_temperature_desired': 55,     'hot_temperature_minimum': 50,  'waste_temperature': 15},
        'cleaning':             {'hot_working_fluid':'water',   'hot_temperature_desired': 85,     'hot_temperature_minimum': 60,  'waste_temperature': 15}
    },
    'food_and_beverage':{
        'blanching':            {'hot_working_fluid':'water',   'hot_temperature_desired': 95,     'hot_temperature_minimum': 60,  'waste_temperature': 50},
        'scalding':             {'hot_working_fluid':'water',   'hot_temperature_desired': 90,     'hot_temperature_minimum': 45,  'waste_temperature': 15},
        'evaporating':          {'hot_working_fluid':'air',     'hot_temperature_desired': 130,    'hot_temperature_minimum': 40,  'waste_temperature': 15},
        'cooking':              {'hot_working_fluid':'air',     'hot_temperature_desired': 120,    'hot_temperature_minimum': 70,  'waste_temperature': 50},
        'smoking':              {'hot_working_fluid':'air',     'hot_temperature_desired': 85,     'hot_temperature_minimum': 20,  'waste_temperature': 15},
        'cleaning':             {'hot_working_fluid':'water',   'hot_temperature_desired': 90,     'hot_temperature_minimum': 60,  'waste_temperature': 50},
        'sterilization':        {'hot_working_fluid':'water',   'hot_temperature_desired': 140,    'hot_temperature_minimum': 100, 'waste_temperature': 50},
        'tempering':            {'hot_working_fluid':'water',   'hot_temperature_desired': 80,     'hot_temperature_minimum': 40,  'waste_temperature': 15},
        'drying':               {'hot_working_fluid':'air',     'hot_temperature_desired': 200,    'hot_temperature_minimum': 40,  'waste_temperature': 15},
        'washing':              {'hot_working_fluid':'water',   'hot_temperature_desired': 80,     'hot_temperature_minimum': 35,  'waste_temperature': 15}
    },
    'chemicals':{
        'bio_reactor':          {'hot_working_fluid':'water',   'hot_temperature_desired': 55,     'hot_temperature_minimum': 25,  'waste_temperature': 15},
        'distillation':         {'hot_working_fluid':'air',     'hot_temperature_desired': 200,    'hot_temperature_minimum': 100, 'waste_temperature': 50},
        'compression':          {'hot_working_fluid':'air',     'hot_temperature_desired': 170,    'hot_temperature_minimum': 110, 'waste_temperature': 50},
        'cooking':              {'hot_working_fluid':'air',     'hot_temperature_desired': 110,    'hot_temperature_minimum': 85,  'waste_temperature': 50},
        'thickening':           {'hot_working_fluid':'air',     'hot_temperature_desired': 140,    'hot_temperature_minimum': 130, 'waste_temperature': 50}
    },
    'paper': {
        'bleahing':             {'hot_working_fluid':'water',   'hot_temperature_desired': 150,    'hot_temperature_minimum': 40,  'waste_temperature': 15},
        'de_inking':            {'hot_working_fluid':'water',   'hot_temperature_desired': 70,     'hot_temperature_minimum': 50,  'waste_temperature': 15},
        'cooking':              {'hot_working_fluid':'water',   'hot_temperature_desired': 180,    'hot_temperature_minimum': 110, 'waste_temperature': 50},
        'drying':               {'hot_working_fluid':'water',   'hot_temperature_desired': 200,    'hot_temperature_minimum': 95,  'waste_temperature': 50}
    },
    'metal':{
        'pickling':             {'hot_working_fluid':'water',   'hot_temperature_desired': 100,    'hot_temperature_minimum': 20,  'waste_temperature': 15},
        'chromating':           {'hot_working_fluid':'water',   'hot_temperature_desired': 75,     'hot_temperature_minimum': 20,  'waste_temperature': 15},
        'degreasing':           {'hot_working_fluid':'water',   'hot_temperature_desired': 100,    'hot_temperature_minimum': 20,  'waste_temperature': 15},
        'electroplating':       {'hot_working_fluid':'air',     'hot_temperature_desired': 95,     'hot_temperature_minimum': 30,  'waste_temperature': 15},
        'phosphating':          {'hot_working_fluid':'air',     'hot_temperature_desired': 95,     'hot_temperature_minimum': 35,  'waste_temperature': 15},
        'purging':              {'hot_working_fluid':'air',     'hot_temperature_desired': 70,     'hot_temperature_minimum': 40,  'waste_temperature': 15},
        'drying':               {'hot_working_fluid':'air',     'hot_temperature_desired': 200,    'hot_temperature_minimum': 60,  'waste_temperature': 50}
    },
    'textiles':{
        'bleaching':            {'hot_working_fluid':'water',   'hot_temperature_desired': 100,    'hot_temperature_minimum': 40,  'waste_temperature': 15},
        'coloring':             {'hot_working_fluid':'water',   'hot_temperature_desired': 130,    'hot_temperature_minimum': 40,  'waste_temperature': 15},
        'drying':               {'hot_working_fluid':'air',     'hot_temperature_desired': 105,    'hot_temperature_minimum': 60,  'waste_temperature': 50},
        'washing':              {'hot_working_fluid':'water',   'hot_temperature_desired': 100,    'hot_temperature_minimum': 50,  'waste_temperature': 15}
    },
    'wood':{
        'steaming':             {'hot_working_fluid':'water',   'hot_temperature_desired': 95,     'hot_temperature_minimum': 75,  'waste_temperature': 50},
        'pickiling':            {'hot_working_fluid':'water',   'hot_temperature_desired': 70,     'hot_temperature_minimum': 40,  'waste_temperature': 15},
        'compression':          {'hot_working_fluid':'air',     'hot_temperature_desired': 170,    'hot_temperature_minimum': 120, 'waste_temperature': 50},
        'cooking':              {'hot_working_fluid':'air',     'hot_temperature_desired': 90,     'hot_temperature_minimum': 80,  'waste_temperature': 50},
        'drying':               {'hot_working_fluid':'air',     'hot_temperature_desired': 150,    'hot_temperature_minimum': 40,  'waste_temperature': 15}
    },
    'misc':{
        'plastic_drying':       {'hot_working_fluid':'air',     'hot_temperature_desired': 150,    'hot_temperature_minimum': 50,  'waste_temperature': 15},
        'plastic_preheating':   {'hot_working_fluid':'air',     'hot_temperature_desired': 70,     'hot_temperature_minimum': 50,  'waste_temperature': 15},
        'surface_treatment':    {'hot_working_fluid':'air',     'hot_temperature_desired': 130,    'hot_temperature_minimum': 20,  'waste_temperature': 15},
        'cleaning':             {'hot_working_fluid':'water',   'hot_temperature_desired': 90,     'hot_temperature_minimum': 40,  'waste_temperature': 15}
    },
    'beer_brewing':{
        'boiling':              {'hot_working_fluid':'water',   'hot_temperature_desired': 110,    'hot_temperature_minimum': 100, 'waste_temperature': 50},
        'cleaning':             {'hot_working_fluid':'water',   'hot_temperature_desired': 90,     'hot_temperature_minimum': 80,  'waste_temperature': 50},
        'pasteurization':       {'hot_working_fluid':'water',   'hot_temperature_desired': 80,     'hot_temperature_minimum': 72,  'waste_temperature': 50},
    }

}

# Here all refrigerants that may be relevant are stored. Each of these could be used to conduct analysis.
refrigerant_all = [
    'Ammonia', 'Butane', 'CarbonDioxide', 'Ethanol', 'Ethylene', 'HFE143m', 'Methanol', 'Nitrogen', 
    'R11', 'R113','R114','R115','R115', 'R12','R123', 'R1233zd(E)','R1234yf', 'R1234ze(E)', 
    'R1234ze(Z)', 'R124', 'R1243zf','R125','R13','R134a','R13I1', 'R14', 'R141b', 'R142b', 
    'R143a', 'R152A', 'R161', 'R21', 'R218', 'R22', 'R227EA', 'R23', 'R236EA', 'R236FA', 
    'R245ca', 'R245fa', 'R32', 'R365MFC', 'R40', 'R404A', 'R407C', 'R41', 'R410A', 'R507A',
    'RC318', 'n-Pentane', 'Water'
]

# Based on research and interviews, this short list is the list the model pulls from by default to perform analysis.
refrigerants = ['Ammonia', 'CarbonDioxide', 'Ethanol', 'Methanol', 'R1234ze(E)', 'R1234ze(Z)', 'R245ca', 'R245fa', 'n-Pentane']
refrigerants = refrigerant_all

# Compressor efficiency is currently not fully utilizied. Will require additional code development.
compressors = {
    'Piston': {'Isentropic_Efficiency': 0.7, 'load_coefficient':0.55},
    'Screw': {'Isentropic_Efficiency': 0.5, 'load_coefficient':0.55},
    'Twin_Screw': {'Isentropic_Efficiency': 0.55, 'load_coefficient':0.55},
    'Scroll': {'Isentropic_Efficiency': 0.55, 'load_coefficient':0.55},
    'Turbo': {'Isentropic_Efficiency': 0.55, 'load_coefficient':0.55}
}

# Volumetric efficiency
# Comes from compressor manufacturer
# 15-20 years lifespan
# German association of engineers suggests 1.5% of capital cost is O&M Costs