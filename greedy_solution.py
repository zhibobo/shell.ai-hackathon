from solution import predict_biomass
from cost_helpers import calculate_cost_of_single_trip
from generate_submission import update_biomass_demand_supply, update_pellet_demand_supply, generate_submission
from tqdm import tqdm
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

DISTANCE_MATRIX = pd.read_csv('Distance_Matrix.csv')
SAMPLE_SUBMISSION = pd.read_csv("sample_submission.csv")
NUMBER_OF_DEPOTS = 15
NUMBER_OF_REFINERIES = 3
DEPOT_PROCESSING_CAPACITY = 20000 * 0.95
REFINERY_PROCESSING_CAPACITY = 100000 * 0.95


def generate_cost_depots(dist_mat: pd.DataFrame, biomass_forecast: pd.DataFrame, refineries: list):
    """
    Calculates the cost of transporting all biomass to a single depot. 

    Args:
        biomass_forecast: Forecasted biomass at each index which will be updated after each iteration

    Returns:
        index of biomass with the least cost (int)
    """
    cost_list = []
    for i in range(len(dist_mat.columns)-1):
        curr_index = dist_mat.iloc[:,i+1]
        curr_index_transport_cost = (curr_index.mul(biomass_forecast.iloc[:,1])).sum()
        cost_list.append([dist_mat.columns.values[i+1],curr_index_transport_cost])
        cost_list.sort(key = lambda x: x[1])

    for i in range(2417):
        if cost_list[i][0] not in refineries: # check for duplicates
            return(int(cost_list[i][0]))


def update_biomass_depot(new_depot: int, biomass_forecast: pd.DataFrame, dist_mat: pd.DataFrame, biomass_demand_supply: pd.DataFrame):
    """
    Calculates the cost of transportation of biomass to current depot. Updates the biomass at respective
    depots after movement

    Args:
        new_depot: Index of depot
        biomass_forecast: Forecasted biomass at each index before update
        dist_mat: distance between each biomass location

    Returns:
        cost_of_transportation: total amount of biomass * distance
        updated_biomass_forecast: Changes in biomass forecast due to biomass movement

    """
    cost = 0
    biomass_in_depot = 0
    shortest_dist_matrix = dist_mat.sort_values(by=str(new_depot), ascending=True)
    shortest_dist_col = shortest_dist_matrix.loc[:, str(new_depot)]
    # This is an attempt to weight the biomass. 
    # However, i think no difference is made lol
    # dist_matrix_from_depot = dist_mat[str(new_depot)]
    # forecast = biomass_forecast["2018/2019"]
    # shortest_dist_col = dist_matrix_from_depot * forecast
    # shortest_dist_col = shortest_dist_col.sort_values()
    for index, value in shortest_dist_col.items():
        
        if biomass_in_depot >= DEPOT_PROCESSING_CAPACITY:
            break
        if biomass_in_depot + biomass_forecast.loc[index,'2018/2019'] * 0.95 > DEPOT_PROCESSING_CAPACITY:
            update_biomass_demand_supply(new_depot, index, DEPOT_PROCESSING_CAPACITY - biomass_in_depot, biomass_demand_supply)
            biomass_moved = DEPOT_PROCESSING_CAPACITY - biomass_in_depot
            biomass_forecast.loc[index,'2018/2019'] -= biomass_moved
            biomass_in_depot = DEPOT_PROCESSING_CAPACITY
        else: 
            update_biomass_demand_supply(new_depot, index, biomass_forecast.loc[index,'2018/2019'] * 0.95, biomass_demand_supply)
            biomass_moved = biomass_forecast.loc[index,'2018/2019'] * 0.95
            biomass_in_depot += biomass_moved
            biomass_forecast.loc[index,'2018/2019'] = 0
        cost += calculate_cost_of_single_trip(index, new_depot, biomass_moved)
    return cost, pd.DataFrame(biomass_forecast)

def remove_empty_biomass(biomass_forecast: pd.DataFrame):
    """
    Removes all biomass locations with no biomass left from biomass forecast,
    so they wont be considered in next iteration

    Args:
        updated_biomass_forecast: biomass forecast after transport to depot

    Returns:
        biomass_indices_removed: List of empty biomass locations
        updated_biomass_forecast: Empty locations removed, ready for next iteration
    """
    removed_indices = []
    for index in biomass_forecast.index:
        if biomass_forecast.loc[index,'2018/2019'] == 0:
            biomass_forecast.drop(index,inplace=True)
            removed_indices.append(index)
    return removed_indices, pd.DataFrame(biomass_forecast)

def remove_empty_dist(index_to_remove: list, dist_mat: pd.DataFrame):
    """
    Removes all biomass locations with no biomass left in distance matrix, so
    they wont be considered in choosing the next depot

    Args:
        index_to_remove: list of empty biomass locations 
        dist_mat: initial distance matrix of locations
        
    Returns:
        updated_dist_mat: Distance matrix with columns and rows of empty biomass locations removed
    """
    for index in index_to_remove:
        dist_mat.drop(columns=[str(index)], inplace=True)
        dist_mat.drop(index,inplace=True)
    return dist_mat

