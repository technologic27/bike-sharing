from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error, r2_score
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from models.model_train import TrainPredictDuration
import stats
import numpy as np


def get_prediction_interval(prediction, y_test, test_predictions, pi=.95):
    """
    Get a prediction interval for a linear regression.

    INPUTS:
        - Single prediction,
        - y_test
        - All test set predictions,
        - Prediction interval threshold (default = .95)
    OUTPUT:
        - Prediction interval for single prediction
    """
    # get standard deviation of y_test
    sum_errs = np.sum((y_test - test_predictions) ** 2)
    stdev = np.sqrt(1 / (len(y_test) - 2) * sum_errs)
    # get interval from standard deviation
    one_minus_pi = 1 - pi
    ppf_lookup = 1 - (one_minus_pi / 2)
    z_score = stats.norm.ppf(ppf_lookup)
    interval = z_score * stdev
    # generate prediction interval lower and upper bound
    lower, upper = prediction - interval, prediction + interval
    return lower, prediction, upper


def main():

    estimators = [('lr', Ridge())]

    backup = [('gb', GradientBoostingRegressor()),('rf', RandomForestRegressor())]

    run = TrainPredictDuration('resource/config.ini', 'model')
    subscr_type = run.subscr_type
    df = run.data_preparation()
    df = run.feature_engineering(df)
    X, y, feature_names = run.feature_selection(df)
    print(feature_names)

    for estimator in estimators:
        model_name = estimator[0]+'_{}'.format(subscr_type)
        model, y_pred, y_test = run.grid_search_train(X, y, estimator[1], model_name)
        print('{}-MSE: '.format(model_name), mean_squared_error(y_test, y_pred))
        print('{}-MAPE: '.format(model_name), mean_absolute_percentage_error(y_test, y_pred))
        print('{}-R2: '.format(model_name), r2_score(y_test, y_pred))
        run.save_model(model, '{}.sav'.format(model_name))
        run.save_output(y_pred, y_test, '{}.json'.format(model_name))

        if model_name == 'lr'+'_{}'.format(subscr_type):
            for idx, value in enumerate(feature_names):
                print(value+': ', round(model.coef_[idx], 5))


if __name__ == "__main__":
    main()