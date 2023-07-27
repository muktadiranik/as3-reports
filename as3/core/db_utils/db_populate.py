import os

import pandas as pd
from as3.core.db_utils import db_api, post_processing, utilities
from as3.core.db_utils.errors import raise_assertion_error
from as3.core.db_utils.student_report import CreateReportArtifacts, GenerateReport
import logging
import shortuuid
logger = logging.getLogger(__name__)

class CourseDataUploader:
    def __init__(self, company_data_dir, course_params):
        course_data = ReadProcessCourseDataUtil(company_data_dir)
        # Run the pipeline
        course_data.execute(course_params)
        self.dfs = course_data.dfs
        self.df_vbox = course_data.df_vbox
        self.df_exercise_details = course_data.df_exercise_details
        self.df_final_exercise = self.create_final_exercise_data()
        # self.get_data_upload_glimpse()
    
    def populate_course_students_report(self, report_dir = str(shortuuid.uuid())):
        plot_dir = f"{shortuuid.uuid()}"
        dfs = self.dfs
        df_final_exercise = self.df_final_exercise
        country = dfs['course_generals'].loc[0, 'country']
        # Generate report for specified country
        report_artifacts = CreateReportArtifacts(dfs, df_final_exercise, plot_dir)
        df_student_report, mse_report = report_artifacts.execute()
        report_artifacts_global_dict =  report_artifacts.get_global_vars_dict()
        generate_report = GenerateReport(
            dfs, df_final_exercise, report_artifacts_global_dict, df_student_report, plot_dir)
        generate_report.generate_student_reports(report_dir)
        
        # Generate report for second country
        if country =='MX':
            dfs['course_generals'].loc[0, 'country'] = "USA"
        else:
            dfs['course_generals'].loc[0, 'country'] = "MX"
        report_artifacts = CreateReportArtifacts(dfs, df_final_exercise, plot_dir)
        df_student_report, mse_report = report_artifacts.execute()
        report_artifacts_global_dict =  report_artifacts.get_global_vars_dict()
        generate_report = GenerateReport(
            dfs, df_final_exercise, report_artifacts_global_dict, df_student_report, plot_dir)
        generate_report.generate_student_reports(report_dir)
        
        # Reset the country to the one specified in the course sheet
        dfs['course_generals'].loc[0, 'country'] = country

        report_artifacts_global_dict = {k: '' if v != v else v for k, v in report_artifacts_global_dict.items() }
        
        return (
            df_student_report.to_dict(orient="records"),
            report_artifacts_global_dict,
        )
        
    def get_country(self):
        to_send = self.dfs["course_generals"][["country", "units"]].to_dict(orient="records")
        return to_send[0]
    
    def get_students(self):
        # Students
        df_students = self.dfs["students"].rename(columns={
            "name": "firstName",
            "last name": "lastName",
        }).drop(columns=["fullname"])
        to_send = df_students.to_dict(orient="records")
        return to_send

    def get_program(self):
        to_send = self.dfs["course_generals"][["program"]].rename(
            columns={"program": "name"}
        ).to_dict(orient="records")
        return to_send[0]

    def get_venue(self):
        to_send = self.dfs["course_generals"][["location", "country"]].rename(
            columns={"location": "name"}
        ).to_dict(orient="records")
        return to_send[0]
    
    def get_course(self):
        df_course = self.dfs["course_generals"][["location", "program", "date", "is_open"]].rename(
            columns={"location": "venue", "date": "eventDate"},
        )
        df_course["idealTime"] = int(self.dfs["final_exercise"].loc[0, "ideal_time sec"])
        df_course["conePenalty"] = int(self.dfs["final_exercise"].loc[0, "cone penalty sec"])
        df_course["gatePenalty"] = int(self.dfs["final_exercise"].loc[0, "door penalty sec"])
        to_send = df_course.to_dict(orient="records")
        return to_send[0]
    
    def get_vehicles(self):
        df_vehicles = self.dfs["car_information"][["car", "name", "latacc"]].rename(columns={"car": "car_id"})
        df_vehicles = df_vehicles.drop_duplicates()
        to_send = df_vehicles.to_dict(orient="records")
        return to_send
    
    def get_comments(self):
        # Comments
        to_send = self.dfs["instructor_comments"][["studentId", "comment"]].to_dict(orient="records")
        return to_send

    def get_exercises(self):
        to_send = self.dfs['skill_building'].reset_index()[["exercise"]].to_dict(orient="records")
        return to_send

    def get_exercises_selected(self):
        to_send = self.dfs['skill_building'].reset_index()[["exercise", "chord", "mo"]].to_dict(orient="records")
        return to_send
    
    def get_data_exercises(self):
        to_send = self.dfs['skill_building_line'][
                    ["studentId", "exercise", "car", "speed req", "v1", "v2", "v3", "%_of_exercise", "%_of_vehicle"]
                ].rename(
                    columns={"%_of_vehicle": "pVehicle",
                            "%_of_exercise": "pExercise",
                            "speed req": "speedReq",
                            "car": "vehicle"}
                ).assign(penalties=0)
        return to_send.to_dict(orient="records")
    
    def get_data_final_exercise(self):
        to_send = self.df_final_exercise[
            ["studentId", "stress", "rev_slalom", "slalom", "LnCh", "cones", "gates", "f_time", "final_result", "car"]
            ].rename(
                columns={
                    "rev_slalom": "revSlalom",
                    "LnCh": "laneChange",
                    "f_time": "time", 
                    "final_result": "finalResult",
                    "car": "vehicle"
                }
            )
        to_send[["laneChange", "revSlalom", "finalResult"]] = to_send[["laneChange", "revSlalom", "finalResult"]].fillna(0)
        return to_send.to_dict(orient="records")
    
    def get_data_final_exercise_computed(self):
        df_final_exercise_computed = self.df_final_exercise[
            ["studentId", "stress", "rev_slalom", "slalom", "LnCh", "penalty", "f_time", "final_result", "car"]
            ].rename(
                columns={
                    "rev_slalom": "revSlalom",
                    "LnCh": "laneChange",
                    "f_time": "finalTime",
                    "car": "vehicle",
                    "final_result": "finalResult"
                }
            )
        df_final_exercise_computed = df_final_exercise_computed.loc[df_final_exercise_computed.groupby(by=["studentId"]).finalResult.idxmax()]
        return df_final_exercise_computed.to_dict(orient="records")
    
    def get_data_upload_glimpse(self):
        """
        Glimpse of the final dataset created to show while uploading
        """
        # Convert f_time and rev_slalom to seconds
        
        # Verify is course exist
        course_exist = db_api.course_exists(
            self.dfs["course_generals"].loc[0, "date"], 
            self.dfs["course_generals"].loc[0, "program"],
            self.dfs["course_generals"].loc[0, "location"])
        if course_exist:
            raise_assertion_error("The course already exist for the provided date, program, and location", -1, "Uploading the course")
        
        df_glimpse = self.df_final_exercise.copy()
        
        # Put car info
        cars_map = self.dfs["car_information"].set_index("car")["name"].to_dict()
        cars_new_map = self.dfs["car_information"].set_index("car")["isNew"].to_dict()
        df_glimpse["vehicle_name"] = df_glimpse["car"].map(cars_map)
        df_glimpse["IsNewVehicle"] = df_glimpse["car"].map(cars_new_map)
        # df_glimpse["car_information"].set_index("car")["isNew"].to_dict()
        
        # Name the stress
        df_glimpse["stress"] = df_glimpse["stress"].apply(lambda x: "High" if x==1 else "Low")
        
        # Convert to percent
        # df_glimpse["revPercent"] = df_glimpse["revPercent"]
        
        # Get student's company
        student_company_map = self.dfs["students"].set_index("studentId")["company"].to_dict()
        student_new_map = self.dfs["students"].set_index("studentId")["isNew"].to_dict()
        company_isNew_map = self.dfs["students"].set_index("company")["isCompanyNew"].to_dict()
        df_glimpse["company"] = df_glimpse["studentId"].map(student_company_map)
        df_glimpse["IsStudentNew"] = df_glimpse["studentId"].map(student_new_map)
        df_glimpse["isCompanyNew"] = df_glimpse["company"].map(company_isNew_map)
        to_send = df_glimpse.apply(lambda x: x.fillna("N/A")).to_dict(orient="records")
        return to_send
        
        
    def create_final_exercise_data(self):
        """
        Create the data_final_exercise
        """
        final_exercise_required_cols = ['exercise', 'participant', 'studentId', 'car', 'stress', 'rev_slalom', 'revPercent', 'slalom', 
                                        'LnCh', 'cones', 'gates', 'penalty', 'f_time', 'final_result']
        final_exercise_map = {
            "ideal_time": pd.to_timedelta(self.dfs['final_exercise'].loc[0, 'ideal_time sec'], unit='s'),
            "c_penalty": pd.to_timedelta(self.dfs['final_exercise'].loc[0, 'cone penalty sec'], unit='s'),
            "g_penalty": pd.to_timedelta(self.dfs['final_exercise'].loc[0, 'door penalty sec'], unit='s')    
        }

        df_final_exercise = self.dfs['final_exercise_line'].copy()
        try:
            if "pressure" in df_final_exercise.columns:
                df_final_exercise.rename(columns={"pressure": "stress", "doors": "gates", "time":"g_time"}, inplace=True)
            # Changing types
            df_final_exercise["car"] = df_final_exercise["car"].astype(int)
            df_final_exercise[['stress', 'cones', 'gates']] = df_final_exercise[['stress', 'cones', 'gates']].fillna(0).astype(int)
            
            #Time conversion to Time Delta
            df_final_exercise['g_time'] = pd.to_timedelta(df_final_exercise['g_time'], unit='s')
            
            # Final exercise - final time calculations
            df_final_exercise['final_result'] = df_final_exercise.apply(
                lambda row: post_processing.final_result_calculations(
                    row, final_exercise_map["c_penalty"], final_exercise_map["g_penalty"], final_exercise_map["ideal_time"]), axis=1)
            df_final_exercise['final_result'] = round(df_final_exercise['final_result']*100.0, 2)

            df_final_exercise["f_time"] = df_final_exercise.apply(
                lambda row: row['g_time'] + ((row['cones']*final_exercise_map["c_penalty"]) + (row['gates']*final_exercise_map["g_penalty"])), axis=1)
            df_final_exercise["f_time"] = round(df_final_exercise["f_time"].dt.total_seconds(), 2)

            # Calculate overall Penalty
            df_final_exercise["penalty"] = df_final_exercise.apply(
                lambda row: post_processing.calculate_penalty(
                    row, self.dfs['final_exercise'].loc[0, 'cone penalty sec'], self.dfs['final_exercise'].loc[0, 'door penalty sec']), axis=1)
            
            # Assign df_vbox variables to df_final_exercise
            df_final_exercise['rev_slalom'] = self.df_vbox['rev_slalom']
            df_final_exercise['slalom'] = self.df_vbox['slalom']
            df_final_exercise['LnCh'] = self.df_vbox['LnCh']    
            
            # Remove demo rows
            df_final_exercise = df_final_exercise[df_final_exercise["participant"] != "Demo"]
            
            df_final_exercise['revPercent'] = df_final_exercise.apply(lambda x: round((x['rev_slalom'] / x['g_time']), 2), axis=1)
            df_final_exercise['revPercent'] = round(df_final_exercise['revPercent']*100.0, 2)
            df_final_exercise = df_final_exercise[final_exercise_required_cols].reset_index(drop=True)
            df_final_exercise['rev_slalom'] = df_final_exercise['rev_slalom'].dt.total_seconds().round(2)

            # Verify the dataframe
            # 'rev_slalom', >=0 (IF < 0 THEN == 0)
            df_final_exercise.loc[df_final_exercise['rev_slalom']<0, "rev_slalom"] = 0
            # 'rev_%', >=0 (IF < 0 THEN == 0)
            df_final_exercise.loc[df_final_exercise['revPercent']<0, "revPercent"] = 0
            # 'slalom', >= 0 | <=100 (IF negative == 0 AND IF >100 == 0
            df_final_exercise.loc[df_final_exercise['slalom']<0, "slalom"] = 0
            df_final_exercise.loc[df_final_exercise['slalom']>100, "slalom"] = 0
            # 'LnCh', >= 0 | <=100 (IF negative == 0 AND IF >100 == 0
            df_final_exercise.loc[df_final_exercise['LnCh']<0, "LnCh"] = 0
            df_final_exercise.loc[df_final_exercise['LnCh']>100, "LnCh"] = 0
            # 'cones', >= 0 (else == 0)
            df_final_exercise.loc[df_final_exercise['cones']<0, "cones"] = 0
            # 'gates’, >= 0 (else == 0)
            df_final_exercise.loc[df_final_exercise['gates']<0, "gates"] = 0
            # 'f_time', is TIME_DELTA OR FLOAT > 1 (else [raise error]) (Very important that it has decimals, we use 2 decimals, more are not a problem)
            df_final_exercise.loc[df_final_exercise['f_time']<1, "f_time"] = 0
            # 'final_result' >= 0 (else == 0)
            df_final_exercise.loc[df_final_exercise['final_result']<0, "final_result"] = 0
            df_final_exercise.loc[df_final_exercise['final_result']>100, "final_result"] = 0
            if df_final_exercise.isnull().any(axis=1).any():
                null_vals = df_final_exercise.loc[df_final_exercise.isnull().any(axis=1), "participant"].tolist()
                raise_assertion_error("Error in calculating the final results for students", -1, 
                                      f"Some of the values are missing or invalid while calculating the final results for students {null_vals}")
                
            null_fill_cols = ["rev_slalom", "revPercent", "slalom", "LnCh", "cones", "gates", "final_result"]
            df_final_exercise[null_fill_cols].fillna(0, inplace=True)
            
        except Exception as e:
            raise_assertion_error(str(e), -1, "Getting final exercise data")

        return df_final_exercise

    


