import numpy as np
import pandas as pd
from as3.core.db_utils.db_populate import CourseDataUploader
from as3.core.db_utils.student_report import CreateReportArtifacts, GenerateReport

import sys
import logging
logger = logging.getLogger(__name__)
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
sys.excepthook = handle_exception

data_path = "./as3/static/database_migration_files"
company_data_dir = f"{data_path}/2022 - March 17-18 - Willow Springs - OE"
# obj = CourseDataUploadUtil(company_data_dir)
# print("Data Final Exercise")
# obj.get_data_upload_glimpse()
# print("Countries")
# print(obj.get_countries())
# print("Students")
# print(obj.get_students())
# print("Programs")
# print(obj.get_programs())
# print("Venues")
# print(obj.get_venues())
# print("Course")
# print(obj.get_course())
# print("Vehicles")
# print(obj.get_vehicles())
# print("Comments")
# print(obj.get_comments())
# print("Exercise selected")
# print(obj.get_exercises_selected())
# print("Exercises")
# print(obj.get_exercises())
# print("Data Exercises")
# print(obj.get_data_exercises())
# print("Final data exercises")
# print(obj.get_data_final_exercise())


# from as3.core.db_utils import run
# quit()
# python3 manage.py shell


# Run the pipeline
logger.info("Reading the course")
course_data = CourseDataUploader(company_data_dir)
# course_data.execute()
dfs = course_data.dfs
df_final_exercise = course_data.df_final_exercise
# df_final_exercise.to_csv("df_final_exercise.csv")

create_report = CreateReportArtifacts(dfs, df_final_exercise)
df_student_report, mse_report = create_report.execute()
report_artifacts_global_dict =  create_report.get_global_vars_dict()
# print(report_artifacts_global_dict)

# # # Save data
# # df_student_report.to_csv("df_student_report.csv")
# # mse_report.to_csv("mse_report.csv")
# # np.save('report_artifacts_global_dict.npy', report_artifacts_global_dict) 
# # # Load data
# # df_student_report = pd.read_csv("df_student_report.csv", index_col=0)
# # mse_report = pd.read_csv("mse_report.csv", index_col=0)
# # report_artifacts_global_dict = np.load('report_artifacts_global_dict.npy',allow_pickle='TRUE').item()

generate_report = GenerateReport(dfs, df_final_exercise, report_artifacts_global_dict, df_student_report)
generate_report.generate_student_reports()


# # Namings
# # df_passed_ex_enhance -> counts_df
# # dfs['skill_building_line'] -> course_df
# # dfs['students'] -> students_df
# # df_vehicle_pc_avg -> slalom_avg
# # df_passed_ex -> passed_ex_df
