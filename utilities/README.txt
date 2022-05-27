# The usurdb_commercial_dataframe.csv file is used by the run_all_commercial_electricity_utility_rates() function inside heat_pump_model.py

# This function does not yet live up to it's name as of 5-27-2022. The function currently selects the utility rate and applies the rate
# structure (periods) to update the self.hourly_utility_rate from the first row of the usurdb_commercial_dataframe.csv. If a for-loop is applied,
# all the utility rates can be applied and any resulting calculations could be saved as a DataFrame and/or csv.

# The usurdb_commercial_dataframe.csv file is simply filtered data from the usurdb.csv file.

# Ultimately, this function should include the demand charges and tiers for more accurate utility pricing. Currently, the usurdb_commercial_dataframe.csv
# file only includes the first tier. The function should run the thermal model once then rerun the appropriate economic functions to produce the following
# table:

# utility name | year_one_energy_costs | year_one_operating_costs | LCOH | kwh_CAGR_energy_costs | net_present_value | internal_rate_of_return | payback_period | Utility Rate Average
# _____________|_______________________|__________________________|______|_______________________|___________________|_________________________|________________|_____________________
# _____________|_______________________|__________________________|______|_______________________|___________________|_________________________|________________|_____________________