import random
import pandas as pd
from tqdm import tqdm
from genetic_solution import generate_inital_locations
from greedy_solution import DISTANCE_MATRIX, NUMBER_OF_DEPOTS, NUMBER_OF_REFINERIES, generate_cost_depots, generate_depot_matrix, remove_empty_biomass, remove_empty_dist, update_biomass_refinery
from cost_helpers import DEPOT_PROCESSING_CAPACITY, REFINERY_PROCESSING_CAPACITY, calculate_cost_of_single_trip

def fill_refineries(refineries: set[int], depots: set[int]):
    depots = list(depots)
    refinery_cost = {}
    pellet_demand_supply = {}
    # Calculate cost for filling each refinery
    depot_forecast = pd.DataFrame({'Index': depots, '2018/2019':[int(20000),]*NUMBER_OF_DEPOTS}, index = depots)
    dist_mat_2 = generate_depot_matrix(depots)
    for i in range(NUMBER_OF_REFINERIES):
        refinery = refineries.pop() # some randomness for fun

        move_to_refinery_cost , updated_depot_forecast = update_biomass_refinery(refinery,depot_forecast,dist_mat_2,pellet_demand_supply)
        refinery_cost[refinery] = move_to_refinery_cost

        index_to_remove, depot_forecast = remove_empty_biomass(updated_depot_forecast)
        #biomass_forecast.to_csv('after_remove_empty_biomass.csv')
        dist_mat_2 = remove_empty_dist(index_to_remove, dist_mat_2)
        #dist_mat.to_csv
        # ('after_remove_empty_dist.csv')
    return refinery_cost

def generate_next_generation(learning_rate: int, depots: set[int], refinery_cost: dict[int, int]):
    total_cost = sum(refinery_cost.values())
    refineries = list(refinery_cost.keys())
    next_generation_of_refineries = set()
    # print(refinery_cost)
    # Move each refinery in direction, determined through learning_rate
    for i in range(len(refineries)):
        if refineries[i] + learning_rate < 2417:
            new_refinery_1 = refineries[i] + learning_rate
        else: 
            new_refinery_1 = refineries[i] - 2 * learning_rate

        # Calculate cost of refinery 1
        new_refineries = set(refinery_cost.keys())
        new_refineries.remove(refineries[i])
        new_refineries.add(new_refinery_1)
        new_refinery_cost = fill_refineries(new_refineries, depots)
        total_cost_1 = sum(new_refinery_cost.values())
        
        if refineries[i] - learning_rate > 0:
            new_refinery_2 = refineries[i] - learning_rate
        else: 
            new_refinery_2 = refineries[i] + 2 * learning_rate


        # Calculate cost of refinery 2
        new_refineries = set(refinery_cost.keys())
        new_refineries.remove(refineries[i])
        new_refineries.add(new_refinery_2)
        new_refinery_cost = fill_refineries(new_refineries, depots)
        total_cost_2 = sum(new_refinery_cost.values())
        if total_cost < total_cost_1 and total_cost < total_cost_2:
            next_generation_of_refineries.add(refineries[i])
        elif total_cost_1 < total_cost_2 and total_cost_1 < total_cost:
            next_generation_of_refineries.add(new_refinery_1)
            refineries[i] = new_refinery_1
            total_cost = total_cost_1
        elif total_cost_2 < total_cost_1 and total_cost_2 < total_cost:
            next_generation_of_refineries.add(new_refinery_2)
            refineries[i] = new_refinery_2
            total_cost = total_cost_2
        else:
            print("I'm confused")
            random_refinery = random.randint(0, 2417)
            next_generation_of_refineries.add(random_refinery)
            refineries[i] = random_refinery
            total_cost = sum(refineries)

    # for refinery, cost in refinery_cost.items():
    #     if refinery + learning_rate < 2417:
    #         new_refinery_1 = refinery + learning_rate
    #     else: 
    #         new_refinery_1 = refinery - 2 * learning_rate

    #     # Calculate cost of refinery 1
    #     new_refineries = set(refinery_cost.keys())
    #     new_refineries.remove(refinery)
    #     new_refineries.add(new_refinery_1)
    #     new_refinery_cost = fill_refineries(new_refineries, depots)
    #     total_cost_1 = sum(new_refinery_cost.values())
        
    #     if refinery - learning_rate > 0:
    #         new_refinery_2 = refinery - learning_rate
    #     else: 
    #         new_refinery_2 = refinery + 2 * learning_rate


    #     # Calculate cost of refinery 2
    #     new_refineries = set(refinery_cost.keys())
    #     new_refineries.remove(refinery)
    #     new_refineries.add(new_refinery_2)
    #     new_refinery_cost = fill_refineries(new_refineries, depots)
    #     total_cost_2 = sum(new_refinery_cost.values())

    #     if total_cost < total_cost_1 and total_cost < total_cost_2:
    #         next_generation_of_refineries.add(refinery)
    #     elif total_cost_1 < total_cost_2 and total_cost_1 < total_cost:
    #         next_generation_of_refineries.add(new_refinery_1)
    #     elif total_cost_2 < total_cost_1 and total_cost_2 < total_cost:
    #         next_generation_of_refineries.add(new_refinery_2)
    #     else:
    #         print("I'm confused")
    #         next_generation_of_refineries.add(random.randint(0, 2417))
    return next_generation_of_refineries

def main():
    depots = {388, 504, 811, 1485, 2286, 1101, 1360, 1938, 1907, 1086, 94, 985, 1981, 1694, 1469}
    random_refineries = generate_inital_locations(sets=1, locations=3)[0] # Generate random refineries
    random_refineries = {1537, 2203, 1421}
    learning_rate = 1
    print("Initial Refineries and Cost of each refinery:", fill_refineries(random_refineries.copy(), depots))
    refineries = random_refineries
    iterations = int(input("How many iterations: ")) 
    for _ in tqdm(range(iterations), desc="Refinery gradient descent:"):
        refinery_cost = fill_refineries(refineries, depots)
        refineries = generate_next_generation(learning_rate, depots, refinery_cost)
        print(refineries)
    print("Final Refineries and Cost of each refinery:", refinery_cost)

if __name__ == '__main__':
    main()

{2403: 30481400.0, 1637: 9677564.0, 1421: 26258032.0}
{1537: 12123123.0, 2203: 14049849.0, 1421: 14712261.5}
{1426: 8476574.0, 2203: 12832213.5, 1527: 13749747.0}
{1425: 8400380.5, 2203: 12832213.5, 1531: 13685041.5}
# print(fill_refineries({1161, 1111, 1329}, {388, 504, 811, 1485, 2286, 1101, 1360, 1938, 1907, 1086, 94, 985, 1981, 1694, 1469}))