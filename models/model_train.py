from utils.propertieshelper import load_properties
import logging
from models.features import Features
from utils.sqlfunctions import make_connection, load_df
import pandas as pd
import os
import pickle
import json
from utils.sqlhelper import SQLHandler
from sklearn.model_selection import train_test_split, GridSearchCV

logging.basicConfig(format='%(asctime)s [%(filename)s:%(lineno)s - %(module)s:%(funcName)10s() : %(levelname)s] %('
                           'message)s',
                    level=logging.DEBUG)

logger = logging.getLogger(__name__)


class TrainPredictDuration:

    def __init__(self, config_path, model_name):
        model_props = load_properties(config_path, model_name)
        self.non_categorical_features = model_props['non_categorical_features']
        self.target = model_props['target']
        self.test_size = float(model_props['test_size'])
        self.model_output_filepath = model_props['model_output_filepath']
        self.model_result_filepath = model_props['model_result_filepath']
        self.features_filename = model_props['features_filename']
        self.Features = Features(config_path, model_name)
        self.subscr_type = model_props['subscr_type']
        self.drop_columns = model_props['drop_columns']
        self.drop_rows = model_props['drop_rows']

    def data_preparation(self):

        cursor = make_connection()

        df = load_df(cursor, """select aa.*, bb.municipal as start_municipal, bb.lat as start_lat, bb.lng as start_lng,\
                                cc.municipal as end_municipal, cc.lat as end_lat, cc.lng as end_lng from hubway_trips as aa \
                                left join hubway_stations as bb on aa.strt_statn = bb.id \
                                left join hubway_stations as cc on aa.end_statn = cc.id"""
                    )

        weather_df = load_df(cursor, """select * from weather""")

        df[['duration', 'birth_date', 'start_lat', 'start_lng', 'end_lat', 'end_lng']] = df[['duration',
                                                                                            'birth_date',
                                                                                            'start_lat',
                                                                                            'start_lng',
                                                                                            'end_lat',
                                                                                            'end_lng']].apply(pd.to_numeric)
        weather_df['hpcp'] = pd.to_numeric(weather_df['hpcp'])

        df[['start_date', 'end_date']] = df[['start_date', 'end_date']].apply(pd.to_datetime)
        weather_df['date_time'] = weather_df['date_time'].apply(pd.to_datetime)

        df = df[(df['subsc_type'] == self.subscr_type)]
        df = df[(df['duration'] < df['duration'].quantile(0.75)) & (df['duration'] > 0)]
        df.dropna(subset=[col for col in self.drop_rows.split(',')], inplace=True)

        def weather_hpcp(df, weather_df, date):
            new_col_name = date.split("_")[0] + '_hpcp'
            tol = pd.Timedelta(days=3)
            df = pd.merge_asof(df.sort_values(by=date),
                               weather_df[['date_time', 'hpcp']].sort_values(by='date_time').set_index('date_time'),
                               right_index=True,
                               direction='nearest',
                               tolerance=tol,
                               left_on=date)
            df.rename(columns={'hpcp': new_col_name}, inplace=True)
            df[new_col_name] = df[new_col_name].groupby([df[date].dt.month]).transform(lambda x: x.fillna(x.mean()))
            return df

        df = weather_hpcp(df, weather_df, "start_date")
        df = weather_hpcp(df, weather_df, "end_date")

        return df

    def feature_engineering(self, df):
        df['driver_age'] = df.apply(lambda x: self.Features.driver_age(x['birth_date']), axis=1)
        df['driver_age_cat'] = df.apply(lambda x: self.Features.driver_age_category(x['driver_age']), axis=1)
        df['travel_distance'] = df.apply(
            lambda x: self.Features.distance(x['start_lat'], x['start_lng'], x['end_lat'], x['end_lng']), axis=1)
        df['average_speed'] = df.apply(lambda x: self.Features.average_speed(x['travel_distance'], x['duration']), axis=1)
        df = self.Features.temporal_features(df)
        df = self.Features.one_hot_encoding(df)
        df['is_station_diff'] = self.Features.strt_end_diff(df)
        df = self.Features.station_flows(df)
        for col in df.columns:
            if df[col].isna().sum() != 0:
                print(col)
        df.to_csv(os.path.join("data", self.features_filename + '.csv'), index=False)
        return df

    def feature_selection(self, df):
        non_impact_features = ['is_start_11Q4','is_adult','is_start_weekend','is_start_9',
                               'is_start_12Q2','is_start_4','is_start_17','is_young_adult',
                               'is_start_working_day','is_start_12Q3']
        non_categorical_features = [feature for feature in self.non_categorical_features.split(",")]
        X = df[non_categorical_features + list(df.filter(regex='is_').columns)]
        # X = X.drop(X[non_impact_features], axis=1)
        feature_names = list(X.columns)
        y = df[self.target]
        return X, y, feature_names

    def train_test_split(self, X, y):
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=self.test_size, random_state=42)
        return X_train, X_test, y_train, y_test

    def grid_search_train(self, X, y, estimator, param):
        param_grid = {
            "rf_{}".format(self.subscr_type): {
                # "n_estimators": list(range(20, 81, 10)),
                "n_estimators": [80],
                "bootstrap": ['True'],
                "criterion": ['mse'],
                "max_features": ['auto', 'sqrt'],
                "min_samples_leaf": [5]
            },
            "lr_{}".format(self.subscr_type): {
                "normalize": ['True'],
                "alpha": [0.01,0.02,0.03,0.04],
            },
            "gb_{}".format(self.subscr_type): {
                "n_estimators": list(range(20, 81, 10)),
                "learning_rate": [0.01,0.02,0.03,0.04],
                "min_samples_split": [500],
                "min_samples_leaf": [50],
                "max_depth": [4,6,8,10],
                "max_features": ['auto'],
                "subsample": [0.9, 0.5, 0.2, 0.1]
            }
        }
        print(param_grid[param])
        X_train, X_test, y_train, y_test = self.train_test_split(X, y)
        grid_search = GridSearchCV(estimator, param_grid[param], cv=5, n_jobs=-1)
        grid_search.fit(X_train, y_train)
        model = grid_search.best_estimator_
        predictions = model.predict(X_test)
        return model, predictions, y_test

    def save_model(self, model, model_name):
        full_path = os.path.join(self.model_output_filepath, model_name)
        pickle.dump(model, open(full_path, 'wb'))

    def save_output(self, y_pred_test, y_test, output_name):
        results = {"y_pred_test": y_pred_test.tolist(),
                   "y_test": y_test.tolist()}
        with open(os.path.join(self.model_result_filepath, output_name), 'w') as ofile:
            json.dump(results, ofile)

    def post_processing(self):
        data_file_path = "data/" + self.features_filename + ".csv"
        ddl_file_path = "ddls/" + self.features_filename + "_table_create.sql"
        cursor = make_connection()
        with open(ddl_file_path, "r") as file_obj:
            sql_statement = file_obj.read()
        try:
            if SQLHandler().execute_ddl(cursor, sql_statement):
                print("Table Created")
            else:
                print("Skipping table creation")
        except IOError as f_ex:
            print("File {} not accessible, Error message : {}".format(ddl_file_path, f_ex))

        try:
            if SQLHandler().ingest_csv(cursor, data_file_path, self.features_filename):
                print("Data Ingested")
            else:
                print("Please Check CSV File")
        except Exception as ex:
            print("Unable to ingest : {}".format(data_file_path, ex))
        return
