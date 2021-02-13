CREATE TABLE hubway_trips (
    seq_id text,
    hubway_id text,
    status text,
    duration int8,
    start_date timestamp,
    strt_statn text,
    end_date text,
    end_statn text,
    bike_nr text,
    subsc_type text,
    zip_code text,
    birth_date int8,
    gender text,
    start_municipal text,
    start_lat float8,
    start_lng float8,
    end_municipal text,
    end_lat float8,
    end_lng float8,
    start_hpcp int8
    end_hpcp int8
);
seq_id,hubway_id,status,duration,start_date,strt_statn,end_date,end_statn,bike_nr,subsc_type,zip_code,birth_date,gender,start_municipal,start_lat,start_lng,end_municipal,end_lat,end_lng,end_hpcp,driver_age,
travel_distance,average_speed,is_station_diff,start_weekday,start_hour_weekofyear,start_hour,end_hour,is_holiday