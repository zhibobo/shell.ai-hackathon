import pandas as pd

def calculate_cost_of_transportation(biomass_demand_supply: pd.DataFrame, pellet_demand_supply: pd.DataFrame):
    distance_matrix = pd.read_csv("Distance_Matrix.csv")
    cost = 0
    cost_in_2018 = 0
    cost_in_2019 = 0
    # Sum biomass cost 
    for index, biomass_row in biomass_demand_supply.iterrows():
        distance = distance_matrix.iloc[int(biomass_row["source_index"]), int(biomass_row["destination_index"]) + 1]
        distance_cost = distance * biomass_row["value"]
        cost += distance_cost
        if biomass_row["year"] == 2018:
            cost_in_2018 += distance_cost
        else:
            cost_in_2019 += distance_cost

    print("~ Transport cost for depots in 2018 is", cost_in_2018)
    print("~ Transport cost for depots in 2019 is", cost_in_2019)

    # Sum pellet cost 
    cost_in_2018 = 0
    cost_in_2019 = 0
    for index, pellet_row in pellet_demand_supply.iterrows():
        distance = distance_matrix.iloc[int(pellet_row["source_index"]), int(pellet_row["destination_index"]) + 1]
        distance_cost = distance * pellet_row["value"]
        cost += distance_cost
        if pellet_row["year"] == 2018:
            cost_in_2018 += distance_cost
        else:
            cost_in_2019 += distance_cost

    print("~ Transport cost for refineries in 2018 is", cost_in_2018)
    print("~ Transport cost for refineries in 2019 is", cost_in_2019)

    print ("==> Transport cost is", cost)
    return cost

def test_calculate_transport():
    df = pd.read_csv("sample_submission.csv")
    biomass_demand_supply = df[df.iloc[:, 1] == "biomass_demand_supply"]
    pellet_demand_supply = df[df.iloc[:, 1] == "pellet_demand_supply"]
    calculate_cost_of_transportation(biomass_demand_supply, pellet_demand_supply)
    return

def calculate_cost_of_underutilization(biomass_demand_supply: pd.DataFrame, pellet_demand_supply: pd.DataFrame, depot_locations: pd.DataFrame, refinery_locations: pd.DataFrame):
    DEPOT_PROCESSING_CAPACITY = 20000
    REFINERY_PROCESSING_CAPACITY = 100000
    depots = {
        2018: {},
        2019: {}
    }
    refineries = {
        2018: {},
        2019: {}
    }
    for index, depot_row in depot_locations.iterrows():
        depots[2018][depot_row["source_index"]] = 0
        depots[2019][depot_row["source_index"]] = 0
    for index, refinery_row in refinery_locations.iterrows():
        refineries[2018][refinery_row["source_index"]] = 0
        refineries[2019][refinery_row["source_index"]] = 0

    for index, biomass_row in biomass_demand_supply.iterrows():
        depots[biomass_row["year"]][biomass_row["destination_index"]] += biomass_row["value"] 

    for index, pellet_row in pellet_demand_supply.iterrows():
        refineries[pellet_row["year"]][pellet_row["destination_index"]] += pellet_row["value"] 

    cost = 0
    for year, location_dict in depots.items():
        yearly_cost = 0
        for index, value in location_dict.items():
            yearly_cost += DEPOT_PROCESSING_CAPACITY - value
        print("~ Underutilization cost for depots in", year, "is", yearly_cost)
        cost += yearly_cost

    for year, location_dict in refineries.items():
        yearly_cost = 0
        for index, value in location_dict.items():
            yearly_cost += REFINERY_PROCESSING_CAPACITY - value
        print("~ Underutilization cost for refineries in", year, "is", yearly_cost)
        cost += yearly_cost
    print("==> Underutilization cost is", cost)
    return cost

def test_calculate_underutilization():
    df = pd.read_csv("sample_submission.csv")
    depot_rows = df[df.iloc[:, 1] == "depot_location"]
    refinery_rows = df[df.iloc[:, 1] == "refinery_location"]
    biomass_demand_supply = df[df.iloc[:, 1] == "biomass_demand_supply"]
    pellet_demand_supply = df[df.iloc[:, 1] == "pellet_demand_supply"]
    calculate_cost_of_underutilization(depot_locations=depot_rows, refinery_locations=refinery_rows, biomass_demand_supply=biomass_demand_supply, pellet_demand_supply=pellet_demand_supply)
    return

test_calculate_transport()
test_calculate_underutilization()