from pint import UnitRegistry
ureg = UnitRegistry()
Q_ = ureg.Quantity
ureg.define('million_Btu = 1e6 * british_thermal_units = MMBtu')
ureg.define('percent = 1e2 * dimensionless')
ureg.define('$ = [currency] = USD = USdollar = USdollars')
ureg.define('million_standard_cubic_feet = 1e6 * ft**3 = MMSCF')