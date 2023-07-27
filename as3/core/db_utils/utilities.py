import pandas as pd
import os
import math
import json
import numpy as np

import unidecode
from collections import Counter
import re
from as3.core.db_utils.errors import raise_assertion_error
from as3.core.db_utils import DB_UTILS_STATIC_DATA

import logging
logger = logging.getLogger(__name__)

"""
***************************************************** Reading True Data *****************************************************
"""
# Reading true data
data_map_path = os.path.join(DB_UTILS_STATIC_DATA, "data_map.json")
columns_inconsistencies_path = os.path.join(DB_UTILS_STATIC_DATA, "columns_inconsistencies.json")
logger.info(data_map_path)

with open(data_map_path) as file:
    data_map = json.load(file)
excel_data_map = data_map["excel"]["sheets"]

with open(columns_inconsistencies_path) as file:
    columns_inconsistencies = json.load(file)


"""
***************************************************** Validation utilities *****************************************************
"""
def validate_num_tables_in_sheet(true_value, expected_value):
    if expected_value!=true_value:
        raise_assertion_error("Inconsisteny in `data_map.json`", -1, f"The expected number of tables must be \
                '{expected_value}' but data is available for only {true_value} tables")
    
    
def validate_sheet_size(sheet_name, true_value, expected_value=1):
    if not (true_value>=expected_value):
        raise_assertion_error(f"Error in method `validate_sheet_size` ", -1, f"Sheet '{sheet_name}' has no data")
    

def validate_and_resolve_columns_inconsistencies(true_columns, expected_columns):
    new_true_columns = true_columns.copy()
    new_true_columns = [columns_inconsistencies[col] if col in columns_inconsistencies else col for col in true_columns]
    mismatch_columns = set(expected_columns).difference(set(new_true_columns))
    if len(mismatch_columns)>0:
        return []
    return new_true_columns


def validate_table_columns(sheet_name, true_value, expected_value):
    try:
        true_columns = pre_process_columns(true_value)
        expected_columns = pre_process_columns(expected_value)
        true_columns = validate_and_resolve_columns_inconsistencies(true_columns, expected_columns)
        # Checking if expected columns match
        if len(true_columns)==0 and len(expected_columns)==0 and len(set(expected_columns).difference(set(true_columns)))!=0:
            raise_assertion_error("Error in method `validate_and_resolve_columns_inconsistencies`", -1, 
                                f"The columns in sheet '{sheet_name}' are not matched. Expected columns must be '{expected_columns}'")
        return true_columns, expected_columns
    except AssertionError as e:
        raise e
    except Exception as e:
        raise_assertion_error(str(e), -1, "Error in validating table columns")


def spanish_to_english(value):
    try:
        value = "".join(str(value).lower().split(" "))
        # Decode string to nearest unicode
        value = unidecode.unidecode(value)
        return value
    except Exception as e:
        raise_assertion_error(str(e), -1, "Error in converting Spanish to English")


def validate_student_name_consistency_helper(sheet_name, true_names, apparent_names, student_name_id_dict):
    """
    Verifies the student names in the both lists. In case of mismatch in the `apparent_names`, through an assertion error with row number and name
    
    @input
    sheet_name -> Name of the sheet
    true_names -> List of ground truth names (may be duplicate but not always)
    apparent_names -> List of apparent names (may contain duplicates)
    
    @output
    True if matches, else False
    """
    
    try:
        # Test each name in aparent_name
        for i in range(len(apparent_names)):
            apparent_name = apparent_names[i]
            if apparent_name not in true_names and apparent_name!="Demo":
                # Try more advanced methods
                found = False
                for true_name in true_names:
                    if spanish_to_english(true_name)==spanish_to_english(apparent_name):
                        found = True
                        if apparent_name not in student_name_id_dict:
                            student_name_id_dict[apparent_name] = student_name_id_dict[true_name]
                        break
                if not found:
                    raise_assertion_error("Error in method `validate_student_name_consistency_helper`", 
                                          i, f"Student name {apparent_name} not found in sheet {sheet_name}")
        return student_name_id_dict
    except AssertionError as e:
        raise e
    except Exception as e:
        raise_assertion_error(str(e), -1, "Error in validating student name")


