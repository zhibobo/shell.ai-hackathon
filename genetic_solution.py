import random
import pandas as pd
from tqdm import tqdm
from solution import predict_biomass
from cost_helpers import DEPOT_PROCESSING_CAPACITY, REFINERY_PROCESSING_CAPACITY, calculate_cost_of_single_trip

'''
Assume that Depot/Refinery construction will not destroy biomass
Assume the best Depot locations give the best Refinery locations
Assume we should always fill Depot

Total forecasted biomass is 341k. 
Accounting for fluctuations of 5%, 324k & 359k 
Minimum biomass to collect (constraints is 80%), 259k & 286k. 
Safe to collect more than 286k < 300k = 15 depots (multiples of 20k)

First, find the best Depot locations.
1. Randomly select 15 Depots 10 times.
2. Score the cost of each set.
    Have a int array containing the forecasted biomass at each index
    From each depot, 
        sort dist matrix at that index
        Fill depot until full
        substract biomass from locations
        Sum cost, attach to depot
3. Select parents based of fitness proportionate selection
4. Crossover parts of the parents, if not just take parents. 
     Also take the elite into next generation
5. Mutate children
6. Repeat steps 2-5 for as many iterations until a low cost is achieved. 

'''


DISTANCE_MATRIX = pd.read_csv('Distance_Matrix.csv')
SAMPLE_SUBMISSION = pd.read_csv("sample_submission.csv")

def generate_inital_depots(sets: int = 10, locations: int = 15):
    initial_depots = []
    while len(initial_depots) < sets:
        depot_locations = set()
        while len(depot_locations) < locations:
            location = random.randint(0, 2418)
            depot_locations.add(location) 
        initial_depots.append(depot_locations)
    return initial_depots

def fill_depots_and_calculate_transport(depots: set[int], forecasted_biomass: pd.DataFrame):
    forecasted_biomass_list = forecasted_biomass["2018/2019"].tolist()
    cost = 0
    for depot in depots:
        biomass_in_depot = 0
        shortest_distance_matrix = DISTANCE_MATRIX.sort_values(by=str(depot), ascending=True)
        shortest_distance_col = shortest_distance_matrix.iloc[:, depot + 1]
        for index, value in shortest_distance_col.items():
            if biomass_in_depot >= DEPOT_PROCESSING_CAPACITY:
                break
            if biomass_in_depot + forecasted_biomass_list[index] > DEPOT_PROCESSING_CAPACITY: # exceeds 20k
                forecasted_biomass_list[depot] -= DEPOT_PROCESSING_CAPACITY - biomass_in_depot
                biomass_in_depot = DEPOT_PROCESSING_CAPACITY
            else: 
                biomass_in_depot += forecasted_biomass_list[index]
                forecasted_biomass_list[index] = 0

            cost += calculate_cost_of_single_trip(index, depot, value)
    return cost

def main():
    sets_of_depots = generate_inital_depots()
    for _ in range(1):
        biomass_forecast = predict_biomass()
        cost_of_depot_sets = []
        for depots in tqdm(sets_of_depots, desc="Iterating through parents"):
            cost = fill_depots_and_calculate_transport(depots, biomass_forecast)
            cost_of_depot_sets.append(cost)
        print(cost_of_depot_sets)

if __name__ == '__main__':
    main()
