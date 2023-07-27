import pandas as pd
from as3.core.db_utils.errors import raise_assertion_error


# Table `skill_building`
def calculate_radius(row):
    try:
        x = row['chord']
        y = row['mo']
        radius = (x**2) / (8*y) + (y/2)
        return radius
    except Exception as e:
        raise_assertion_error(message=str(e), row=row.name+1, method="Calculting Radius")
        

# Table `skill_building_line`
def ex_percentage(row):
    """
    Everything in the MPH
    """
    try:
        x = row[['v1', 'v2', 'v3']].mean()
        sd = row[['v1', 'v2', 'v3']].std()
        cns = row['cones']
        y = round(x, 2)
        z = row['speed req']
        p = ((y / z))
        res = 0
        if sd < 3 and cns == 0:
            res = round(p, 2)
        return res
    except Exception as e:
        raise_assertion_error(str(e), row.name+1, "Calculating ex percentage")

def v_percentage(row, car_lat_acc_map, exercise_radius_map):
    """
    Calculate %_of_vehicles. Everything in the MPH
    Note: Depends on car_lat_acc_map, and dfs['skill_building']['radius']
    """
    try:
        vx = row[['v1', 'v2', 'v3']].mean()
        sd = row[['v1', 'v2', 'v3']].std()
        ex = row['exercise']
        R = exercise_radius_map[ex.strip()]
        v = round(vx, 2)
        LA = ((v**2) / (R*15))
        res = round(LA, 2)/car_lat_acc_map[row["car"]]
        if res < 1:
            pass
        else:
            res = 0
        if sd < 3:
            pass
        else:
            res = 0
        return res
    except Exception as e:
        raise_assertion_error(str(e), row.name+1, "Calculating v percentage")


# Table `final_exercise`
def final_result_calculations(row, c_penalty, g_penalty, ideal_time):
    """
    Uses data from `final_exercise`. Final exercise - final time calculations
    Note: Not used
    """
    try:
        cns = row['cones']
        gts = row['gates']
        tme1 = row['g_time']
        g_tme = (tme1 + (cns * c_penalty) + (gts * g_penalty))
        f_time = (-(((g_tme / ideal_time)*100)-200)/100)
        if f_time > .2:
            f_time = round(f_time, 2)
        else:
            f_time = 0
        return f_time
    except Exception as e:
        raise_assertion_error(str(e), row.name+1, "Calculating final result calculations")

# Calculate overall penalty
def calculate_penalty(row, c_penalty, g_penalty):
    try:
        cns = row['cones']
        gts = row['gates']
        penalty = (1 + (cns * c_penalty) + (gts * g_penalty))
        return penalty
    except Exception as e:
        raise_assertion_error(str(e), row.name+1, "Calculating penalty")

# Table `students`
def make_student_id(row):
    try:
        unique_id = "{}{}{}{}".format(
            row['last name'][0].upper(),
            row['last name'][-1].upper(),
            row['name'][0].upper(),
            row['birthday'].strftime('%Y%m%d')
        )
        return unique_id
    except Exception as e:
        raise_assertion_error(str(e), row.name+1, "Making student id")


# Vehicle csv's processing
def process_cars_csv_data(df_exercise_details):
    csv_car_results = list()
    for car in df_exercise_details:
        try:
            c_df = df_exercise_details[car]['exercise'].rename(
                columns={
                    'UTC time (At Start)':'UTC_Time',
                    'Time (s)' : 'rev_slalom'
                }
            )
            c_df['car'] = car
            c_time = c_df[['car', 'rev_slalom', 'UTC_Time']][::3].reset_index(drop=True)
            speed_unit = "mph" if c_df.columns[2].find("mp")!=-1 else "kmph"
            c_slalom = c_df.iloc[1::3, 2:4].reset_index(drop=True)
            c_slalom.columns = ['slalom_avg', 'slalom_std_dev']
            c_LnCh = c_df.iloc[2::3, 2:4].reset_index(drop=True)
            c_LnCh.columns = ['LnCh_avg', 'LnCh_std_dev']
            # Frame variables
            c_frames = [c_time, c_slalom, c_LnCh]
            # Final DataFrames
            c_result = pd.concat(c_frames, join='inner', axis=1)
            # Creating Time Deltas
            c_result['rev_slalom'] = c_result['rev_slalom'].astype(float)
            c_result['rev_slalom'] = pd.to_timedelta(c_result['rev_slalom'], unit='s')
            # Converting time to datetime64
            c_result['UTC_Time'] = (pd.to_datetime(c_result['UTC_Time'], utc=True, format=('%H:%M:%S.%f')).dt.tz_convert('US/Pacific').dt.time)
            # Changind types to float
            float_type_cols = ['slalom_avg', 'slalom_std_dev', 'LnCh_avg', 'LnCh_std_dev']
            c_result[float_type_cols] = c_result[float_type_cols].astype(float)
            if speed_unit == "kmph":
                c_result[float_type_cols] = c_result[float_type_cols]/1.609344
            c_result[float_type_cols].fillna(0.0, inplace=True)
            c_result.rename(columns={'car' : 'car_ID'}, inplace=True)
            c_result['car_ID'] = c_result['car_ID'].astype(int)
            csv_car_results.append(c_result)
        except Exception as e:
            raise_assertion_error(str(e), -1, f"Processing cars csv data for car id {car}")
        
    # Creating a sigle DataFrame
    df_vbox = pd.concat(csv_car_results, ignore_index=True).sort_values(by=['UTC_Time']).reset_index().drop(['index'], axis=1)
    return df_vbox

# MSE slalom and LnCh percentages
def mse_slalom_pc(row, car_lat_acc_map, exercise_radius_map):
    try:
        vx = row['slalom_avg']
        ex = 'Slalom'
        R = exercise_radius_map[ex.strip()]
        v = round(vx, 2)
        LA = ((v**2) / (R*15))
        if LA >= car_lat_acc_map[row["car_ID"]]:
            res = 0
        else:
            res = round(LA, 2) / car_lat_acc_map[row["car_ID"]]
        return int((round(res, 2))*100)
    except Exception as e:
        raise_assertion_error(str(e), row.name+1, "Calcuting MSE Slalom percentages")

def mse_LnCh_pc(row, car_lat_acc_map, exercise_radius_map):
    try:
        vx = row['LnCh_avg']
        ex = 'Lane Change'
        R = exercise_radius_map[ex.strip()]
        v = round(vx, 2)
        LA = ((v**2) / (R*15))

        if LA >= car_lat_acc_map[row["car_ID"]]:
            res = 0
        else:
            res = round(LA, 2) / car_lat_acc_map[row["car_ID"]]

        return int((round(res, 2))*100)
    except Exception as e:
        raise_assertion_error(str(e), row.name+1, "Calcuting MSE Lance Change percentages")
