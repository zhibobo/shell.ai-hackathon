import pandas as pd
from tqdm import tqdm
from cost_helpers import DEPOT_PROCESSING_CAPACITY, calculate_cost_of_single_trip
from solution import predict_biomass
from generate_submission import update_biomass_demand_supply, update_pellet_demand_supply, generate_submission
from greedy_solution import NUMBER_OF_DEPOTS, NUMBER_OF_REFINERIES, generate_cost_depots, generate_depot_matrix, remove_empty_biomass, remove_empty_dist, update_biomass_depot, update_biomass_refinery

DISTANCE_MATRIX = pd.read_csv('Distance_Matrix.csv')

def fill_depots_and_track_demand_supply(depots: set[int], forecasted_biomass: pd.DataFrame, biomass_demand_supply: dict):
    cost = 0
    for depot in depots:
        biomass_in_depot = 0
        shortest_dist_matrix = DISTANCE_MATRIX.sort_values(by=str(depot), ascending=True)
        shortest_dist_col = shortest_dist_matrix.loc[:, str(depot)]
        for index, value in shortest_dist_col.items():
            if biomass_in_depot >= DEPOT_PROCESSING_CAPACITY:
                break
            if biomass_in_depot + forecasted_biomass.loc[index,'2018/2019'] > DEPOT_PROCESSING_CAPACITY:
                update_biomass_demand_supply(depot, index, DEPOT_PROCESSING_CAPACITY - biomass_in_depot, biomass_demand_supply)
                forecasted_biomass.loc[index,'2018/2019'] -= DEPOT_PROCESSING_CAPACITY - biomass_in_depot
                biomass_in_depot = DEPOT_PROCESSING_CAPACITY
            else: 
                update_biomass_demand_supply(depot, index, forecasted_biomass.loc[index,'2018/2019'], biomass_demand_supply)
                biomass_in_depot += forecasted_biomass.loc[index,'2018/2019']
                forecasted_biomass.loc[index,'2018/2019'] = 0
            cost += calculate_cost_of_single_trip(index, depot, value)    
    return cost

def main():
    predicted_biomass = predict_biomass()
    set_of_depots = {388, 504, 811, 1485, 2286, 1101, 1360, 1938, 1907, 1086, 94, 985, 1981, 1694, 1469}
    biomass_demand_supply = {}
    total_cost = fill_depots_and_track_demand_supply(set_of_depots, predicted_biomass, biomass_demand_supply)
    print(total_cost)
    return
    pellet_demand_supply = {}
    depot_forecast = pd.DataFrame({'Index': list(set_of_depots), '2018/2019':[int(20000),]*NUMBER_OF_DEPOTS}, index = list(set_of_depots))
    dist_mat_2 = generate_depot_matrix(set_of_depots)
    refineries = []
    for i in tqdm(range(NUMBER_OF_REFINERIES), desc = "Iterating through refineries"):
        generated_refinery = generate_cost_depots(dist_mat_2, depot_forecast)
        refineries.append(generated_refinery)

        move_to_refinery_cost , updated_depot_forecast = update_biomass_refinery(generated_refinery,depot_forecast,dist_mat_2,pellet_demand_supply)
        total_cost += move_to_refinery_cost

        index_to_remove, depot_forecast = remove_empty_biomass(updated_depot_forecast)
        #biomass_forecast.to_csv('after_remove_empty_biomass.csv')
        dist_mat_2 = remove_empty_dist(index_to_remove, dist_mat_2)
        #dist_mat.to_csv('after_remove_empty_dist.csv')

    print("The total transportation cost (depots to refineries) is " + str(total_cost))
    print(refineries)
    
    generate_submission(set_of_depots, refineries, biomass_demand_supply, pellet_demand_supply)
    return

if __name__ == '__main__':
    main()

