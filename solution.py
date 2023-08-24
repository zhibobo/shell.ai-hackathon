import pandas as pd
from statsmodels.tsa.arima_model import ARIMA
from statsmodels.tsa.holtwinters import SimpleExpSmoothing,ExponentialSmoothing

dist_mat = pd.read_csv('Distance_Matrix.csv')
biomass_hist = pd.read_csv('Biomass_History.csv')


#predict biomass for 2018/2019 using average values

def predict_biomass_average():
    biomass_hist['2018/2019'] = biomass_hist.iloc[:,3:].mean(axis=1)
    return biomass_hist

def predict_biomass_2018():
    forecast_list_2018 = []
    for index in range(len(biomass_hist)):
        biomass_values = list(biomass_hist.iloc[index,3:]) + [0,]
        years = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018]

        current_grid = pd.DataFrame({'date':years, 'value':biomass_values})

        train_data = current_grid.iloc[1:len(current_grid)-1]
        test_data = current_grid.iloc[len(current_grid)-1:]

        model_2018 = ExponentialSmoothing(train_data.value)
        model_fitted_2018 = model_2018.fit(smoothing_level = 0.05)

        #print('coefficients',model_fitted_2018.params)
        predictions_2018 = model_fitted_2018.predict(start=len(train_data), end=len(train_data) + len(test_data)-1)
        forecast_list_2018.append(float(predictions_2018))
    biomass_hist['2018/2019'] = forecast_list_2018
    return biomass_hist

##not in use currently
def predict_biomass_2019(predicted_biomass_2018):
    forecast_list_2019= []
    for index in range(len(predicted_biomass_2018)):
        biomass_values = list(predicted_biomass_2018.iloc[index,3:]) + [0,]
        years = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019]
        current_grid = pd.DataFrame({'date':years, 'value':biomass_values})

        train_data = current_grid.iloc[1:len(current_grid)-1]
        test_data = current_grid.iloc[len(current_grid)-1:]

        model_2019 = ExponentialSmoothing(train_data.value)
        model_fitted_2019 = model_2019.fit()

        #print('coefficients',model_fitted.params)
        predictions_2019 = model_fitted_2019.predict(start=len(train_data), end=len(train_data) + len(test_data)-1)
        forecast_list_2019.append(float(predictions_2019))
    predicted_biomass_2018['2019'] = forecast_list_2019
    return predicted_biomass_2018

#tried to predict for each year individually but fail lmao
#generated the best score for greedy solution so far
def predict_biomass():
    predicted_biomass_2018 = predict_biomass_2018()
    predicted_biomass_2018.to_csv("forecasted_biomass.csv") #required for generated_submission.py
    #predicted_biomass_2019 = predict_biomass_2019(predicted_biomass_2018)
    return predicted_biomass_2018

def main():
    #load input data
    predicted_biomass = predict_biomass()
    print(predicted_biomass)

if __name__ == '__main__':
    main()