def validate_student_name_consistency_driver(dataframe_dict, student_name_id_dict): 
    """
    Validates the student names in the whole sheet
    """
    
    # Test for student name consistency in a company's data
    ## Test Student data in `Skill Building`
    try:
        true_names = dataframe_dict["students"].fullname.to_list()
        apparent_names = dataframe_dict["skill_building_line"].participant.to_list()
        student_name_id_dict = validate_student_name_consistency_helper("Skill Building", true_names, apparent_names, student_name_id_dict)

        ## Test Student data in `Final Exercise`
        apparent_names = dataframe_dict["final_exercise_line"].participant.to_list()
        student_name_id_dict = validate_student_name_consistency_helper("Final Exercise", true_names, apparent_names, student_name_id_dict)

        ## Test Student data in `Instructor Comments`
        apparent_names = dataframe_dict["instructor_comments"].participant.to_list()
        student_name_id_dict = validate_student_name_consistency_helper("Instructor Comments", true_names, apparent_names, student_name_id_dict)
        
        # Add demo in dict
        student_name_id_dict['Demo'] = "Demo"
        return student_name_id_dict
    except AssertionError as e:
        raise e
    except Exception as e:
        raise_assertion_error(str(e), -1, "Error in validating student name driver")
    
    

"""
***************************************************** Helper utilities *****************************************************
"""
def get_all_files_in_directory(dir_name, file_extension):
    """
    Get all the files in a given company directory
    
    @input
    dir_name: Name of company directory
    file_extension: The file extension to read
    
    @output
    List of files in a directory
    """
    try:
        if os.path.exists(dir_name):
            all_paths = os.walk(dir_name)
            allowed_files = list()
            for (dir_path, dir_names, file_names) in all_paths:
                for file in file_names:
                    if file.split(".")[-1] == file_extension:
                        allowed_files.append(f"{dir_path}/{file}")
    
            if len(allowed_files) < 1:
                raise_assertion_error(f"Zip file must contain required xlsx and csv file.", -1, "Reading Zip")
                
            return allowed_files
    except AssertionError as e:
        raise e
    except Exception as e:
        raise_assertion_error(str(e), -1, f"Failed while reading Zip.")


def pre_process_columns(columns):
    return [_.replace(r"#", "").strip().lower() for _ in columns]


def parse_excel_sheet(excel_file_path, excel_data_map, str_columns):
    """
    Parse the given excel sheet.
    Note: All `student` is replaced with `participant`
    
    @input
    excel_file_path -> File path for the excel file
    excel_data_map -> Ground truth map for excel file
    str_columns -> Columns names which must be converted to str
    
    @output
    Returns all the tables in the excel file
    """
    
    if not os.path.exists(excel_file_path) and excel_file_path.split(".")[-1]!='xlsx':
        raise_assertion_error("Error in method `parse_excel_sheet`", -1, "Excel file doesn't exist or incorrect file extension")
        
    # Read excel file
    excel_data = pd.ExcelFile(excel_file_path)
    
    logger.info("****Verifying the excel file****")
    # Test for sheet names
    expected_sheet_names = [_["sheet_name"] for _ in excel_data_map]
    actual_sheets_names = excel_data.sheet_names
    if len(set(actual_sheets_names).intersection(set(expected_sheet_names)))!=len(expected_sheet_names):
        raise_assertion_error("Error in method `parse_excel_sheet`", -1, f"Sheet names does not match. Current allowed values are: {expected_sheet_names}")
        
    full_excel_dict = dict()
    for _ in excel_data_map:
        try:
            sheet_name = _["sheet_name"]
            header = _["header"]
            num_tables = _["num_table"]
            validate_num_tables_in_sheet(true_value=len(_["meta_data"]), expected_value=num_tables)

            # Do not read the sheet if it is not required
            if "required" in _ and not _["required"]:
                continue
            for i in range(num_tables):
                # Do not read the sheet if it is not required
                if "required" in _ and not _["meta_data"][i]["required"]:
                    continue
                table_name = _["meta_data"][i]["table_name"]
                non_null_col = None
                if "non_null_col" in _["meta_data"][i]:
                    non_null_col = _["meta_data"][i]["non_null_col"]
                
                sheet = pd.read_excel(excel_data, sheet_name, header=header)
                validate_sheet_size(sheet_name, sheet.shape[0], 1)

                true_columns = list(sheet.columns)
                expected_columns = list(_["meta_data"][i]["columns"].keys())
                true_columns, expected_columns = validate_table_columns(sheet_name, true_columns, expected_columns)
                
                # Read the table
                sheet.columns = true_columns
                df = sheet.loc[:, expected_columns]
                df.columns = expected_columns
                # Put NaN for empty rows
                for col in df.columns:
                    df[col] = df[col].apply(lambda x: np.NaN if len(str(x).strip())==0 else x)
                
                # pre-process certain columns
                for col in df.columns:
                    if col in str_columns:
                        df[col] = df[col].apply(lambda x: x.strip() if type(x)==str else x)
                
                # Remove rows with null data for non null column
                df = df.dropna(subset=[non_null_col])
                
                logger.info(f"=> Sheet '{sheet_name}',\n table: '{table_name}' verified and read. \
                    \nThe columns are: {expected_columns}. \nTotal rows: {df.shape[0]}")
                full_excel_dict[table_name] = df
        except AssertionError as e:
            raise e
        except Exception as e:
            raise_assertion_error(str(e), -1, f"Error in parsing excel sheet {sheet_name}")
            
    logger.info("****Verified and read the excel file's metadata successfully****")
    
    return full_excel_dict


