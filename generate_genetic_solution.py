from greedy_solution import update_biomass_refinery, update_biomass_depot, remove_empty_biomass, remove_empty_dist, generate_depot_matrix, generate_submission
from solution import predict_biomass
import pandas as pd

DISTANCE_MATRIX = pd.read_csv('Distance_Matrix.csv')
SAMPLE_SUBMISSION = pd.read_csv("sample_submission.csv")
NUMBER_OF_DEPOTS = 15
NUMBER_OF_REFINERIES = 3
DEPOT_PROCESSING_CAPACITY = 20000 * 0.95
REFINERY_PROCESSING_CAPACITY = 100000 * 0.95

depots = [388, 504, 811, 1485, 2286, 1101, 1360, 1938, 1907, 1086, 94, 985, 1981, 1694, 1469]
refineries = [1425,2203,1531]

def main():
    biomass_forecast = predict_biomass().iloc[:,[0,11]]
    dist_mat = DISTANCE_MATRIX.copy()
    total_cost = 0

    biomass_demand_supply = {}
    for index in depots:
        print(index)
        move_to_depot_cost, updated_biomass_forecast = update_biomass_depot(index,biomass_forecast,dist_mat, biomass_demand_supply)
        total_cost += move_to_depot_cost

        index_to_remove, biomass_forecast = remove_empty_biomass(updated_biomass_forecast)
        dist_mat = remove_empty_dist(index_to_remove, dist_mat)

    depot_forecast = pd.DataFrame({'Index': depots, '2018/2019':[DEPOT_PROCESSING_CAPACITY,]*NUMBER_OF_DEPOTS}, index = depots)
    dist_mat_2 = generate_depot_matrix(depots)
    pellet_demand_supply = {}
    for index2 in refineries:   
        move_to_refinery_cost , updated_depot_forecast = update_biomass_refinery(index2,depot_forecast,dist_mat_2,pellet_demand_supply)
        total_cost += move_to_refinery_cost

        index_to_remove, depot_forecast = remove_empty_biomass(updated_depot_forecast)

        dist_mat_2 = remove_empty_dist(index_to_remove, dist_mat_2)

    print("total cost: " + str(total_cost))

    generate_submission(depots, refineries, biomass_demand_supply, pellet_demand_supply)

if __name__ == '__main__':
    main()