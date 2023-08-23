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
            depot_locations.add(random.randint(0, 2417)) 
        initial_depots.append(depot_locations)
    return initial_depots

def fill_depots_and_calculate_transport(depots: set[int], forecasted_biomass: pd.DataFrame):
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

def perform_crossover(parent1: set[int], parent2: set[int]):
    crossover_point = random.randint(0, len(parent1) - 1)
    parent1 = list(parent1)
    parent2 = list(parent2)
    if len(parent1) != len(parent2):
        print("ERROR FOUND HERE!", parent1, parent2)
        if len(parent1) < 15:
            parent1.append(random.randint(0, 2417))
        if len(parent2) < 15:
            parent2.append(random.randint(0, 2417))
    offspring1 = set()
    offspring2 = set()
    for index in range(len(parent1)):
        if index < crossover_point:
            offspring1.add(parent1[index])
            offspring2.add(parent2[index])
        else:
            offspring2.add(parent1[index])
            offspring1.add(parent2[index])
    index1= 0
    while len(offspring1) < len(parent1):
        if index1 < len(parent1):
            offspring1.add(parent1[index1])
        else:
            offspring1.add(random.randint(0, 2417))
        index1 += 1
    index2=0
    while len(offspring2) < len(parent2):
        if index2 < len(parent2):
            offspring2.add(parent2[index2])
        else:
            offspring2.add(random.randint(0, 2417))
        index2 += 1

    return offspring1, offspring2

def perform_mutation(children: list[set[int]], mutation_rate: float):
    child_length = len(children[0]) 
    for index in range(len(children)):
        if random.random() < mutation_rate:
            children[index].pop()
            while len(children[index]) < child_length:
                children[index].add(random.randint(0, 2417))  # Replace with a random integer
    return children


def main():
    iterations = input("How many iterations: ")
    if iterations == "secret":
        sets_of_depots = [{388, 504, 811, 1485, 1101, 2286, 1360, 1938, 1907, 1086, 94, 985, 1981, 1694, 1469}, {388, 811, 1694, 1485, 2286, 1101, 1360, 1938, 1907, 
504, 985, 1086, 1981, 94, 1469}, {388, 811, 1694, 1485, 2286, 1101, 1360, 1938, 1907, 504, 985, 1086, 1981, 94, 1469}, {388, 811, 1694, 1485, 2286, 1101, 1360, 1938, 1907, 504, 985, 1086, 1981, 94, 1469}, {388, 811, 1485, 2286, 1101, 1360, 1938, 1907, 94, 504, 985, 1086, 1981, 1694, 1469}, {388, 811, 1694, 1485, 2286, 1101, 1360, 1938, 1907, 504, 985, 1086, 1981, 94, 1469}, {388, 811, 1694, 1485, 2286, 1101, 1360, 1938, 1907, 504, 985, 1086, 1981, 94, 1469}, {388, 811, 1694, 1485, 
1101, 2286, 1360, 1938, 1907, 504, 985, 1086, 1981, 94, 1469}, {388, 811, 1694, 1485, 2286, 1101, 1360, 1938, 1907, 504, 94, 985, 1981, 1086, 1469}, {388, 811, 1485, 2286, 1101, 1360, 1938, 1907, 94, 504, 985, 1086, 1981, 1694, 1469}]
        print("Using saved depots, with lowest cost:", min([7453177.211994515, 7584148.660531587, 8352251.634412729, 8352251.634412722, 8352251.634412722, 8352251.634412722, 8352251.634412721, 7964046.886082531, 25865075.35801047, 7964046.886082531]
))
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
        children = perform_mutation(children, mutation_rate)

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

After another 1000 iterations ~1hr
Final cost: [51598904.5219258, 68405093.12135077, 16704417.449202554, 56955222.5163988, 16950344.489914026, 25139939.453170087, 96632994.99945362, 41081173.25854627, 16704417.449202554, 14746041.815643761]))
Final sets of Depots: [{1086, 1740, 2233, 1469, 2178, 1101, 1938, 1485, 1907, 2333, 353, 1236, 1694, 1988, 1010}, {1086, 1740, 985, 1469, 1790, 1101, 1938, 1485, 1907, 2333, 353, 1360, 1694, 1988, 1010}, {1086, 1740, 985, 1469, 94, 1101, 1938, 1485, 1907, 2333, 353, 1360, 1694, 1988, 1010}, {1086, 1740, 985, 1469, 94, 1101, 1938, 509, 1186, 1412, 353, 1360, 1694, 1988, 552}, {1086, 1740, 985, 1469, 94, 1101, 1938, 1485, 1186, 2333, 353, 2114, 1694, 1988, 552}, {1086, 1740, 985, 1469, 94, 1101, 1938, 2301, 1186, 2333, 353, 2114, 
1694, 1988, 552}, {1086, 1740, 985, 1469, 94, 1101, 1938, 1485, 1186, 1412, 353, 1360, 1694, 1988, 2048}, {1086, 1740, 985, 1469, 1558, 1101, 2130, 1485, 1225, 2333, 353, 1360, 1633, 1988, 552}, {1086, 1740, 985, 1469, 94, 1101, 1938, 1485, 1907, 2333, 353, 1360, 1694, 1988, 1010}, {1086, 1740, 985, 1469, 94, 1101, 1938, 1485, 1907, 2333, 353, 1360, 1694, 1988, 552}]

