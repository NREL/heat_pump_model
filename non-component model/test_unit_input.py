from logging.config import DEFAULT_LOGGING_CONFIG_PORT
from utilities.unit_defs import ureg, Q_

# T_i = Q_(input('Input Temp? ') + input('Temp Unit? ')).to(ureg.degC)
T_im = float(input('Input Temperature: '))
print(ureg.get_compatible_units('[temperature]'))
T_iu = ureg.parse_units(input('Select Temperature Unit: '), as_delta=False)
T_i = Q_(T_im, T_iu).to('degC')

Q_im = float(input('Heat In: '))
print(ureg.get_compatible_units('[energy]'))
Q_iu = ureg.parse_units(input('Select Heat Unit: '), as_delta=False)
Q_i = Q_(Q_im, Q_iu).to('J')

print(f'{T_i:.2f~P}')
print(f'{Q_i:.2f~P}')