def parse_csv_sheet(company_directory, final_exercise_vehicle_ids):
    """
    Pase the given csv sheet. The sheet represents a final exercise. 
    It links the final_exercise_line with csv by a factor of 3
    
    @input
    company_directory -> Company's directory for all the csv file path
    final_exercise_vehicle_ids -> All the vehicle ids in the final_exercise_line dataframe
    
    @output
    Returns all the csv data with format:
    {
        vehicle_id: {
            "exercise": pd.DataFrame,
            "exercise_agg": pd.DataFrame,
        }
    }
    """
    
    csv_file_paths = get_all_files_in_directory(company_directory, "csv")
    if len(csv_file_paths)==0:
        raise_assertion_error("Error in method `parse_csv_sheet`", -1, "There is no csv file in the company directory")
    
    expected_csvs = set(final_exercise_vehicle_ids) 
    true_csvs = list()
    for csv_file_path in csv_file_paths:
        csv_file_name = csv_file_path[csv_file_path.rindex("/")+1:]
        try:
            true_csvs.append(int(csv_file_name.lower().split(".")[-2][-1]))
        except Exception as e:
            raise_assertion_error(str(e), -1, f"Error in parsing CSV filename {csv_file_name}. The file name should end with vehicle ID")
    true_csvs = set(true_csvs)

    if len(true_csvs) < len(expected_csvs):
        missing_csvs = expected_csvs.difference(true_csvs)
        raise_assertion_error("Error in method `parsing csvs`", -1, f"The zip does not contain csvs for vehicles {missing_csvs}")
    elif len(true_csvs)>len(expected_csvs):
        extra_csvs = true_csvs.difference(expected_csvs)
        raise_assertion_error("Error in method `parsing csvs`", -1, f"The zip contain extra csvs for vehicles {extra_csvs}")    

    exercise_data = dict()
    student_counts_for_vehicle_dict = dict(Counter(final_exercise_vehicle_ids))
    logger.info(f"****Total student counts in a vehicle: {student_counts_for_vehicle_dict}****")
    for csv_file_path in csv_file_paths:
        _csv_file = csv_file_path.split("/")[-1]
        try:
            vehicle_id = int(csv_file_path.split(".")[-2][-1])
            logger.info(f"****Reading data for vehicle id {vehicle_id}****")
            if vehicle_id not in student_counts_for_vehicle_dict:
                error = {
                    "message": f"File {_csv_file} does not have vehicle id in it's name. \
                        Expected v1 or v2 or v3 .. as suffix in file name"
                }
                raise AssertionError(error)
            num_students = student_counts_for_vehicle_dict[vehicle_id]
            expected_rows = num_students*3
            with open(csv_file_path, "r") as file:
                exercise_date = file.readline()
                exercise_date = re.findall(r"[0-9]{2}/[0-9]{2}/[0-9]{4} [0-9]{2}:[0-9]{2}", exercise_date)[0]

            df = pd.read_csv(csv_file_path, skiprows=1)
            # Add test date columns
            df["Test Date"] = exercise_date

            # Remove last 4 rows
            df_exercise = df.iloc[:-4, :]
            df_exercise_agg = df.iloc[-4:, :]

            # Test if exercise have correct number of results
            difference = df_exercise.shape[0] - expected_rows
            logger.info(f"Total row difference in csv: {difference}")
            if difference>0:
                error = {
                    "message": f"Data could not be registered. There are {difference} number of extra rows in sheet \
                        {_csv_file}"
                }
                raise AssertionError(error)
            elif difference<0:
                error = {
                    "message": f"Data could not be registered. There are {-difference} rows missing in sheet {_csv_file}"
                }
                raise AssertionError(error)
                
            exercise_data[vehicle_id] = {
                "exercise": df_exercise,
                "exercise_agg": df_exercise_agg
            }
        except AssertionError as e:
            raise e
        except Exception as e:
            raise_assertion_error(str(e), -1, f"Error in parsing csv file {_csv_file}")
    
    return exercise_data