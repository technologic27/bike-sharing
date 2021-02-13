from utils.propertieshelper import load_properties
import pandas as pd
import numpy as np
from pandas.tseries.holiday import USFederalHolidayCalendar as calendar


class Features:

    def __init__(self, config_path, model_name):
        model_props = load_properties(config_path, model_name)
        self.categorical_features = model_props['categorical_features']

    def driver_age(self, birth_date):
        return int(2013 - birth_date)

    def one_hot_encoding(self, df):
        for category in self.categorical_features.split(","):
            if 'start' == category.split("_")[0]:
                prefix = 'is_start'
            elif 'end' == category.split("_")[0]:
                prefix = 'is_end'
            else:
                prefix = 'is'
            dummies = pd.get_dummies(df['{}'.format(category)], prefix=prefix, dummy_na=False)
            df = pd.concat([df, dummies], axis=1)
        return df

    def strt_end_diff(self, df):
        return np.where((df['strt_statn'] != df['end_statn']), 1, 0)

    def distance(self, s_lat, s_lng, e_lat, e_lng):
        """
        Calculate the distance of latitude and longitude using the great circle distance (haversine)
        Parameters
        ----------
            s_lat: float
                Start latitude.
            s_lng: float
                Start longitude.
            e_lat: float
                End latitude.
            e_lng: float
                End longitude.
        Returns
        -------
            c: float
                Haversine distance in km from start to end latitude
                and longitude.
        """
        rad_lat, rad_lng, rad_pt_lat, rad_pt_lng = map(
            np.radians, [s_lat, s_lng, e_lat, e_lng]
        )
        dlng = rad_lng - rad_pt_lng
        dlat = rad_lat - rad_pt_lat
        a = np.sin(dlat / 2.0) ** 2 + np.cos(rad_lat) * np.cos(rad_pt_lat) \
            * np.sin(dlng / 2.0) ** 2
        c = 2 * np.arcsin(np.sqrt(a))
        return c

    def average_speed(self, distance, time):
        try:
            return distance/time
        except:
            return 0

    def temporal_features(self, df):
        df['start_year'] = df['start_date'].dt.year
        df['start_month'] = df['start_date'].dt.month
        df['start_weekday'] = df['start_date'].dt.weekday
        df['start_hour'] = df['start_date'].dt.hour
        df['end_year'] = df['end_date'].dt.year
        df['end_month'] = df['end_date'].dt.month
        df['end_weekday'] = df['end_date'].dt.weekday
        df['end_hour'] = df['end_date'].dt.hour
        cal = calendar()
        holidays = cal.holidays(start=df['start_date'].min(), end=df['start_date'].max())
        df['is_start_holiday'] = np.where(df['start_date'].isin(holidays), 1, 0)
        df['is_start_working_day'] = np.where((df['start_date'].dt.weekday != 5) & (df['start_date'].dt.weekday != 6) & (df['is_start_holiday'] == 0), 1, 0)
        df['is_start_weekend'] = np.where((df['start_date'].dt.weekday == 5) | (df['start_date'].dt.weekday == 6), 1, 0)
        df['start_year_part'] = df.apply(lambda x: self.year_part(x['start_year'], x['start_month']), axis=1)
        return df

    def year_part(self, year, month):
        if year == 2011 and month <= 3:
            return '11Q1'
        if year == 2011 and month > 3 and month <= 6:
            return '11Q2'
        if year == 2011 and month > 6 and month <= 9:
            return '11Q3'
        if year == 2011 and month > 9 and month <= 12:
            return '11Q4'
        if year == 2012 and month <= 3:
            return '12Q1'
        if year == 2012 and month > 3 and month <= 6:
            return '12Q2'
        if year == 2012 and month > 6 and month <= 9:
            return '12Q3'
        if year == 2012 and month > 9 and month <= 12:
            return '12Q4'
        if year == 2013 and month <= 3:
            return '13Q1'
        if year == 2013 and month > 3 and month <= 6:
            return '13Q2'
        if year == 2013 and month > 6 and month <= 9:
            return '13Q3'
        if year == 2013 and month > 9 and month <= 12:
            return '13Q4'

    def station_flows(self, df):
        in_flow = df.groupby(['strt_statn', 'start_year', 'start_month', 'start_weekday']).size().reset_index(name='daily_in_flow_count')
        out_flow = df.groupby(['end_statn', 'end_year', 'end_month', 'end_weekday']).size().reset_index(name='daily_out_flow_count')
        df = pd.merge(df, in_flow, how="left", on=["strt_statn", 'start_year', 'start_month', 'start_weekday'])
        df = pd.merge(df, out_flow, how="left", on=["end_statn", 'end_year', 'end_month', 'end_weekday'])
        return df

    def driver_age_category(self, age):
        if age > 21 and age <= 40:
            return 'young_adult'
        if age <= 21:
            return 'young'
        if age > 40:
            return 'adult'