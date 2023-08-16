import pandas as pd
dist_mat = pd.read_csv('Distance_Matrix.csv')
biomass_hist = pd.read_csv('Biomass_History.csv')

#predict biomass for 2018/2019
def predict_biomass():
    biomass_hist['2018/2019'] = biomass_hist.iloc[:,3:].mean(axis=1)
    return biomass_hist

def main():
    #load input data
    predicted_biomass = predict_biomass()

if __name__ == '__main__':
    main()