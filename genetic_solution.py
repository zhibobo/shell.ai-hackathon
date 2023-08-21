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
        depot_locations = []
        while len(depot_locations) < locations:
            location = random.randint(0, 2417)
            if location not in depot_locations:
                depot_locations.append(location) 
        initial_depots.append(depot_locations)
    return initial_depots

def fill_depots_and_calculate_transport(depots: list[int], forecasted_biomass: pd.DataFrame):
    """
    Calculates the necessary transport required to fill all the depots using biomass and returns the cost

    Args:
        depots (set[int]): A set of indexes representing the location of depots.
        forecasted_biomass (DataFrame): The forecasted biomass at each index.

    Returns:
        int: Transport cost necessary to fill up all depots.
    """
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

def tournament_selection(population, fitness_scores, tournament_size):
    selected_parents = []
    population_size = len(population)

    for _ in range(population_size):
        # Select random participants for the tournament
        tournament_participants = random.sample(population, tournament_size)

        # Calculate fitness scores for participants
        participant_fitness_scores = [fitness_scores[participant] for participant in tournament_participants]

        # Select the participant with the lowest cost from the tournament
        winner_index = participant_fitness_scores.index(min(participant_fitness_scores))
        selected_parent = tournament_participants[winner_index]

        selected_parents.append(selected_parent)

    return selected_parents

def perform_crossover(parent1: list[int], parent2: list[int]):
    crossover_point = random.randint(0, len(parent1))
    offspring1 = parent1[:crossover_point] + parent2[crossover_point:]
    offspring2 = parent2[:crossover_point] + parent1[crossover_point:]
    return offspring1, offspring2

def perform_mutation(child: set[int], mutation_rate: float):
    mutated_child = child.copy()

    for i in range(len(mutated_child)):
        if random.random() < mutation_rate:
            mutated_child[i] = random.randint(0, 2417)  # Replace with a random integer

    return mutated_child


def main():
    sets_of_depots = generate_inital_depots()
    for _ in tqdm(range(1000), desc="Iteration:"):
        biomass_forecast = predict_biomass()
        cost_of_depot_sets = []
        # calculate cost to fill each depot in each set
        for depots in sets_of_depots:
            cost = fill_depots_and_calculate_transport(depots, biomass_forecast)
            cost_of_depot_sets.append(cost)
        if _ == 0: print("Initial cost:", cost_of_depot_sets)

        # choose parents to have the next generation
        tournament_size = 3  # Tournament size
        population = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        selected_parents = tournament_selection(population, cost_of_depot_sets, tournament_size)

        children = []
        min_index = min(range(len(cost_of_depot_sets)), key=lambda i: cost_of_depot_sets[i])
        children.append(sets_of_depots[min_index]) # lowest cost parent survives to next generation
        for index in range(0, len(selected_parents) - 1, 2): # crossover to create children
            child1, child2 = perform_crossover(sets_of_depots[selected_parents[index]], sets_of_depots[selected_parents[index + 1]])
            children.append(child1)
            if len(children) < 10: children.append(child2)

        # Mutate children 
        mutation_rate = 1/len(children[0])
        for index in range(len(children)):
            children[index] = perform_mutation(children[index], mutation_rate)

        # for i in range(len(children)):
        #     print(f"Selected Parent {i}: {sets_of_depots[selected_parents[i]]}")
        #     print(f"Children {i}: {children[i]}")
        # print(children)
        sets_of_depots = children
    print("Final cost:", cost_of_depot_sets)


if __name__ == '__main__':
    main()