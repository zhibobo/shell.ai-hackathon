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
Final Depots and Cost of each depot: {1922: 663783.5096799524, 2403: 2657975.6835127235, 1807: 689825.9257929691, 435: 875372.7014236345, 2255: 1429969.611400446, 
675: 1202811.4210089243, 1103: 1011957.2130423306, 658: 1344603.351167224, 861: 1559750.52762098, 1010: 905686.9112847644, 257: 1322195.9565092537, 954: 1484394.9954765309, 2021: 1088331.6283107281, 2143: 2137621.160098063, 127: 3797677.1027778443}   Total: 22171957.699106373
'''