After another 1000 iterations ~1hr
Final cost: [8786446.738655157, 9890983.298936546, 9925734.24213069, 9695846.73042403, 8786446.738655157, 9695846.73042403, 8786446.738655157, 10763106.92409065, 
10763106.92409065, 8786446.738655157]
Final sets of Depots: [{552, 811, 1485, 1101, 1981, 1360, 1938, 1907, 504, 94, 1086, 985, 2333, 1694, 1469}, {2333, 552, 811, 1694, 1485, 1101, 1360, 1938, 1907, 
504, 985, 1086, 1981, 94, 1469}, {2333, 552, 811, 1694, 1485, 1101, 1360, 1938, 1907, 504, 985, 1086, 1981, 94, 1469}, {552, 811, 1694, 1485, 1101, 494, 1360, 1938, 1907, 504, 985, 1086, 1981, 94, 1469}, {2333, 552, 811, 1694, 1485, 1101, 1360, 1938, 1907, 504, 985, 1086, 1981, 94, 1469}, {552, 811, 1694, 1485, 1101, 1981, 1360, 1938, 1907, 504, 985, 1086, 2333, 94, 1469}, {2333, 552, 811, 1101, 1485, 1360, 1938, 1907, 504, 94, 1086, 985, 1981, 1694, 1469}, {2333, 552, 811, 1694, 1485, 1101, 1360, 1938, 1907, 504, 985, 1086, 1981, 94, 1469}, {552, 811, 1485, 1101, 1981, 1360, 1938, 1907, 504, 94, 1086, 985, 2333, 1694, 1469}, {2333, 552, 811, 1694, 1485, 1101, 1360, 1938, 1907, 504, 985, 1086, 1981, 94, 1469}]

After another 500 iterations ~1hr
Final cost: [8486112.884062981, 8648191.252849221, 8486112.884062981, 8648191.252849221, 8648191.252849221, 8575873.517198808, 8486112.884062981, 8648191.252849221, 8648191.252849221, 8486112.88406299]
Final sets of Depots: [{552, 811, 1694, 1101, 1485, 2286, 1360, 1938, 1907, 504, 985, 1086, 1981, 94, 1469}, {2201, 811, 1485, 1101, 2286, 1360, 1938, 1907, 94, 504, 985, 1086, 1981, 1694, 1469}, {552, 811, 1485, 1101, 2286, 1360, 1938, 1907, 504, 94, 1086, 985, 1981, 1694, 1469}, {2272, 811, 1694, 1101, 1485, 2286, 1360, 
1938, 1907, 94, 504, 985, 1981, 1086, 1469}, {552, 504, 811, 1485, 1101, 2286, 1360, 1938, 1907, 1086, 94, 985, 1981, 1694, 1469}, {552, 811, 1485, 1101, 2286, 1360, 1938, 1907, 504, 94, 1086, 985, 1981, 1694, 1469}, {552, 811, 1694, 1101, 1485, 2286, 1360, 1938, 1907, 94, 504, 985, 1981, 1086, 1469}, {552, 811, 1485, 1101, 2286, 1360, 1938, 1907, 94, 504, 985, 1086, 1981, 1694, 1469}, {552, 811, 1485, 1101, 2286, 1360, 1938, 1907, 504, 94, 1086, 985, 1981, 1694, 1469}, {552, 811, 
1485, 1101, 2286, 1360, 1938, 1907, 504, 94, 1086, 985, 1981, 1694, 1469}]

After another 1000 iterations ~1hr
Final cost: [7453177.211994515, 7584148.660531587, 8352251.634412729, 8352251.634412722, 8352251.634412722, 8352251.634412722, 8352251.634412721, 7964046.886082531, 25865075.35801047, 7964046.886082531]
Final sets of Depots: [{388, 504, 811, 1485, 1101, 2286, 1360, 1938, 1907, 1086, 94, 985, 1981, 1694, 1469}, {388, 811, 1694, 1485, 2286, 1101, 1360, 1938, 1907, 
504, 985, 1086, 1981, 94, 1469}, {388, 811, 1694, 1485, 2286, 1101, 1360, 1938, 1907, 504, 985, 1086, 1981, 94, 1469}, {388, 811, 1694, 1485, 2286, 1101, 1360, 1938, 1907, 504, 985, 1086, 1981, 94, 1469}, {388, 811, 1485, 2286, 1101, 1360, 1938, 1907, 94, 504, 985, 1086, 1981, 1694, 1469}, {388, 811, 1694, 1485, 2286, 1101, 1360, 1938, 1907, 504, 985, 1086, 1981, 94, 1469}, {388, 811, 1694, 1485, 2286, 1101, 1360, 1938, 1907, 504, 985, 1086, 1981, 94, 1469}, {388, 811, 1694, 1485, 
1101, 2286, 1360, 1938, 1907, 504, 985, 1086, 1981, 94, 1469}, {388, 811, 1694, 1485, 2286, 1101, 1360, 1938, 1907, 504, 94, 985, 1981, 1086, 1469}, {388, 811, 1485, 2286, 1101, 1360, 1938, 1907, 94, 504, 985, 1086, 1981, 1694, 1469}]
'''