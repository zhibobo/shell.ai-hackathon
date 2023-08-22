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
    offspring1 = parent1[:crossover_point] + parent2[crossover_point:] # CATCH DUPLICATES HERE
    offspring2 = parent2[:crossover_point] + parent1[crossover_point:]
    return offspring1, offspring2

def perform_mutation(child: set[int], mutation_rate: float):
    mutated_child = child.copy()

    for i in range(len(mutated_child)):
        if random.random() < mutation_rate:
            mutated_child[i] = random.randint(0, 2417)  # Replace with a random integer

    return mutated_child


def main():
    iterations = input("How many iterations: ")
    if iterations == "secret":
        sets_of_depots = [[1086, 1740, 2233, 1469, 2178, 1101, 1938, 1485, 1907, 2333, 353, 1236, 1694, 1988, 1010], [1086, 1740, 985, 1469, 1790, 1101, 1938, 1485, 1907, 2333, 353, 1360, 1694, 1988, 1010], [1086, 1740, 985, 1469, 94, 1101, 1938, 1485, 1907, 2333, 353, 1360, 1694, 1988, 1010], [1086, 1740, 985, 1469, 94, 1101, 1938, 509, 1186, 1412, 353, 1360, 1694, 1988, 552], [1086, 1740, 985, 1469, 94, 1101, 1938, 1485, 1186, 2333, 353, 2114, 1694, 1988, 552], [1086, 1740, 985, 1469, 94, 1101, 1938, 2301, 1186, 2333, 353, 2114, 
1694, 1988, 552], [1086, 1740, 985, 1469, 94, 1101, 1938, 1485, 1186, 1412, 353, 1360, 1694, 1988, 2048], [1086, 1740, 985, 1469, 1558, 1101, 2130, 1485, 1225, 2333, 353, 1360, 1633, 1988, 552], [1086, 1740, 985, 1469, 94, 1101, 1938, 1485, 1907, 2333, 353, 1360, 1694, 1988, 1010], [1086, 1740, 985, 1469, 94, 1101, 1938, 1485, 1907, 2333, 353, 1360, 1694, 1988, 552]]
        print("Using saved depots, with lowest cost:", min([40218638.294213206, 56922050.33877739, 64986401.15816496, 16950344.489914026, 132152781.16508712, 87053075.85846142, 62963186.62290612, 49685494.09948571, 32883745.404578935, 16704417.449202554]))
        iterations = int(input("How many iterations: ")) 
    else:
        iterations = int(iterations)
        sets_of_depots = generate_inital_depots()
    biomass_forecast = predict_biomass()
    for _ in tqdm(range(iterations), desc="Iteration:"):
        biomass_for_iteration = biomass_forecast
        cost_of_depot_sets = []
        # calculate cost to fill each depot in each set
        for depots in sets_of_depots:
            cost = fill_depots_and_calculate_transport(depots, biomass_for_iteration)
            cost_of_depot_sets.append(cost)
        if _ == 0: print("Initial cost:", cost_of_depot_sets)

        # choose parents to have the next generation
        tournament_size = 2  # Tournament size 20% of gen size
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
    print("Final sets of Depots:", sets_of_depots)


if __name__ == '__main__':
    main()

'''
After running for: 3000 iterations ~4hrs
Final cost: [40218638.294213206, 56922050.33877739, 64986401.15816496, 16950344.489914026, 132152781.16508712, 87053075.85846142, 62963186.62290612, 49685494.09948571, 32883745.404578935, 16704417.449202554]
Final sets of Depots: [[1086, 1740, 2233, 1469, 2178, 1101, 1938, 1485, 1907, 2333, 353, 1236, 1694, 1988, 1010], [1086, 1740, 985, 1469, 1790, 1101, 1938, 1485, 1907, 2333, 353, 1360, 1694, 1988, 1010], [1086, 1740, 985, 1469, 94, 1101, 1938, 1485, 1907, 2333, 353, 1360, 1694, 1988, 1010], [1086, 1740, 985, 1469, 94, 1101, 1938, 509, 1186, 1412, 353, 1360, 1694, 1988, 552], [1086, 1740, 985, 1469, 94, 1101, 1938, 1485, 1186, 2333, 353, 2114, 1694, 1988, 552], [1086, 1740, 985, 1469, 94, 1101, 1938, 2301, 1186, 2333, 353, 2114, 
1694, 1988, 552], [1086, 1740, 985, 1469, 94, 1101, 1938, 1485, 1186, 1412, 353, 1360, 1694, 1988, 2048], [1086, 1740, 985, 1469, 1558, 1101, 2130, 1485, 1225, 2333, 353, 1360, 1633, 1988, 552], [1086, 1740, 985, 1469, 94, 1101, 1938, 1485, 1907, 2333, 353, 1360, 1694, 1988, 1010], [1086, 1740, 985, 1469, 94, 1101, 1938, 1485, 1907, 2333, 353, 1360, 1694, 1988, 552]]

After another 1000 iterations ~1hr
Final cost: [168013246.29398298, 19494886.809439886, 45479407.13145936, 19494886.809439886, 80184812.0997883, 28397082.31471725, 32518186.973485917, 52168289.94307286, 56064185.35552238, 20700790.50231924]
Final sets of Depots: [[2333, 1575, 611, 2034, 2119, 64, 929, 941, 684, 924, 2002, 992, 2143, 1921, 1026], [2333, 1575, 611, 2034, 1643, 64, 929, 941, 684, 924, 2002, 992, 395, 1921, 1026], [2333, 1575, 611, 1098, 2119, 64, 929, 941, 684, 924, 1042, 992, 2143, 1921, 1026], [2333, 1521, 260, 1284, 1036, 64, 1872, 2079, 684, 297, 2002, 992, 2143, 1921, 1026], [2333, 1575, 611, 2034, 2119, 1037, 929, 941, 684, 924, 752, 992, 2143, 1921, 1026], [2333, 644, 611, 1842, 2119, 64, 929, 941, 684, 924, 2002, 992, 2143, 1921, 1026], [2333, 1575, 611, 2034, 2119, 1037, 929, 941, 684, 924, 2002, 992, 2143, 1921, 1026], [2333, 1575, 611, 2034, 2119, 64, 
1872, 2079, 684, 297, 752, 992, 2143, 1921, 1026], [2333, 1598, 243, 771, 1036, 64, 929, 941, 453, 924, 2002, 992, 2143, 1921, 1026], [2333, 1521, 611, 1842, 2119, 64, 929, 941, 684, 924, 2002, 992, 2143, 1921, 1026]]

'''