def generate_depot_matrix(depots: list):
    new_dist_mat = []
    for index in range(len(DISTANCE_MATRIX.columns)-1):
        if index not in depots:
            continue
        else:
            new_dist_mat.append(DISTANCE_MATRIX.loc[int(index)])
    return pd.DataFrame(new_dist_mat)

def update_biomass_refinery(new_refinery: int, depot_forecast: pd.DataFrame, dist_mat_2: pd.DataFrame, pellet_demand_supply: pd.DataFrame):
    """
    Calculates the cost of transportation of biomass to current depot. Updates the biomass at respective
    depots after movement

    Args:
        new_refinery: Index of depot
        biomass_forecast: Forecasted biomass at each index before update
        dist_mat: distance between each biomass location

    Returns:
        cost_of_transportation: total amount of biomass * distance
        updated_biomass_forecast: Changes in biomass forecast due to biomass movement

    """
    cost = 0
    biomass_in_refinery = 0
    shortest_dist_matrix = dist_mat_2.sort_values(by=str(new_refinery), ascending=True)
    shortest_dist_col = shortest_dist_matrix.loc[:, str(new_refinery)]
    for index, value in shortest_dist_col.items():
        if biomass_in_refinery >= REFINERY_PROCESSING_CAPACITY:
            break
        if biomass_in_refinery + depot_forecast.loc[index,'2018/2019'] > REFINERY_PROCESSING_CAPACITY:
            update_pellet_demand_supply(new_refinery, index, (REFINERY_PROCESSING_CAPACITY - biomass_in_refinery), pellet_demand_supply)
            biomass_moved = REFINERY_PROCESSING_CAPACITY - biomass_in_refinery
            depot_forecast.loc[index,'2018/2019'] -= biomass_moved
            biomass_in_refinery = REFINERY_PROCESSING_CAPACITY
        else: 
            update_pellet_demand_supply(new_refinery, index, depot_forecast.loc[index,'2018/2019'], pellet_demand_supply)
            biomass_moved = depot_forecast.loc[index,'2018/2019']
            biomass_in_refinery += depot_forecast.loc[index,'2018/2019']
            depot_forecast.loc[index,'2018/2019'] = 0
        cost += calculate_cost_of_single_trip(index, new_refinery, biomass_moved)

    return cost, pd.DataFrame(depot_forecast)


def main():
    #Choosing the depot locations
    biomass_forecast = predict_biomass().iloc[:,[0,11]]
    dist_mat = DISTANCE_MATRIX.copy()
    total_cost = 0
    depots = []
    
    biomass_demand_supply = {}
    for i in tqdm(range(NUMBER_OF_DEPOTS), desc = "Iterating through depots"):
        generated_depot = generate_cost_depots(dist_mat, biomass_forecast, [])
        # print("The next depot is " + str(generated_depot))
        depots.append(generated_depot)

        move_to_depot_cost, updated_biomass_forecast = update_biomass_depot(generated_depot,biomass_forecast,dist_mat, biomass_demand_supply)
        #updated_biomass_forecast.to_csv("after_prev_iteration.csv")
        total_cost += move_to_depot_cost

        index_to_remove, biomass_forecast = remove_empty_biomass(updated_biomass_forecast)
        #biomass_forecast.to_csv('after_remove_empty_biomass.csv')
        dist_mat = remove_empty_dist(index_to_remove, dist_mat)
        #dist_mat.to_csv('after_remove_empty_dist.csv')
    print("The total transportation cost (harvest to depot) is " + str(total_cost))
    depots = sorted(depots)
    print(depots)
    #Choosing the refinaries
    pellet_demand_supply = {}
    depot_forecast = pd.DataFrame({'Index': depots, '2018/2019':[DEPOT_PROCESSING_CAPACITY,]*NUMBER_OF_DEPOTS}, index = depots)
    dist_mat_2 = generate_depot_matrix(depots)
    refineries = []
    for i in tqdm(range(NUMBER_OF_REFINERIES), desc = "Iterating through refineries"):
        generated_refinery = generate_cost_depots(dist_mat_2, depot_forecast, refineries)
        refineries.append(generated_refinery)

        move_to_refinery_cost , updated_depot_forecast = update_biomass_refinery(generated_refinery,depot_forecast,dist_mat_2,pellet_demand_supply)
        total_cost += move_to_refinery_cost

        index_to_remove, depot_forecast = remove_empty_biomass(updated_depot_forecast)
        #biomass_forecast.to_csv('after_remove_empty_biomass.csv')
        dist_mat_2 = remove_empty_dist(index_to_remove, dist_mat_2)
        #dist_mat.to_csv('after_remove_empty_dist.csv')
    print("The total transportation cost (depots to refineries) is " + str(total_cost))
    # print(refineries)
    
    generate_submission(depots, refineries, biomass_demand_supply, pellet_demand_supply)

    #Generating heatmap
    """
    initial_forecast = predict_biomass()
    merged_df = pd.merge(initial_forecast, biomass_forecast, on = "Index", how='left')
    merged_df.to_csv("remaining_biomass.csv")
    sns.heatmap(merged_df.pivot("Latitude", "Longitude", "2018/2019_y"))
    plt.show()
    """

if __name__ == '__main__':
    main()

