import random
import pandas as pd
from tqdm import tqdm
from genetic_solution import generate_inital_locations
from greedy_solution import DISTANCE_MATRIX, NUMBER_OF_DEPOTS, update_biomass_depot
from solution import predict_biomass

def fill_depots(depots: list[int], biomass_forecast: pd.DataFrame):
    depot_cost = {}
    biomass_demand_supply = {}
    # Calculate cost for filling each refinery
    dist_mat = DISTANCE_MATRIX
    for i in range(NUMBER_OF_DEPOTS):
        depot = depots[i]
        move_to_depot_cost, biomass_forecast = update_biomass_depot(depot,biomass_forecast,dist_mat, biomass_demand_supply)
        depot_cost[depot] = move_to_depot_cost
    return depot_cost

def generate_next_generation(learning_rate: int, depots: set[int], depot_cost: dict[int, int], biomass_forecast: pd.DataFrame):
    total_cost = sum(depot_cost.values())
    depots = list(depot_cost.keys())
    next_generation_of_depots = []
    dist_mat = DISTANCE_MATRIX
    # print(depot_cost)
    # Move each depot in direction, determined through learning_rate
    for i in range(len(depots)):
        if depots[i] + learning_rate < 2417:
            new_depot_1 = depots[i] + learning_rate
        else: 
            new_depot_1 = depots[i] - 2 * learning_rate

        # Calculate cost of depot 1
        new_depots = list(depot_cost.keys())
        new_depots.remove(depots[i])
        new_depots.append(new_depot_1)
        new_depot_cost = fill_depots(new_depots, biomass_forecast.copy())
        total_cost_1 = sum(new_depot_cost.values())
        
        if depots[i] - learning_rate > 0:
            new_depot_2 = depots[i] - learning_rate
        else: 
            new_depot_2 = depots[i] + 2 * learning_rate


        # Calculate cost of depot 2
        new_depots = list(depot_cost.keys())
        new_depots.remove(depots[i])
        new_depots.append(new_depot_2)
        new_depot_cost = fill_depots(new_depots, biomass_forecast.copy())
        total_cost_2 = sum(new_depot_cost.values())
        if total_cost < total_cost_1 and total_cost < total_cost_2:
            next_generation_of_depots.append(depots[i])
        elif total_cost_1 < total_cost_2 and total_cost_1 < total_cost:
            next_generation_of_depots.append(new_depot_1)
            depots[i] = new_depot_1
            total_cost = total_cost_1
        elif total_cost_2 < total_cost_1 and total_cost_2 < total_cost:
            next_generation_of_depots.append(new_depot_2)
            depots[i] = new_depot_2
            total_cost = total_cost_2
        else:
            print("I'm confused")
            random_depot = random.randint(0, 2417)
            next_generation_of_depots.append(random_depot)
            depots[i] = random_depot
            total_cost = sum(depots)

    return next_generation_of_depots

def perform_mutation(depots: list[int], mutation_rate: float, depots_cost: int, biomass_forecast: pd.DataFrame):
    children = depots.copy()
    child_length = len(depots) 
    if random.random() < mutation_rate:
        index = random.randint(0, child_length - 1)
        while True:
            new_child = random.randint(0, 2417)
            if new_child not in children:
                children[index] = new_child  # Replace with a random integer
                break
    chlidren_cost = sum(fill_depots(children, biomass_forecast).values())
    if depots_cost > chlidren_cost:
        return children
    else:
        return depots

def main():
    biomass_forecast = predict_biomass()
    random_depots = list(generate_inital_locations(sets=1, locations=15)[0]) # Generate random depots
    learning_rate = 10
    depot_cost = fill_depots(random_depots, biomass_forecast.copy())
    print("Initial depots and Cost of each refinery:", depot_cost, "  Total:", sum(depot_cost.values()))
    depots = random_depots
    iterations = int(input("How many iterations: ")) 
    for _ in tqdm(range(iterations), desc="Depot gradient descent:"):
        depot_cost = fill_depots(depots, biomass_forecast.copy())
        depots = generate_next_generation(learning_rate, depots, depot_cost, biomass_forecast.copy())
        if _ < iterations - 1:
            mutation_rate = 1/len(depots)
            depots = perform_mutation(depots, mutation_rate, sum(depot_cost.values()), biomass_forecast.copy())
        print(depots)
    print("Final Depots and Cost of each depot:", depot_cost, "  Total:", sum(depot_cost.values()))

if __name__ == '__main__':
    main()
'''
{2403: 30481400.0, 1637: 9677564.0, 1421: 26258032.0}
{1537: 12123123.0, 2203: 14049849.0, 1421: 14712261.5}
{1426: 8476574.0, 2203: 12832213.5, 1527: 13749747.0}
{1425: 8400380.5, 2203: 12832213.5, 1531: 13685041.5}

{1578, 491, 2090}
{2277: 14665749.0, 1198: 14306738.0, 1295: 9606733.0}
{2282, 1198, 1295}
{2282: 13601981.5, 1198: 14306738.0, 1295: 9606733.0}

{1324: 9725492.5, 218: 12391312.0, 352: 25335236.0}
{1324: 9725492.5, 218: 12391312.0, 352: 25335236.0}
{2282: 13601981.5, 1098: 10061732.0, 1293: 9693957.5}

{1912: 9461128.0, 990: 9196705.0, 1293: 9693957.5} [1912, 990, 1293]
{1293: 8446844.0, 806: 10463851.0, 1751: 9413259.5} [1293, 806, 1751]

{1424: 7099498.0, 1750: 5876937.5, 1161: 6437399.5}
[1424, 1750, 1161]

{1360: 8336008.0, 741: 10838003.5, 1858: 9745523.5} [1360, 741, 1858]
'''
# print(fill_refineries({2282, 1198, 1295}, {388, 504, 811, 1485, 2286, 1101, 1360, 1938, 1907, 1086, 94, 985, 1981, 1694, 1469}))
# print(fill_refineries({1425, 2203, 1531}, {388, 504, 811, 1485, 2286, 1101, 1360, 1938, 1907, 1086, 94, 985, 1981, 1694, 1469}))
# print(fill_refineries({1161, 1111, 1330}, {388, 504, 811, 1485, 2286, 1101, 1360, 1938, 1907, 1086, 94, 985, 1981, 1694, 1469}))