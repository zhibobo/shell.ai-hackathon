from solution import predict_biomass
from cost_helpers import DEPOT_PROCESSING_CAPACITY, REFINERY_PROCESSING_CAPACITY, calculate_cost_of_single_trip
from generate_submission import format_biomass_demand_supply, generate_submission
from tqdm import tqdm
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

DISTANCE_MATRIX = pd.read_csv('Distance_Matrix.csv')
SAMPLE_SUBMISSION = pd.read_csv("sample_submission.csv")
NUMBER_OF_DEPOTS = 15
NUMBER_OF_REFINERIES = 5



def generate_cost_depots(dist_mat: pd.DataFrame, biomass_forecast: pd.Series):
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
    return(int(cost_list[0][0]))

def update_biomass(new_depot: int, biomass_forecast: pd.DataFrame, dist_mat: pd.DataFrame, biomass_demand_supply: pd.DataFrame):
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
    for index, value in shortest_dist_col.items():
        if biomass_in_depot >= DEPOT_PROCESSING_CAPACITY:
            break
        if biomass_in_depot + biomass_forecast.loc[index,'2018/2019'] > DEPOT_PROCESSING_CAPACITY:
            update_biomass_demand_supply(new_depot, index, DEPOT_PROCESSING_CAPACITY - biomass_in_depot, biomass_demand_supply)
            biomass_forecast.loc[index,'2018/2019'] -= DEPOT_PROCESSING_CAPACITY - biomass_in_depot
            biomass_in_depot = DEPOT_PROCESSING_CAPACITY
        else: 
            update_biomass_demand_supply(new_depot, index, biomass_forecast.loc[index,'2018/2019'], biomass_demand_supply)
            biomass_in_depot += biomass_forecast.loc[index,'2018/2019']
            biomass_forecast.loc[index,'2018/2019'] = 0
        cost += calculate_cost_of_single_trip(index, new_depot, value)
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
    new_dist_mat = pd.DataFrame()
    for index in depots:
        print(index)
        new_dist_mat.append(DISTANCE_MATRIX.iloc[index,:])
    return new_dist_mat

def update_biomass_demand_supply(depot: int, biomass_location: int, biomass_demand: int, biomass_demand_supply: pd.DataFrame):
    if depot not in biomass_demand_supply:
        biomass_demand_supply[depot] = {biomass_location: biomass_demand}
    else:
        biomass_demand_supply[depot][biomass_location] = biomass_demand
    return

def main():
    #Choosing the depot locations
    biomass_forecast = predict_biomass().iloc[:,[0,11]]
    # print(biomass_forecast)
    dist_mat = DISTANCE_MATRIX
    # print(dist_mat)
    # print(dist_mat.iloc[810,:])
    total_cost = 0
    depots = []
    biomass_demand_supply = {}
    for i in tqdm(range(NUMBER_OF_DEPOTS), desc = "Iterating through depots"):
        generated_depot = generate_cost_depots(dist_mat, biomass_forecast)
        # print("The next depot is " + str(generated_depot))
        depots.append(generated_depot)

        cost, updated_biomass_forecast = update_biomass(generated_depot,biomass_forecast,dist_mat,biomass_demand_supply)
        #updated_biomass_forecast.to_csv("after_prev_iteration.csv")
        total_cost += cost

        index_to_remove, biomass_forecast = remove_empty_biomass(updated_biomass_forecast)
        #biomass_forecast.to_csv('after_remove_empty_biomass.csv')
        dist_mat = remove_empty_dist(index_to_remove, dist_mat)
        #dist_mat.to_csv('after_remove_empty_dist.csv')
    print("The total transportation cost (harvest to depot) is", total_cost)
    sorted_depots = sorted(depots)
    print(sorted_depots)
    generate_submission(depot_locations=sorted_depots, refinery_locations=["1", "2", "3", "4" ,"5"], biomass_demand_supply=biomass_demand_supply)
    

    #Choosing the refinaries
    """ 
    ***Work in Progress***
    depot_forecast = pd.DataFrame({'Index': depots, '2018/2019':[20000,]*NUMBER_OF_DEPOTS})
    dist_mat_2 = generate_depot_matrix(depots)
    print(dist_mat_2)
    """

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