class ReadProcessCourseDataUtil:
    def __init__(self, company_data_dir:str):
        if not os.path.exists(company_data_dir) or not os.path.isdir(company_data_dir):
            raise_assertion_error("Extracted zip directory does not exist", -1, f"Error in ReadCourseDataUtil")
            
        # Read company directory
        self.dfs, self.df_exercise_details = self.read_company_data(company_data_dir)
    
    
    def execute(self, course_params: dict):
        """
        Execute the verification and processing pipeline
        """
        
        logger.info("Reading course data files")
        # New change: Replace course_general values to user defined values from UI
        if course_params:
            self.fix_course_generals(course_params)
        # Remove null rows
        self.post_process_meta_data()
        # Post process students
        student_name_id_dict = self.post_process_students()
        # Verify student names
        student_name_id_dict = self.verify_student_names(student_name_id_dict)
        # Post process skill building (line)
        self.post_process_skill_building_line(student_name_id_dict)
        # Post process cars csv data
        self.df_vbox = self.post_process_car_csv_data()
        # Post process final exercise line
        self.post_process_final_exercise(student_name_id_dict)
        # Post process comments line
        self.post_process_comments(student_name_id_dict)
        # Post process vehicles
        self.post_process_vehicles()
        logger.info("Reading course data files successful")
 
    
    def read_company_data(self, company_dir: str):
        """
        Read the company data from excel and csvs
        Args:
            company_dir (str): The directory which contains companies data (sheet and csvs)

        Returns:
            dict of DataFrames in sheet
            dict of DataFrames in all the csvs
        """
        try:
            excel_str_columns = ["location", "program", "client", 
                                 "country", "units", "make", "exercise", 
                                 "name", "last name", 
                            "company", "fullname", "gender", 
                            "participant", "comment"]

            logger.info("Parsing data for company")
            # Get all excel files in a directory
            excel_files = utilities.get_all_files_in_directory(company_dir, "xlsx")
            dfs = utilities.parse_excel_sheet(excel_files[0], utilities.excel_data_map, str_columns=excel_str_columns)
            # Parse csv files in a directory
            vehicle_ids = dfs["final_exercise_line"].car.astype(int).to_list()
            df_exercise_details = utilities.parse_csv_sheet(company_dir, vehicle_ids)
            return dfs, df_exercise_details
        except AssertionError as e:
            raise e
        except Exception as e:
            raise_assertion_error(str(e), -1, "Reading company data")


    def fix_course_generals(self, course_params: dict): 
        """
        Replacing excel values to user-defined values
        """
        try:
            self.dfs['course_generals'].loc[0, 'date'] = pd.to_datetime(course_params['date'])
        except Exception as e:
            raise_assertion_error(str(e), -1, "Parsing course date")
        self.dfs['course_generals'].loc[0, 'location'] = course_params['location']
        self.dfs['course_generals'].loc[0, 'program'] = course_params['program']
        
        print(course_params['client'], self.dfs['course_generals'].loc[0, 'client'])
        
        if 'client' not in course_params or course_params['client'] is None:
            raise_assertion_error("Company not provided", -1, "Please enter the company name during course upload")
        if course_params['client'] != self.dfs['course_generals'].loc[0, 'client']:
            raise_assertion_error("Company name mismatch", -1, "Company name is different in sheet and user input.")
        self.dfs['course_generals'].loc[0, 'client'] = course_params['client']
        if len(self.dfs['course_generals'].loc[0, 'client'])==0:
            self.dfs['course_generals'].loc[0, 'client'] = "Open Enrollment"
        if self.dfs['course_generals'].loc[0, 'client'] == "Open Enrollment":
            self.dfs['course_generals'].loc[0, 'is_open'] = True
        else:
            self.dfs['course_generals'].loc[0, 'is_open'] = False


    def verify_student_names(self, student_name_id_dict):
        """
        Verifies student names in whole sheet.
        
        Args:
            dfs (dict of dataframes): All the dataframes in the Sheet
        """
        student_name_id_dict = utilities.validate_student_name_consistency_driver(self.dfs, student_name_id_dict)
        logger.info("****Student names verified****")
        return student_name_id_dict
    
    
    def post_process_comments(self, student_name_id_dict):
        # Create unique ID for students
        self.dfs['instructor_comments']["studentId"] = self.dfs['instructor_comments'].participant.map(student_name_id_dict)
    
    
    def post_process_meta_data(self):
        # Drop the course with null program
        self.dfs['course_generals'].dropna(subset=["program"], inplace=True)
        # Drop the vehicle with no car information
        self.dfs['car_information'].dropna(subset=["car"], inplace=True)
        # Drop the skills with null chord or mo
        self.dfs['skill_building'].dropna(subset=["chord"], inplace=True)
        self.dfs['skill_building'].dropna(subset=["mo"], inplace=True)  
        # Take only first row in final exercise
        self.dfs["final_exercise"] = self.dfs["final_exercise"].loc[:0].astype(int)
    
    
    def post_process_final_exercise(self, student_name_id_dict):
        # Create unique ID for students
        self.dfs['final_exercise_line']["studentId"] = self.dfs['final_exercise_line'].participant.map(student_name_id_dict)
    
    
    def post_process_car_csv_data(self):
        df_vbox = post_processing.process_cars_csv_data(self.df_exercise_details)
        exercise_radius_map = self.dfs['skill_building']["radius"].to_dict()
        car_lat_acc_map = self.dfs["car_information"].set_index("car")["latacc"].to_dict()
        df_vbox['slalom'] = df_vbox.apply(lambda row: post_processing.mse_slalom_pc(row, car_lat_acc_map, exercise_radius_map), axis=1)
        df_vbox['LnCh'] = df_vbox.apply(lambda row: post_processing.mse_LnCh_pc(row, car_lat_acc_map, exercise_radius_map), axis=1)
        return df_vbox
    
    
    def post_process_skill_building_line(self, student_name_id_dict):
        ## Table `skill_building`
        self.dfs['skill_building'] = self.dfs['skill_building'].set_index("exercise")
        self.dfs['skill_building']['radius'] = self.dfs['skill_building'].apply(lambda row: post_processing.calculate_radius(row), axis=1)
        exercise_radius_map = self.dfs['skill_building']["radius"].to_dict()
        
        ## Table `skill_building_line`
        if self.dfs['skill_building_line']['car'].isnull().any():
            raise_assertion_error("Car column in Skill building sheet is not correct", -1, "Car value must be specified")
        self.dfs['skill_building_line']['car'] = self.dfs['skill_building_line']['car'].astype(int)
        self.dfs['skill_building_line']['cones'] = self.dfs['skill_building_line']['cones'].fillna(0)
        car_lat_acc_map = self.dfs["car_information"].set_index("car")["latacc"].to_dict()

        ## Converting the values to MPH
        # Units of Measure (Metric or Imperial)
        units = self.dfs['course_generals'].loc[0, 'units']
        kms_per_mile = 1.609344
        # Conversion formula 1.609344 kms per mile
        if units == 'MPH':
            pass
        else:
            self.dfs['skill_building_line']['speed req'] = round((self.dfs['skill_building_line']['speed req']/kms_per_mile), 0).astype(int)
            self.dfs['skill_building_line']['v1'] = round((self.dfs['skill_building_line']['v1']/kms_per_mile), 0).astype(int)    
            self.dfs['skill_building_line']['v2'] = round((self.dfs['skill_building_line']['v2']/kms_per_mile), 0).astype(int)    
            self.dfs['skill_building_line']['v3'] = round((self.dfs['skill_building_line']['v3']/kms_per_mile), 0).astype(int)    

        self.dfs['skill_building_line']['%_of_exercise'] = self.dfs['skill_building_line'].apply(lambda row: post_processing.ex_percentage(row), axis=1).astype('float')
        self.dfs['skill_building_line']['%_of_vehicle'] = self.dfs['skill_building_line'].apply(
            lambda row:post_processing.v_percentage(row, car_lat_acc_map, exercise_radius_map), axis=1).astype('float')
        
        self.dfs['skill_building_line'][["%_of_vehicle", "%_of_vehicle"]].fillna(0, inplace=True)
        self.dfs['skill_building_line'].loc[self.dfs['skill_building_line']['%_of_vehicle']<0] = 0
        self.dfs['skill_building_line'].loc[self.dfs['skill_building_line']['%_of_vehicle']>100] = 0
        
        # Create unique ID for students
        self.dfs['skill_building_line']["studentId"] = self.dfs['skill_building_line'].participant.map(student_name_id_dict)
        
        
    def post_process_vehicles(self):
        # Rename `make` to `name`
        if "make" in self.dfs['car_information'].columns:
            self.dfs['car_information'] = self.dfs['car_information'].rename(columns={"make": "name"})
        # Check if vehicle is new
        self.dfs['car_information']["isNew"] = self.dfs['car_information'].apply(lambda row: 
            self.is_new_vehicle(row["name"], row["latacc"]), axis = 1)
     
                
    def post_process_students(self):
        # Convert birthday string to datetime
        self.dfs['students']['birthday'] = pd.to_datetime(self.dfs['students']['birthday'])
        self.dfs['students']['studentId'] = self.dfs['students'].apply(lambda row: post_processing.make_student_id(row), axis=1)
        self.dfs['students']['birthday'] = self.dfs['students']['birthday'].dt.date
        
        # Parent company
        course_company = self.dfs['course_generals'].loc[0, 'client']
        if len(course_company)==0 or course_company=="Open Enrollment":
            self.dfs['students']["company"].fillna("Open Enrollment", inplace=True)
        else:
            self.dfs['students']["company"] = self.dfs['students']["company"].apply(lambda x: course_company)    

        self.dfs['students']["isCompanyNew"] = self.dfs['students']["company"].apply(
            lambda x: True if x=="Open Enrollment" else self.is_new_company(x))

        # Check if student is new
        self.dfs['students']["isNew"] = self.dfs['students']["studentId"].apply(lambda x: self.is_new_student(x))
        student_name_id_dict = self.dfs['students'].set_index("fullname")["studentId"].to_dict()
        return student_name_id_dict

    
    @staticmethod
    def is_new_company(company_name):
        all_companies = db_api.get_companies()
        exisiting_companies = [_["name"] for _ in all_companies]
        return company_name not in exisiting_companies
    
    @staticmethod
    def is_new_student(student_id):
        all_students = db_api.get_students()
        exisiting_student_ids = [_["student_id"] for _ in all_students]
        return student_id not in exisiting_student_ids
        
    @staticmethod
    def is_new_vehicle(name, latacc):
        all_vehicles = db_api.get_vehicles()
        for vehicles in all_vehicles:
            if vehicles["name"] == name:
                if vehicles["latAcc"] != latacc:
                    raise_assertion_error(
                        "Error while reading car data", -1, 
                        f"Car {name} exist with Lat Acc {vehicles['latAcc']}. Please check the entries"
                    )
                return False
        return True
