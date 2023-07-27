import json
import os
from functools import partial
import shortuuid
import shutil
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from as3.core.db_utils import DB_UTILS_STATIC_DATA
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from PIL import Image as pImage
from reportlab.lib import colors, utils
from reportlab.lib.fonts import addMapping
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle as PS
from reportlab.lib.units import cm, inch
from reportlab.pdfbase.pdfmetrics import registerFont, registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Flowable, Image, NextPageTemplate, PageBreak,
                                Spacer, Table, TableStyle)
from reportlab.platypus.doctemplate import BaseDocTemplate, PageTemplate
from reportlab.platypus.frames import Frame
from reportlab.platypus.paragraph import Paragraph
import warnings
import logging

logger = logging.getLogger(__name__)
warnings.filterwarnings("ignore")

from django.conf import settings
static_root = settings.STATIC_ROOT + "/reports"
media_root = settings.MEDIA_ROOT + "/reports"
assets_dir = settings.STATIC_ROOT + "/assets"
plots_dir = settings.MEDIA_ROOT + "/reports/plots"

# media_root = "./" + f"reports-{str(shortuuid.uuid())}/"
# static_root = "./as3/static/reports"
# assets_dir = "./as3/static/assets"
# plots_dir = "./as3/static/reports/plots"


class CreateReportArtifacts():
    def __init__(self, dataframes, df_final_exercise, plots_path_str):
        """
        Dataframes contains all the read artifacts from sheets. df_final_exercise holds the final processed data for a course
        """
        self.dfs = dataframes
        self.df_final_exercise = df_final_exercise
        self.plots_path = os.path.join(plots_dir, plots_path_str)
        
    def create_global_variables(self, df_passed_ex_enhance, df_skill_building, df_final_exercise, df_final_exercise_meta):
        global_vars = dict()
        # Group Variables
        global_vars['gasnor'] = int((df_passed_ex_enhance['count']['Slalom'].agg('mean'))) # group_average_slalom_runs
        global_vars['gaspoce'] = int((df_passed_ex_enhance['Slalom Passed'].mean())*100) # group_average_slalom_prcnt_completed
        global_vars['gasaoep'] = int(((df_passed_ex_enhance['av_score']['Slalom'].mean())*100)) # group_average_slalom_ex_prcnt
        global_vars['gasaovc'] = int((df_skill_building.loc[df_skill_building['exercise'] == 'Slalom']['%_of_vehicle'].mean())*100) # group_average_slalom_vehicle_control
        global_vars['galnor'] = int((df_passed_ex_enhance['count']['Lane Change'].agg('mean'))) #.astype(int) # group_average_lnch_runs
        global_vars['galpoce'] = int((df_passed_ex_enhance['LnCh Passed'].mean())*100) # group_average_lnch_prcnt_completed
        global_vars['galaoep'] = int(((df_passed_ex_enhance['av_score']['Lane Change'].mean())*100)) # group_average_lnch_ex_prcnt
        global_vars['galaovc'] = int((df_skill_building.loc[df_skill_building['exercise'] == 'Lane Change']['%_of_vehicle'].mean())*100) # group_average_lnch_vehicle_control
        mseg_t_pre = str(df_final_exercise['f_time'].mean())
        global_vars['mseg_t'] = mseg_t_pre[mseg_t_pre.find(':')+1 : mseg_t_pre.find('.')+3 : ] # mse_group_av_time
        global_vars['mseg_c'] = int((df_final_exercise['cones'].mean())) # mse_group_av_cones
        global_vars['mseg_g'] = int((df_final_exercise['gates'].mean())) # mse_group_av_gates
        global_vars['mseg_perf'] = int((df_final_exercise['final_result'].mean())) # mse_group_av_performance
        global_vars['mseg_per'] = int((df_final_exercise['final_result'].quantile())) # mse_group_av_percentile
        global_vars['mse_obj'] = str(pd.to_timedelta(df_final_exercise_meta.loc[0, 'ideal_time sec'], unit='s'))[10:] # mse_objective_obj
        mseg_rev_pre = df_final_exercise['rev_slalom'].mean() # strings mse_group_used_in_rev
        mseg_rev_pre = "%.2f" % mseg_rev_pre
        global_vars['mseg_rev'] = mseg_rev_pre
        
        if "revPercent" in df_final_exercise:
            global_vars['mseg_rev_pc'] = int(round((df_final_exercise['revPercent'].mean()), 0))
        else:
            global_vars['mseg_rev_pc'] = int(round((df_final_exercise['rev_%'].mean()), 0))
            
        global_vars["msed_per"]= np.nan # MSE Driver Percentile (Quantile)
        global_vars["msed_rev"] = np.nan # MSE Driver % Used in Reverse
        global_vars["msed_rev_time"] = np.nan # MSE Driver Reverse Time
        global_vars["paragraph"] = np.nan # Lead Instructor Feedback
        
        return global_vars
    
    
    def execute(self):
        df_passed_ex = self.get_passed_exercise_data(self.dfs['skill_building_line'])
        df_passed_ex_enhance = self.get_passed_exercise_enhance_data(self.dfs['skill_building_line'])
        df_vehicle_pc_avg = self.get_vehicle_pc_average_data(self.dfs['skill_building_line'])
        # Generate static variables
        global_vars_dict = self.create_global_variables(df_passed_ex_enhance, self.dfs['skill_building_line'], 
                                                        self.df_final_exercise, self.dfs['final_exercise'])
        self.set_global_vars_dict(global_vars_dict)
        global_vars_dict['country'] = self.dfs['course_generals'].loc[0, 'country']
        if "make" in self.dfs['car_information']:
            global_vars_dict['make'] = self.dfs['car_information'].loc[0, 'make']
        else:
            global_vars_dict['make'] = self.dfs['car_information'].loc[0, 'name']
        global_vars_dict['program'] = self.dfs['course_generals'].loc[0, 'program']
        global_vars_dict['course_date'] = self.dfs['course_generals'].loc[0, 'date']
        global_vars_dict['latacc'] = self.dfs['car_information'].loc[0, 'latacc']
        df_report, mse_report = self.create_report_dataframe(self.dfs['students'], df_passed_ex_enhance, df_vehicle_pc_avg, df_passed_ex, global_vars_dict)
        return df_report, mse_report
        
    def create_report_dataframe(self, df_students, df_passed_ex_enhance, df_vehicle_pc_avg, df_passed_ex, global_vars_dict):
        #Final report DataFrame Lineup
        df_report = pd.DataFrame(df_students, columns=['fullname', 'studentId', 'company'])
        df_report['program'] = global_vars_dict['program']
        df_report['date'] = global_vars_dict['course_date']

        # Versiones en ambos idiomas
        if global_vars_dict['country'] == 'MX':
            df_report['vehicle'] = (global_vars_dict['make'] + ' (Capacidad ' + global_vars_dict['latacc'].astype(str) + 'g)')
        else:
            df_report['vehicle'] = (global_vars_dict['make'] + ' (' + global_vars_dict['latacc'].astype(str) + 'g Capability)')

        # Slalom variables
        df_vehicle_pc_avg.fillna(0, inplace=True)
        df_report['s_no_runs'] = pd.merge(left=df_report, right=(df_passed_ex_enhance['count']['Slalom']).astype(int), left_on='studentId', right_index=True)['Slalom']
        df_report['s_passed'] = pd.merge(left=df_report, right=df_passed_ex_enhance['passed']['Slalom'], left_on='studentId', right_index=True)['Slalom']
        df_report['prcnt_s_pass'] = pd.merge(left=df_report, right=round((df_passed_ex_enhance['Slalom Passed'])*100, 0), left_on='studentId', right_index=True)['Slalom Passed']
        df_report['avg_ex_control_s'] = pd.merge(left=df_report, right=round((df_passed_ex_enhance['av_score']['Slalom'])*100, 0), left_on='studentId', right_index=True)['Slalom']
        df_report['avg_v_control_s'] = pd.merge(left=df_report, right=round((df_vehicle_pc_avg['vehicle_pc_avg']['Slalom'])*100, 0), left_on='studentId', right_index=True)['Slalom']
        df_report['slalom_max'] = pd.merge(left=df_report, right=round((df_passed_ex['end_score']['Slalom'])*100), left_on='studentId', right_index=True)['Slalom']
        #LnCh Variables
        df_report['lc_no_runs'] = pd.merge(left=df_report, right=(df_passed_ex_enhance['count']['Lane Change']).astype(int), left_on='studentId', right_index=True)['Lane Change']
        df_report['lc_passed'] = pd.merge(left=df_report, right=df_passed_ex_enhance['passed']['Lane Change'], left_on='studentId', right_index=True)['Lane Change']
        df_report['prcnt_lc_pass'] = pd.merge(left=df_report, right=round((df_passed_ex_enhance['LnCh Passed'])*100, 0), left_on='studentId', right_index=True)['LnCh Passed']
        df_report['avg_ex_control_lc'] = pd.merge(left=df_report, right=round((df_passed_ex_enhance['av_score']['Lane Change'])*100, 0), left_on='studentId', right_index=True)['Lane Change']
        df_report['avg_v_control_lc'] = pd.merge(left=df_report, right=round((df_vehicle_pc_avg['vehicle_pc_avg']['Lane Change'])*100, 0), left_on='studentId', right_index=True)['Lane Change']
        df_report['lnch_max'] = pd.merge(left=df_report, right=round((df_passed_ex['end_score']['Lane Change'])*100), left_on='studentId', right_index=True)['Lane Change']
        
        # Including the right comments
        student_comment_map = self.dfs["instructor_comments"].set_index("studentId")["comment"].to_dict()
        df_report["comments"] = df_report["studentId"].map(student_comment_map)
        # Prepare MSE data
        mse_report = self.create_mse_report_data(self.df_final_exercise, global_vars_dict['country'])
        # Read jinga variables
        jinga_path = "./as3/static/reports"
        tmplt_data = pd.read_excel(f'{jinga_path}/jinja_variables.xlsx', skiprows=2)
        tmplt_context = dict(zip(tmplt_data['var'], tmplt_data['value']))
        self.create_all_student_graphs(global_vars_dict, self.df_final_exercise, df_report, mse_report, tmplt_context)
        return df_report, mse_report
        
    
    def get_skill_building_student_data(self, studentId, exercise, result_column):
        return self.dfs['skill_building_line'].loc[
            ((self.dfs['skill_building_line']['studentId'] == studentId) & 
            (self.dfs['skill_building_line']['exercise'] == exercise)), result_column
        ].astype(float)*100


    def create_all_student_graphs(self, global_vars_dict, df_final_exercise, df_report, mse_report, tmplt_context):
        i = 0
        global student, program, fulldate, vehicle, snor, spoce, saoep, saovc, lnor, lpoce, laoep, laovc, lfpl, msed_rev_time, comment, items, mse_graph, slalom_graph, lnch_graph
        
        # TODO: Remove
        if not os.path.exists(media_root) or not os.path.isdir(media_root):
            os.mkdir(media_root)
        if not os.path.exists(self.plots_path) or not os.path.isdir(self.plots_path):
            os.mkdir(self.plots_path)
        
        for index, row in df_report.iterrows():
            if i > len(df_report):
                break
            else:
                #Define variables for template
                if row['fullname'] in df_final_exercise['participant'].values:
                    student = row['fullname']
                
                fullname, studentId, company, program = student, row["studentId"], row['company'], row['program']
                
                # Date language Format: TODO **
                if global_vars_dict["country"] == 'MX':
                    try:
                        fulldate = row['date'].strftime("%d / %m / %Y")
                    except AttributeError:
                        fulldate = row['date']
                else:
                    try:
                        fulldate = row['date'].strftime("%B %d %Y")
                    except AttributeError:
                        fulldate = row['date']
                        
                global_vars_dict["fulldate"] = fulldate
                
                vehicle = row['vehicle']
                snor = row['s_no_runs']
                spoce = int(row['prcnt_s_pass'])
                saoep = int(row['avg_ex_control_s'])
                saovc = int(row['avg_v_control_s'])
                sfpl = int(row['slalom_max'])
                lnor = row['lc_no_runs']
                lpoce = int(row['prcnt_lc_pass'])
                laoep = int(row['avg_ex_control_lc'])
                laovc = int(row['avg_v_control_lc']) 
                lfpl = int(row['lnch_max'])
                
                #Graphs Variables
                ax1_slalom_plt = self.get_skill_building_student_data(studentId, "Slalom", "%_of_exercise")
                ax1_slalom_plt = ax1_slalom_plt.reset_index(drop=True)
                ax2_slalom_plt = self.get_skill_building_student_data(studentId, "Slalom", "%_of_vehicle")
                ax2_slalom_plt = ax2_slalom_plt.reset_index(drop=True)
                
                ax1_LnCh_plt = self.get_skill_building_student_data(studentId, "Lane Change", "%_of_exercise")
                ax1_LnCh_plt = ax1_LnCh_plt.reset_index(drop=True)
                ax2_LnCh_plt = self.get_skill_building_student_data(studentId, "Lane Change", "%_of_vehicle")
                ax2_LnCh_plt = ax2_LnCh_plt.reset_index(drop=True)
                
                #Slalom Runs Graph
                plt.style.use('seaborn-dark-palette')
                plt.figure(figsize=(6.5,2))
                plt.axhline(y=80, color='#C87867', ls='--', lw=3)
                plt.annotate('Ideal', (0, 90), ha='center', va='center', fontsize=8, color='#C87867')
                plt.axhline(y=100, color='#67BEC8', ls='--', lw=3)
                plt.annotate('Ideal', (0, 110), ha='center', va='center', fontsize=8, color='#67BEC8')
                
                # Language Specific
                if global_vars_dict["country"] == 'MX':
                    plt.plot(ax1_slalom_plt, label = '% Del Ejercicio', linewidth=2, color='#001EBA')
                    plt.plot(ax2_slalom_plt, label = '% Del Vehículo', linewidth=2, color='#BA0000')
                    plt.title('Resultados de Slalom - ' + student)
                else:
                    plt.plot(ax1_slalom_plt, label = '% Of The Exercise', linewidth=2, color='#001EBA')
                    plt.plot(ax2_slalom_plt, label = '% Of The Vehicle', linewidth=2, color='#BA0000')
                    plt.title(student + ' ' + 'Slalom Results')
                
                plt.ylim(ymin=0, ymax=120)
                plt.legend()
                
                #Language specific labels
                if global_vars_dict["country"] == 'MX':
                    plt.xlabel('Intentos')
                else:
                    plt.xlabel('Runs')
                
                plt.ylabel('%')
                plt.tight_layout()
                plt.savefig(f'{self.plots_path}/Slalom Graph ' + studentId + '.png', transparent=True, bbox_inches='tight', dpi=300)
                plt.close()
                
                #Lane Change Graph
                plt.style.use('seaborn-dark-palette')
                plt.figure(figsize=(6.5,2))
                plt.axhline(y=80, color='#C87867', ls='--', lw=3)
                plt.annotate('Ideal', (0, 90), ha='center', va='center', fontsize=8, color='#C87867')
                plt.axhline(y=100, color='#67BEC8', ls='--', lw=3)
                plt.annotate('Ideal', (0, 110), ha='center', va='center', fontsize=8, color='#67BEC8')
                
                # Language Specific
                if global_vars_dict["country"] == 'MX':
                    plt.plot(ax1_LnCh_plt, color='#001EBA', label = '% Del Ejercicio', linewidth=2)
                    plt.plot(ax2_LnCh_plt, color='#BA0000', label = '% Del Vehículo', linewidth=2)
                    plt.title('Resultados de Evasión de Barricada - ' + student)
                else:
                    plt.plot(ax1_LnCh_plt, color='#001EBA', label = '% Of The Exercise', linewidth=2)
                    plt.plot(ax2_LnCh_plt, color='#BA0000', label = '% Of The Vehicle', linewidth=2)
                    plt.title(student + ' ' + 'Barricade Evasion Results')
                plt.ylim(ymin=0, ymax=120)
                plt.legend()
                
                #Language specific labels
                if global_vars_dict["country"] == 'MX':
                    plt.xlabel('Intentos')
                else:
                    plt.xlabel('Runs')
                
                plt.ylabel('%')
                plt.tight_layout()
                plt.savefig(f'{self.plots_path}/LnCh Graph ' + studentId + '.png', transparent=True, bbox_inches='tight', dpi=300)
                plt.close()
                
                #Final exercise table population
                items = mse_report[studentId]
                
                # Final Exercise Percetage Graph - NEW
                column_x = df_final_exercise.loc[(df_final_exercise['studentId'] == studentId)]['final_result']
                row_x = column_x.idxmax()

                # Data Variables
                data_slalom = df_final_exercise.iloc[row_x]['slalom']
                data_lnch = df_final_exercise.iloc[row_x]['LnCh']
                data_rev = df_final_exercise.iloc[row_x]['revPercent']
                data_s = df_final_exercise.iloc[row_x]['final_result']
                min_std = 80 - data_s
                if min_std < 0:
                    min_std = 0
                else:
                    pass
                data_y = 100 - (min_std + data_s)
                size = [data_s, min_std, data_y]
                marker_a = [79,1,20]

                dif_pct = 100 - global_vars_dict['mseg_perf']
                gp_pct = [global_vars_dict['mseg_perf'], dif_pct]
                min_std_df = 100 - min_std
                avg_size = [min_std, min_std_df]
                my_circle = plt.Circle((0,0), 0.7, color='white')
                
                # Colors for percetage graph
                if data_s >= 80:
                    colors_x = ['lawngreen', 'gainsboro', 'grey']
                elif data_s >= 70 < 80:
                    colors_x = ['gold', 'gainsboro', 'grey']
                elif data_s < 70:
                    colors_x = ['darkred', 'gainsboro', 'grey']

                # Overall Perf Graph
                fig, ax = plt.subplots(figsize=(1.5,1.5))
                ax.axis('equal')
                
                ## Local Levels
                if global_vars_dict["country"] == 'MX':
                    label1 = """Min.80%"""
                    label2 = "Desempeño"
                else:
                    label1 = """Min.80%"""
                    label2 = "Performance"

                pie_3_names = ['',label1, '']

                pie_back, _ = ax.pie(marker_a, radius = 1.3+.1, colors=['white', 'black', 'white'], labels=pie_3_names, 
                                     counterclock = False, startangle=-90, textprops={'fontsize': 10})
                plt.setp(pie_back, width=0.3, edgecolor='white')
                pie_1, _ = ax.pie(size, radius = 1.3, colors=colors_x, counterclock = False, startangle=-90, textprops={'fontsize': 8})
                plt.setp(pie_1, width=0.4, edgecolor='white')
                ax.annotate((str(int(data_s)) + '%'), (0, 0), ha='center', va='center', fontsize=16, fontweight='bold', color='black')
                plt.margins(0,0)
                plt.savefig(f'{self.plots_path}/final_percent-' + studentId + '.png', transparent=True, bbox_inches='tight', dpi=300)
                plt.close()
                
                #Slalom Gpraph
                min_std = 80 - data_slalom
                if min_std < 0:
                    min_std = 0
                else:
                    pass
                data_y_slalom = 100 - (min_std + data_slalom)
                size = [data_slalom, min_std, data_y_slalom]
                marker_a = [79,1,20]

                dif_pct = 100 - global_vars_dict['mseg_perf']
                gp_pct = [global_vars_dict['mseg_perf'], dif_pct]
                min_std_df = 100 - min_std
                avg_size = [min_std, min_std_df]
                my_circle = plt.Circle((0,0), 0.7, color='white')

                fig, ax = plt.subplots(figsize=(1,1))
                ax.axis('equal')

                if data_slalom >= 80:
                    colors_x = ['lawngreen', 'gainsboro', 'grey']
                elif data_slalom >= 70 < 80:
                    colors_x = ['gold', 'gainsboro', 'grey']
                elif data_slalom < 70:
                    colors_x = ['darkred', 'gainsboro', 'grey']

                ## Local Levels
                if global_vars_dict["country"] == 'MX':
                    label1 = """Min. 80%"""
                    label3 = ""
                else:
                    label1 = """Min. 80%"""
                    label3 = ""

                pie_3_names = ['',label1, '']
                pie_back, _ = ax.pie(marker_a, 
                                    radius = 1.3+.1, 
                                    colors=['white', 'black', 'white'], 
                                    labels=pie_3_names, 
                                    counterclock = False, 
                                    startangle=-90,
                                    textprops={'fontsize': 8},
                                    rotatelabels = False,
                                    labeldistance = 1
                                    )
                plt.setp(pie_back, width=0.3, edgecolor='white')
                pie_1, _ = ax.pie(size, radius = 1.3, colors=colors_x, counterclock = False, startangle=-90, textprops={'fontsize': 6})
                plt.setp(pie_1, width=0.5, edgecolor='white')
                ax.annotate((str(int(data_slalom)) + '%'), (0, 0), ha='center', va='center', fontsize=10, fontweight='bold', color='black')
                ax.annotate((label3), (0, .35), ha='center', va='center', fontsize=6, color='black')
                plt.margins(0,0)
                plt.savefig(f'{self.plots_path}/final_slalom_percent-' + studentId + '.png', transparent=True, bbox_inches='tight', dpi=300)
                plt.close() 
                
                #LaneChange Gpraph
                min_std = 80 - data_lnch
                if min_std < 0:
                    min_std = 0
                else:
                    pass
                data_y_lnch = 100 - (min_std + data_lnch)
                size = [data_lnch, min_std, data_y_lnch]
                marker_a = [79,1,20]

                dif_pct = 100 - global_vars_dict['mseg_perf']
                gp_pct = [global_vars_dict['mseg_perf'], dif_pct]
                min_std_df = 100 - min_std
                avg_size = [min_std, min_std_df]
                my_circle = plt.Circle((0,0), 0.7, color='white')

                fig, ax = plt.subplots(figsize=(1,1))
                ax.axis('equal')

                if data_lnch >= 80:
                    colors_x = ['lawngreen', 'gainsboro', 'grey']
                elif data_lnch >= 70 < 80:
                    colors_x = ['gold', 'gainsboro', 'grey']
                elif data_lnch < 70:
                    colors_x = ['darkred', 'gainsboro', 'grey']

                ## Local Levels
                if global_vars_dict["country"] == 'MX':
                    label1 = """Min. 80%"""
                    label4 = ""
                else:
                    label1 = """Min. 80%"""
                    label4 = ""
                pie_3_names = ['',label1, '']

                pie_back, _ = ax.pie(marker_a, 
                                    radius = 1.3+.1, 
                                    colors=['white', 'black', 'white'], 
                                    labels=pie_3_names, 
                                    counterclock = False, 
                                    startangle=-90,
                                    textprops={'fontsize': 8},
                                    rotatelabels = False,
                                    labeldistance = 1
                                    )
                plt.setp(pie_back, width=0.3, edgecolor='white')
                pie_1, _ = ax.pie(size, radius = 1.3, colors=colors_x, counterclock = False, startangle=-90, textprops={'fontsize': 6})
                plt.setp(pie_1, width=0.5, edgecolor='white')
                ax.annotate((str(int(data_lnch)) + '%'), (0, 0), ha='center', va='center', fontsize=10, fontweight='bold', color='black')
                ax.annotate((label4), (0, .35), ha='center', va='center', fontsize=6, color='black')
                plt.margins(0,0)
                plt.savefig(f'{self.plots_path}/final_lnch_percent-' + studentId + '.png', transparent=True, bbox_inches='tight', dpi=300)
                plt.close()
                
                #Reverse Gpraph
                min_std = 20 - data_rev
                if min_std < 0:
                    min_std = 0
                else:
                    pass
                data_y_rv = 100 - (min_std + data_rev)
                size = [data_rev, min_std, data_y_rv]
                marker_a = [19,1,80]

                dif_pct = 100 - global_vars_dict['mseg_perf']
                gp_pct = [global_vars_dict['mseg_perf'], dif_pct]
                min_std_df = 100 - min_std
                avg_size = [min_std, min_std_df]
                my_circle = plt.Circle((0,0), 0.7, color='white')

                fig, ax = plt.subplots(figsize=(1,1))
                ax.axis('equal')

                if data_rev > 25:
                    colors_x = ['darkred', 'gainsboro', 'grey']
                elif data_rev > 20 <= 25:
                    colors_x = ['gold', 'gainsboro', 'grey']
                elif data_rev <= 20:
                    colors_x = ['lawngreen', 'gainsboro', 'grey']

                ## Local Levels
                if global_vars_dict["country"] == 'MX':
                    label1 = """Max. 20%"""
                    label5 = ""
                else:
                    label1 = """Max. 20%"""
                    label5 = ""

                pie_3_names = ['',label1, '']

                pie_back, _ = ax.pie(marker_a, 
                                    radius = 1.3+.1, 
                                    colors=['white', 'black', 'white'], 
                                    labels=pie_3_names, 
                                    counterclock = False, 
                                    startangle=-90, 
                                    textprops={'fontsize': 8},
                                    rotatelabels = False,
                                    labeldistance = 1
                                    )
                
                plt.setp(pie_back, width=0.3, edgecolor='white')
                pie_1, _ = ax.pie(size, radius = 1.3, colors=colors_x, counterclock = False, startangle=-90, textprops={'fontsize': 6})
                plt.setp(pie_1, width=0.5, edgecolor='white')
                ax.annotate((str(int(data_rev)) + '%'), (0, 0), ha='center', va='center', fontsize=10, fontweight='bold', color='black')
                ax.annotate((label5), (0, .35), ha='center', va='center', fontsize=6, color='black')
                plt.margins(0,0)
                plt.savefig(f'{self.plots_path}/final_rv_percent-' + studentId + '.png', transparent=True, bbox_inches='tight', dpi=300)
                plt.close()
                
                data_time = df_final_exercise.loc[df_final_exercise['studentId'] == studentId].f_time
                data_time = data_time.reset_index(drop=True)
                data_performance = df_final_exercise.loc[df_final_exercise['studentId'] == studentId].final_result
                data_performance = data_performance.reset_index(drop=True)
                data_rv = df_final_exercise.loc[df_final_exercise['studentId'] == studentId].rev_slalom
                data_rv = data_rv.reset_index(drop=True)
                
                data_tm_fn = data_performance
                cones_fn = df_final_exercise.loc[df_final_exercise['studentId'] == studentId].cones
                cones_fn = cones_fn.reset_index(drop=True)
                gates_fn = df_final_exercise.loc[df_final_exercise['studentId'] == studentId].gates
                gates_fn = gates_fn.reset_index(drop=True)
                xtick = mse_report[studentId][0]['f_time']
                cone_img = mpimg.imread(f'{assets_dir}/cones_for_reports.png')
                pass_time = 80 #(ideal_time.total_seconds()*1.2)
                
                # New Values for Graphs #<-----Changed
                data_rv_pct = (data_rv / data_time)*100

                slalom_pct = df_final_exercise.loc[df_final_exercise['studentId'] == studentId].slalom
                slalom_pct = slalom_pct.reset_index(drop=True)
                lnch_pct = df_final_exercise.loc[df_final_exercise['studentId'] == studentId].LnCh
                lnch_pct = lnch_pct.reset_index(drop=True)

                passes = data_time.index.tolist()
                passes.append(2)

                label = df_final_exercise.loc[df_final_exercise['studentId'] == studentId].stress
                if global_vars_dict["country"] == 'MX':
                    label = label.reset_index(drop=True).replace(0, "Bajo Estrés").replace(1, 'Alto Estrés')
                else:
                    label = label.reset_index(drop=True).replace(0, "Low Stress").replace(1, 'High Stress')

                data_sx = mse_report[studentId][0]['final_result']
                min_stdx = 80 - data_sx
                if min_stdx < 0:
                    min_stdx = 0
                else:
                    pass
                barHeight = .8
                fig, ax = plt.subplots(figsize=(8,4))
                ax.invert_yaxis()
                imagebox = OffsetImage(cone_img, zoom=0.1)
                imagebox.image.axes = ax

                # Average Bar
                ## labels
                if global_vars_dict["country"] == 'MX':
                    label3 = """Promedio: """
                    label4 = 'Prom. Rev: '
                    label5 = """ Prom. Penalización: """
                    label6 = 'Prom. Gpo. '
                else:
                    label3 = """Average: """
                    label4 = 'Av. Rev: '
                    label5 = """ Av. Penalties: """
                    label6 = 'Gp. Average '
                
                ax.barh('Av', float(global_vars_dict['mseg_rev']), color='khaki', edgecolor='white', height=.3) #<-----Changed
                ax.barh('Av', float(global_vars_dict['mseg_perf'])-float(global_vars_dict['mseg_rev']), 
                        left=float(global_vars_dict['mseg_rev']), color='gold', edgecolor='white', height=.3)#<-----Changed
                
                ax.annotate(label3 + str(global_vars_dict['mseg_t']), (global_vars_dict['mseg_perf'], .3), color='black', va='center', ha='right', fontsize=8)
                ax.annotate(label4 + str(global_vars_dict['mseg_rev']), (2, .3), color='black', va='center', ha='left', fontsize=8)
                ax.annotate(label5 + str(global_vars_dict['mseg_c']) + " | " + str(global_vars_dict['mseg_g']), 
                            (float(global_vars_dict['mseg_rev']) + 10, .3), color='black', fontsize=8, va='center', ha='left')
                ax.annotate(label6 + str(global_vars_dict['mseg_perf']) + '%', xy=(float(global_vars_dict['mseg_perf']) + .3, 0), 
                            xytext=(float(global_vars_dict['mseg_perf']) + 10, 0), ha='left', fontsize=10, arrowprops=dict(arrowstyle='->'), va='center')

                # Main Bar Plot
                ## Labels ##
                if global_vars_dict['country'] == 'MX':
                    label7 = """T: """ 
                    label8 = """Completó El Ejercicio"""
                    label9 = """Penalizaciones: """
                    label12 = 'Necesita Práctica'
                    label13 = 'Security Driver'
                else:
                    label7 = """T: """ 
                    label8 = """Did Not Finish"""
                    label9 = """Penalties: """
                    label12 = 'Needs More Work'
                    label13 = 'Security Driver'
                """ POM New Design Adaptation"""
                for i, v in data_tm_fn.items():
                    if mse_report[studentId][i]['f_time'] == 0: 
                        ax.barh(i+1, 1,  
                                color='red', 
                                edgecolor='white', 
                                height=barHeight) 

                        # Time Annotations
                        ax.annotate(label8, 
                                    (v+3, i+1), 
                                    color='k', fontsize=10, 
                                    fontweight='bold', 
                                    va='center', 
                                    ha='left')
                        
                    else:
                    
                        # Student Bar
                        ax.barh(i+1, data_rv_pct[i], 
                                color='darkred', 
                                edgecolor='white', 
                                height=barHeight) 
                        ax.barh(i+1, v - data_rv_pct[i], 
                                left=data_rv_pct[i], 
                                color='red', 
                                edgecolor='white', 
                                height=barHeight) 

                        float_f_time = float("%.2f"%float(mse_report[studentId][i]['f_time']))
                        date_f_time = str(pd.to_timedelta(float_f_time, unit='s'))[10:18]
                        xtick1 = date_f_time
                        xtick2 = xtick1 #str(datetime.strptime(xtick1, '%M:%S.%f').time()) <------Deprecated (No se necesita con el cambio anterior)
                        # Time Annotations
                        ax.annotate(label7 + xtick2, 
                                    (v - 1, i+1), 
                                    color='w', fontsize=10, 
                                    fontweight='bold', 
                                    va='center', 
                                    ha='right')
                        ax.annotate(str(int(data_performance[i]))+'%', 
                                    (v + 1, i+1), 
                                    color='black', 
                                    fontsize=10, 
                                    fontweight='bold', 
                                    va='center', 
                                    ha='left')

                    # Stress Labels
                    if label[i] == "High Stress" or "Alto Estrés":
                        label_color = 'orangered'
                    else:
                        label_color = 'yellowgreen'
                    ax.annotate(label[i], 
                                ((v)+1, i + .8), 
                                ha='left', va='top', 
                                fontsize=8, fontweight='bold', 
                                color=(label_color))
                    
                    # Add Penalties Image
                    ab = AnnotationBbox(imagebox, 
                                        ((data_performance[i] - data_rv_pct[i]) - 11, i+1.4),     # Bar Image 
                                        xybox=(0., 0.), 
                                        xycoords='data',
                                        boxcoords="offset points", 
                                        frameon=False)
                    ax.add_artist(ab)
                    
                    # Penalties Cones | Gates
                    ax.annotate(label9 + str(cones_fn[i]) + " | " + str(gates_fn[i]), 
                                (data_performance[i] - data_rv_pct[i], i+1.5), 
                                color='black', 
                                fontsize=8, 
                                ha='center', va='center')
                    
                    # Slalom | LnCh Percetage Annotation
                    # if data_performance[i] < 60:
                    #     label10 = 'S' 
                    #     label11 = 'L'
                    #     labels_offset = .8
                    # else:
                    #     label10 = 'Slalom'
                    #     label11 = 'LnCh'
                    #     labels_offset = 1
                    # ax.annotate(label10 + ' ' + str(slalom_pct[i]) + '%' + " | " + label11 + ' ' + str(lnch_pct[i]) + '%', 
                    #             (data_rv_pct[i] + 5, i + labels_offset), 
                    #             color='w', 
                    #             fontsize = 10, fontweight='bold', 
                    #             va='center', ha='left')
                    label10 = 'Control'
                    label11 = 'LnCh'
                    labels_offset = .8
                    ax.annotate(label10 + ' ' + str((slalom_pct[i]+lnch_pct[i])/2) + '%', #+ " | " + label11 + ' ' + str(lnch_pct[i]) + '%', 
                                (v - 1, i + labels_offset), 
                                color='w', 
                                fontsize = 8, fontweight='bold', 
                                va='center', ha='right')

                
                # Reverse Time Annotation
                # for i, v in data_rv.items():
                #     if global_vars_dict['country'] == 'MX':
                #         ax.annotate("Reversa:" + str(round(float(v),2)), (2, i+1), color='w', fontsize=10, fontweight='bold', va='center') #Reverse Bar Legend
                #     else:
                #         ax.annotate("Reverse:" + str(round(float(v),2)), (2, i+1), color='w', fontsize=10, fontweight='bold', va='center') #Reverse Bar Legend

                for i, v in data_rv.items():
                    if mse_report[studentId][i]['f_time'] != 0:
                        if global_vars_dict['country'] == 'MX':
                            ax.annotate("Reversa:" + str(round(float(v),2)), (2, i+1), color='w', fontsize=10, fontweight='bold', va='center') #Reverse Bar Legend
                        else:
                            ax.annotate("Reverse:" + str(round(float(v),2)), (2, i+1), color='w', fontsize=10, fontweight='bold', va='center') #Reverse Bar Legend

                # Pass or Fail Annotation <-----Changed
                ax.axvline(pass_time, linestyle='--', ymax=len(passes), color='aqua')
                # if global_vars_dict['country'] == 'MX':
                #     ax.annotate('Necesita Práctica', xy=(pass_time - 23, len(passes)-.3), xytext=(pass_time -1, len(passes)-.3), ha='right', fontsize=10,
                #         arrowprops=dict(arrowstyle='->'), va='center')
                #     ax.annotate('Security Driver', xy=(pass_time + 20, len(passes)-.3), xytext=(pass_time +1, len(passes)-.3), fontsize=10,
                #         arrowprops=dict(arrowstyle='->'), va='center')
                # else:
                ax.annotate(label12, xy=(pass_time - len(label12)*2, len(passes)-.3), xytext=(pass_time -1, len(passes)-.3), ha='right', fontsize=10,
                        arrowprops=dict(arrowstyle='->'), va='center')
                ax.annotate(label13, xy=(pass_time + len(label13)*2, len(passes)-.3), xytext=(pass_time +1, len(passes)-.3), fontsize=10,
                        arrowprops=dict(arrowstyle='->'), va='center', ha='left')
                

                # ax.set_yticks([])
                # ax.set_xticks([])
                ax.axis('off')

                fig.tight_layout()
                plt.xlim(xmin=0, xmax=110)
                plt.ylim(ymin=-.5, ymax=len(passes))
                plt.savefig(f'{self.plots_path}/final_exercise-' + studentId + '.png', transparent=True, bbox_inches='tight', dpi=300)
                plt.close()
                
                for var in tmplt_context:
                    if var in global_vars_dict:
                        tmplt_context[var] = global_vars_dict[var]
                comment = str(row['comments'])
                i+=1
                logger.info(f"Graphs created for student: {student}")
            
    
    def create_mse_report_data(self, df_final_exercise, country):
        # Important change in how dates are read (Cambio Importante en como se leen las fechas)
        # Final Exercise Variables - Possible setting as table for multiple occurances
        mse_report = pd.DataFrame(df_final_exercise.replace(np.nan, '-').drop(['exercise', 'rev_slalom'], axis=1))
        if type(mse_report.loc[0, 'f_time']) != np.float64:
            mse_report['f_time'] = pd.to_timedelta(mse_report.loc[0, 'f_time'], unit='s').astype(str).str.extract('days 00:(.*\..{2}|.*$)')
            # mse_report['f_time'] = mse_report['f_time'].astype(str).str.extract('days 00:(.*\..{2}|.*$)')
        else:
            mse_report['f_time'] = mse_report['f_time'].astype(str)
        if country == 'MX':
            mse_report['stress'].replace((1, 0), ('Alto', 'Bajo'), inplace=True)
        else:
            mse_report['stress'].replace((1, 0), ('High', 'Low'), inplace=True)
        if "rev_%" not in mse_report: 
            mse_report[['rev_%', 'final_result']] = mse_report[['revPercent', 'final_result']].apply(lambda x: x*100).astype(int)
        else:
            mse_report[['rev_%', 'final_result']] = mse_report[['rev_%', 'final_result']].apply(lambda x: x*100).astype(int)
        mse_report.rename(columns={'rev_%' : 'rev_pc'}, inplace=True)

        for i, r in mse_report.iterrows():
            if '.' in r.f_time:
                pass
            else:
                r = r.copy()
                ov = r.f_time
                ov = ov+".01"
                mse_report.loc[i, 'f_time'] = ov
        mse_report.loc[mse_report['final_result'] == 0, 'f_time'] = 0 #<----- Remove values of failed passes [Dec 2022]
        mse_report.loc[mse_report['final_result'] == 0, ['rev_pc', 'slalom', 'LnCh']] = 0 
        mse_report = mse_report.groupby('studentId').apply(lambda x: x.to_dict(orient='records'))
        return mse_report
        
     
    def get_passed_exercise_enhance_data(self, df_skill_building):
        df_passed_ex_enhance = df_skill_building.replace(0, np.nan).groupby(
            by=['studentId', 'exercise']
        ).agg(
            count=("exercise", "size"),
            passed=("%_of_exercise", "count"),
            av_score=("%_of_exercise", "mean"),
            start_score=("%_of_vehicle", "min"),
            end_score=("%_of_vehicle", "max"),
        ).replace(np.nan, 0).unstack(level=1)
        df_passed_ex_enhance['LnCh Passed'] = df_passed_ex_enhance['passed']['Lane Change']/df_passed_ex_enhance["count"]["Lane Change"]
        df_passed_ex_enhance['Slalom Passed'] = df_passed_ex_enhance['passed']['Slalom']/df_passed_ex_enhance["count"]["Slalom"]
        return df_passed_ex_enhance
    
        
    def get_passed_exercise_data(self, df_skill_building):
        df_passed_ex = df_skill_building[['studentId','exercise','cones','%_of_vehicle']]
        df_passed_ex = df_passed_ex.groupby(
            by = ['studentId', 'exercise']
        ).agg(
            start_score = ('%_of_vehicle', "min"),
            end_score = ('%_of_vehicle', "max")
        ).unstack(level=1)
        return df_passed_ex


    def get_vehicle_pc_average_data(self, df_skill_building):
        df_vehicle_pc_avg = df_skill_building.replace(0, np.nan).groupby(
            by=['studentId', 'exercise']
        ).agg(
            vehicle_pc_avg=('%_of_vehicle','mean')
        ).unstack(level=1)
        return df_vehicle_pc_avg
    
    def set_global_vars_dict(self, global_vars_dict):
        self.global_vars_dict = global_vars_dict
    def get_global_vars_dict(self):
        return self.global_vars_dict
    
class GenerateReport():
    def __init__(self, dfs, df_final_exercise, report_artifacts_global_dict, df_student_report, plots_path_str):
        self.dfs = dfs
        self.df_final_exercise = df_final_exercise
        self.report_artifacts_global_dict = report_artifacts_global_dict
        self.df_student_report = df_student_report
        self.plots_path = os.path.join(plots_dir, plots_path_str)
  
    def register_fonts(self):
        registerFont(TTFont('MontserratBold', f"{self.font_dir}/Montserrat ExtraBold 800.ttf"))
        registerFont(TTFont('MontserratBlack', f'{self.font_dir}/Montserrat Black 900.ttf'))
        registerFont(TTFont('Montserrat', f'{self.font_dir}/Montserrat-Regular.ttf'))
        registerFont(TTFont('MontserratLight', f'{self.font_dir}/Montserrat Light 300.ttf'))
        registerFont(TTFont('MontserratThin', f'{self.font_dir}/Montserrat Thin 250.ttf'))
    
    
    def get_global_variables(self):
        global_vars = {}
        global_vars["country"] = self.dfs["course_generals"].loc[0, "country"]
        global_vars["program"] = self.dfs["course_generals"].loc[0, "program"]
        global_vars["fulldate"] = self.report_artifacts_global_dict["fulldate"]
        global_vars["vehicle"] = self.dfs["car_information"].loc[0, "name"]
        global_vars["page_size"] = letter
        global_vars["pwidth"], global_vars["pheight"] = letter 
        global_vars["fwidth"] = global_vars["pwidth"]*.8
        return global_vars


    @staticmethod
    def read_country_specific_report_texts():
        report_headings_path = os.path.join(DB_UTILS_STATIC_DATA, "student_report_headings.json")
        with open(report_headings_path) as file:
            country_heading_map = json.load(file)
        return country_heading_map
    
    
    def read_country_specific_texts(language):
        text_dir = "./as3/static/reports/texts"
        with open(f'{text_dir}/[{language}]_personal_report_intro.txt', 'r', encoding="utf-8") as file:
            intro_pre = file.read()
            intro_text = intro_pre
        with open(f'{text_dir}/[{language}]slalom_description.txt', 'r', encoding="utf-8") as file:
            slalom_pre = file.read()
            slalom_text = slalom_pre
        with open(f'{text_dir}/[{language}]final_x_description.txt', 'r', encoding="utf-8") as file:
            mse_pre = file.read()
            mse_text = mse_pre
        with open(f'{text_dir}/[{language}]final_x_intro.txt', 'r', encoding="utf-8") as file:
            mse_pre2 = file.read()
            mse_desc = mse_pre2
        with open(f'{text_dir}/[{language}]final_note.txt', 'r', encoding="utf-8") as file:
            fn_note_pre = file.read()
            fn_note = fn_note_pre
        return intro_text, slalom_text, mse_text, mse_desc, fn_note
    
    
    def set_static_data_paths(self):
        self.font_dir = os.path.join(static_root, "fonts")
        logo_dir = os.path.join(static_root, "logos")
        self.logo_int = f'{logo_dir}/Logo---AS3-international-200x200.png'
        self.ceo_cfo = f'{logo_dir}/The-CFO-to-the-CEO---Logo.png'
        self.ceo_cfo_inv = f'{logo_dir}/The-CFO-to-the-CEO---Logo_inverted.png'
        self.as3_logo = f'{logo_dir}/AS3 Driver Training - Logo.png'
        self.chrysler300 = f'{logo_dir}/chrysler_300.png'
        self.text_dir = os.path.join(static_root, "texts")

    def generate_student_reports(self, report_dir = str(shortuuid.uuid())):
        """
        """
        global_vars = self.get_global_variables()
        self.set_static_data_paths()
        self.register_fonts()
        addMapping('MontserratLight', 1, 0, 'MontserratBold') #bold
        
        country_heading_map = GenerateReport.read_country_specific_report_texts()
        
        if global_vars["country"] == "MX":
            report_headings = country_heading_map["MX"]
            report_headings["mseTable_headers"] = [
                ['Estrés', 'Tiempo Final', 'Reversa', 'Slalom', 'Barricada', Paragraph('<para align="center">Conos</para>'), 
                 Paragraph('<para align="center">Puertas</para>'), Paragraph('<para align="center">Resultado<br/> Final</para>')
                 ]]
            intro_text, slalom_text, mse_text, mse_desc, fn_note = GenerateReport.read_country_specific_texts("es")
            report_headings["intro_text"] = intro_text
            report_headings["slalom_text"] = slalom_text
            report_headings["mse_text"] = mse_text
            report_headings["mse_desc"] = mse_desc
            report_headings["fn_note"] = fn_note
        else:
            report_headings = country_heading_map["USA"]
            report_headings["mseTable_headers"] = [
                ['Stress', 'Final Time', 'Reverse', 'Slalom', 'Barricade', Paragraph('<para align="center">Cone<br/> Penalties</para>'), 
                 Paragraph('<para align="center">Gate<br/> Penalties</para>'), Paragraph('<para align="center">Final<br/> Result</para>')
                 ]]
            intro_text, slalom_text, mse_text, mse_desc, fn_note = GenerateReport.read_country_specific_texts("en")
            report_headings["intro_text"] = intro_text
            report_headings["slalom_text"] = slalom_text
            report_headings["mse_text"] = mse_text
            report_headings["mse_desc"] = mse_desc
            report_headings["fn_note"] = fn_note
        
        reports_path = os.path.join(media_root, report_dir)
        if not os.path.exists(reports_path) or not os.path.isdir(reports_path):
            os.mkdir(reports_path)     
    
        for _ in self.df_student_report.itertuples():
            studentId = _.studentId
            student = _.fullname
            mse_data = self.prepare_mse_data(studentId, global_vars["country"])
            
            if global_vars["country"] == 'MX':
                filename =  "[es]" + studentId + '.pdf'
            else:
                filename =  "[en]" + studentId + '.pdf'
                
            report_path = os.path.join(reports_path, filename)
            student_report = StudentReportTemplate(student, studentId,  report_path, global_vars, report_headings, 
                                                   self.report_artifacts_global_dict, _, mse_data, self.plots_path, pagesize=letter)
            story = student_report.build_report_story()
            student_report.multiBuild(story)
            logger.info(f"Report generated for student: {student}")

        # Delete plots
        if os.path.exists(self.plots_path):
            shutil.rmtree(self.plots_path)
            logger.info("All plots are deleted")
    
        return True
    
    def prepare_mse_data(self, studentId, country):
        mse_student = self.df_final_exercise[self.df_final_exercise['studentId'] == studentId].index.tolist()
        mse_data = pd.DataFrame(self.df_final_exercise.iloc[mse_student], 
                                columns=['stress', 'f_time', 'revPercent', 'slalom', 'LnCh', 'cones', 'gates', 'final_result'])
        if country == 'MX':
            mse_data['stress'].replace((1, 0), ('Alto', 'Bajo'), inplace=True)
        else:
            mse_data['stress'].replace((1, 0), ('High', 'Low'), inplace=True)
            
        mse_data['revPercent'] = mse_data['revPercent'].apply(lambda x: GenerateReport.convert_to_percent_string(x))
        mse_data['slalom'] = mse_data['slalom'].apply(lambda x: GenerateReport.convert_to_percent_string(x))
        mse_data['LnCh'] = mse_data['LnCh'].apply(lambda x: GenerateReport.convert_to_percent_string(x))
        mse_data['final_result'] = mse_data['final_result'].apply(lambda x: GenerateReport.convert_to_percent_string(x))
        return mse_data
    
    @staticmethod
    def convert_to_percent_string(val):
        return "%.1f"%float(str(val)) + '%'
                            
class StudentReportTemplate(BaseDocTemplate):
    def __init__(self, student, studentId, filename, report_vars, 
                 report_headings, report_artifacts_global_dict, 
                 student_specific_vars, mse_report, plots_path, **kw):
        """
        report_vars = set_global_variables()
        report_headings = generate_student_reports()
        report_artifacts_global_dict = From CourseDataUploadUtil
        student_specific_vars = row from report student df
        """
        self.plots_path = plots_path
        self.allowSplitting = 0
        self.studentId = studentId
        self.student = student
        self.student_specific_vars = student_specific_vars
        self.mse_report = mse_report
        self.report_vars = report_vars
        self.report_headings = report_headings
        self.report_artifacts_global_dict = report_artifacts_global_dict
        self.set_static_data_paths()
        self.create_html_report_tags()
        self.header_content = None
        self.footer_content = None
        self.create_deco()
        self.build_report_story()
        
        BaseDocTemplate.__init__(self, filename, **kw)

        template_CoverPage = PageTemplate('CoverPage',
            [Frame(.8*cm, report_vars["pheight"]/2-(inch*3), self.report_vars["pwidth"]/2, 230, id='F1', showBoundary=0)], 
            onPage=self.createCover, 
            )
        
        template_NormalPage = PageTemplate('NormalPage',
                                [Frame(self.report_vars["pwidth"]*.08, 2.5*cm, self.report_vars["pwidth"]*.84, self.report_vars["pheight"]*.8, id='F2', 
                                    showBoundary=0)],
                                onPage=partial(StudentReportTemplate.header_and_footer,
                                header_content=self.header_content,
                                footer_content=self.footer_content),
                                pagesize=self.report_vars["page_size"])
        
        template_SecondPage = PageTemplate('SecondPage',
                                [Frame(self.report_vars["pwidth"]*.08, self.report_vars["pheight"]*.37, self.report_vars["pwidth"]*.84, self.report_vars["pheight"]*.50, id='F3', 
                                    showBoundary=0),
                                Frame(self.report_vars["pwidth"]*.08, 3*cm, self.report_vars["pwidth"]*.42, self.report_vars["pheight"]*.25, id='F4', 
                                    showBoundary=0),
                                Frame(self.report_vars["pwidth"]*.50, 3*cm, self.report_vars["pwidth"]*.42, self.report_vars["pheight"]*.25, id='F5', 
                                    showBoundary=0)],
                                onPage=partial(StudentReportTemplate.header_and_footer,
                                header_content=self.header_content,
                                footer_content=self.footer_content),
                                pagesize=self.report_vars["page_size"])

        self.addPageTemplates([template_CoverPage,template_NormalPage, template_SecondPage])

    def afterFlowable(self, flowable):
        "Registers TOC entries."
        if flowable.__class__.__name__ == 'Paragraph':
            text = flowable.getPlainText()
            style = flowable.style.name
            if style == 'Heading1':
                self.notify('TOCEntry', (0, text, self.page))
            if style == 'Heading2':
                self.notify('TOCEntry', (1, text, self.page))     
        
    
    def set_static_data_paths(self):
        self.font_dir = os.path.join(static_root, "fonts")
        logo_dir = os.path.join(static_root, "logos")
        self.logo_int = f'{logo_dir}/Logo---AS3-international-200x200.png'
        self.ceo_cfo = f'{logo_dir}/The-CFO-to-the-CEO---Logo.png'
        self.ceo_cfo_inv = f'{logo_dir}/The-CFO-to-the-CEO---Logo_Inverted.png'
        self.as3_logo = f'{logo_dir}/AS3 Driver Training - Logo.png'
        self.chrysler300 = f'{logo_dir}/chrysler_300.png'
        self.text_dir = os.path.join(static_root, "texts")
        
    def create_html_report_tags(self):
        self.h1 = PS(name = 'Heading1', fontSize = 18, leading = 20, fontName='MontserratBold', textColor="#C10230", spaceAfter = 8, spaceBefore = 8)
        self.h2 = PS(name = 'Heading2', fontSize = 14, fontName='MontserratBlack', leading = 16, leftIndent = 0)
        self.h3 = PS(name = 'Heading3', fontSize = 14, fontName='MontserratBold', textColor="#C10230", leading = 16, leftIndent = 10)
        self.subh2 = PS(name = 'SubHeading2', fontSize = 14, fontName='Montserrat', leading = 16, leftIndent = 5)
        self.l0 = PS(name = 'list0', fontSize = 12, leading =14, leftIndent=0, rightIndent=0, spaceBefore = 12, spaceAfter = 0)
        self.pstyle = PS(name='ms', fontName='MontserratLight', fontSize=10, leading =14, spaceAfter = 8, spaceBefore = 8)
        self.no_spacing = PS(name='ms', fontName='MontserratLight', fontSize=10, leading =14, spaceAfter = 0, spaceBefore = 0)
        self.footertxt = PS(name='footer', fontName='MontserratLight', fontSize=10, leading =9, leftIndent=40, rightIndent=0)
        self.super_h1 = PS(name = 'Super_Heading1', fontSize = 80, leading = 0, fontName='MontserratBold', textColor="#C10230", spaceAfter = 0, spaceBefore = 0)
        self.ttl = PS(name = 'Title', fontSize = 24, leading = 25, fontName='MontserratBlack', textColor="#000000", spaceAfter = 0, spaceBefore = 0)
        '-----------------------------------------------------------------------------'
        'Table Styles'
        '-----------------------------------------------------------------------------'
        self.normalTable = TableStyle([('FONTNAME', (0,0), (0, -1), 'Montserrat'), ('FONTNAME', (0,-1), (-1,-1), 'Montserrat'),
                                       ('FONTNAME', (0,1), (-1,-2), 'MontserratLight'), ('ALIGN', (0,0), (-1,0), 'CENTER'), 
                                       ('ALIGN', (1,1), (-1,-1), 'CENTER'), ('LINEBELOW', (0,0), (-1,0), 2, colors.black),
                                       ('LINEABOVE', (0,-1), (-1,-1), .5, colors.black), ('LINEBELOW', (0,-1), (-1,-1), 2, colors.black)])
        self.mseTable = TableStyle([('FONTNAME', (0,0), (0, -1), 'Montserrat'), ('FONTNAME', (0,-1), (-1,-1), 'Montserrat'),
                                    ('FONTNAME', (0,1), (-1,-2), 'MontserratLight'), ('ALIGN', (1,0), (-1,0), 'CENTER'), 
                                    ('ALIGN', (1,1), (-1,-1), 'CENTER'), ('LINEBELOW', (0,0), (-1,0), 2, colors.black), 
                                    ('LINEABOVE', (0,-1), (-1,-1), .5, colors.black), ('LINEBELOW', (0,-1), (-1,-1), 2, colors.black), 
                                    ('BACKGROUND', (0, -1), (-1,-1), colors.lightcoral), ('VALIGN', (0, -1), (-1,-1), 'MIDDLE')])
        self.introTable = TableStyle([('FONTNAME', (0,0), (-1, -1), 'Montserrat'), ('ALIGN', (0,0), (-1,-1), 'LEFT'), 
                                      ('LINEBELOW', (0,0), (-1,-1), 1, colors.black)])
        self.consoleTable = TableStyle([('BOX',(0,0),(-1,-1), 2, colors.firebrick), ('ALIGN', (0,0), (0,-1), 'RIGHT'), 
                                        ('ALIGN', (0,1), (-1,-1), 'CENTER'), ('VALIGN', (0,1), (-1,-1), 'TOP'), 
                                        ('BACKGROUND', (0, 0), (-1,-1), colors.beige)])
        self.subTable = TableStyle([('FONTNAME', (0,0), (-1,-1), 'MontserratLight'), ('VALIGN', (0,0), (-1,-1), 'TOP'), 
                                    ('ALIGN', (0,0), (-1,-1), 'RIGHT'), ('TOPPADDING', (0,0), (0,0), 10)])
        
    # Header and Footer
    @staticmethod
    def header(canvas, doc, content):
        canvas.saveState()
        w, h = content.wrap(doc.width, doc.topMargin)
        content.drawOn(canvas, doc.leftMargin-22.4, doc.height + doc.bottomMargin + doc.topMargin - h -10)
        canvas.restoreState()
        
    @staticmethod
    def footer(canvas, doc, content):
        StudentReportTemplate.drawPageNumber(canvas, doc)
        canvas.saveState()
        w, h = content.wrap(doc.width, doc.bottomMargin)
        content.drawOn(canvas, doc.leftMargin-22.4, h)
        canvas.restoreState()

    @staticmethod
    def header_and_footer(canvas, doc, header_content, footer_content):
        StudentReportTemplate.header(canvas, doc, header_content)
        StudentReportTemplate.footer(canvas, doc, footer_content)

    @staticmethod
    def drawPageNumber(canvas, doc):
        pageNumber = canvas.getPageNumber()

    @staticmethod
    def PageNumber(canvas, doc):
        return(canvas.getPageNumber())

    
    def createCover(self, canvas, doc):
        image = pImage.open(self.logo_int)
        image_width, image_height = image.size
        canvas.drawImage(self.logo_int, ((self.report_vars["pwidth"]/2)-(image_width/2)), self.report_vars["pheight"]-image_height*1.5, mask='auto')
        
    def create_deco(self):
        # 'Header'
        Header_table_data=[[Image(self.ceo_cfo_inv, width=230, height=73)]
        ]
        
        Header_table=Table(Header_table_data,
                            colWidths=[self.report_vars["pwidth"]*.84],
                            rowHeights=[3*cm],
                            style=[('ALIGN',(0,0),(0,0),'RIGHT')])
        # 'Footer'
        Footer_table_data=[[Image(self.as3_logo, 
                            width=144, 
                            height=60),
                            Paragraph('''<para fontname="MontserratBold" size="12" color="black">WWW.</para><para color="#C10230">AS3</para><para color="black">INTERNATIONAL.COM</para>''')]]
        Footer_table=Table(Footer_table_data,colWidths=[(self.report_vars["pwidth"]*.84)/2,(self.report_vars["pwidth"]*.84)/2], 
                           rowHeights=[1*cm],style=[('ALIGN',(0,1),(-1,-1),'RIGHT'), ('VALIGN',(0,0),(0,0),'MIDDLE')])
        
        self.footer_content = Footer_table
        self.header_content = Header_table
        
    # 'Image Aspect Ratio'
    @staticmethod
    def get_image(path, width=1*cm):
        img = utils.ImageReader(path)
        iw, ih = img.getSize()
        aspect = ih / float(iw)
        return Image(path, width=width, height=(width * aspect))

    @staticmethod
    def altBackground(data, table):
        data_len = len(data)+1
        for each in range(data_len):
            if each % 2 == 0:
                bg_color = colors.white
            else:
                bg_color = colors.lightgrey
            table.setStyle(TableStyle([('BACKGROUND', (0, each), (-1, each), bg_color)]))
            
    # 'Build story'
    def build_report_story(self):
        story = []

        '-----------------------------------------------------------------------------'
        'Intro Page'
        '-----------------------------------------------------------------------------'
        story.append(Paragraph(self.report_headings["mainTitle"], self.ttl))
        story.append(Spacer(0,20))
        story.append(Paragraph(self.student, self.h2))
        story.append(Paragraph(self.student_specific_vars.company, self.no_spacing))
        story.append(Paragraph(self.report_vars["program"], self.no_spacing))
        story.append(NextPageTemplate('NormalPage'))
        story.append(PageBreak())

        '- Page 2 -'
        intro_table_data = [[Paragraph(self.report_headings["stdt_name"]), self.student],
                            [Paragraph(self.report_headings["company_label"]), self.student_specific_vars.company],
                            [Paragraph(self.report_headings["pgm_label"]), self.report_vars["program"]],
                            [Paragraph(self.report_headings["pgmDt_label"]), self.report_vars["fulldate"]],
                            [Paragraph(self.report_headings["vhcl_label"]), self.report_vars["vehicle"]]
                        ]

        intro_table = Table(intro_table_data, colWidths=[120,200], style=self.introTable)

        story.append(Spacer(0,20))
        story.append(Paragraph(self.report_headings["scndTitle"], self.ttl))
        story.append(Spacer(0,20))
        story.append(intro_table)
        story.append(Spacer(0,20))
        story.append(Paragraph(self.report_headings["intro_title"], self.h1))
        story.append(Spacer(0,20))
        story.append(Paragraph(self.report_headings["intro_text"], self.pstyle))
        story.append(PageBreak())

        '- Page 3 -'
        story.append(Paragraph(self.report_headings["thirdTitle"], self.h1))
        story.append(Paragraph(self.report_headings["thirdSubTitle"], self.h2))
        story.append(Spacer(0,50))
        story.append(Paragraph(self.report_headings["slalomTitle"], self.subh2))
        story.append(Spacer(0,20))

        slalomGraph = Image(f'{self.plots_path}/Slalom Graph ' + self.studentId + '.png', width=self.report_vars["pwidth"]-inch)
        # story.append(slalomGraph)
        story.append(StudentReportTemplate.get_image(f'{self.plots_path}/Slalom Graph ' + self.studentId + '.png', width=self.report_vars["pwidth"]-inch))
        story.append(Paragraph(self.report_headings["slalom_text"], style=self.footertxt))
        story.append(Spacer(0,80))
        story.append(Paragraph(self.report_headings["perf_table_title"], self.h3))
        
        '------------------------------------------------------------------------------------'
        slalom_table_data = [['','',self.report_headings["perf_table_heading"]],
            [self.report_headings["perf_table_completed"], str(int(self.student_specific_vars.prcnt_s_pass))+"%", str(self.report_artifacts_global_dict["gaspoce"])+"%"],
            [self.report_headings["perf_table_runs"], int(self.student_specific_vars.s_no_runs), self.report_artifacts_global_dict["gasnor"]],
            [self.report_headings["perf_table_percetage"], str(int(self.student_specific_vars.avg_ex_control_s))+"%", str(self.report_artifacts_global_dict["gasaoep"])+"%"],
            [self.report_headings["perf_table_control"], str(int(self.student_specific_vars.avg_v_control_s))+"%", str(self.report_artifacts_global_dict["gasaovc"])+"%"],
            [self.report_headings["perf_table_maxControl"], '', str(self.student_specific_vars.slalom_max)+'%']
        ]
        slalom_table = Table(slalom_table_data, colWidths=[self.report_vars["pwidth"]*.40, self.report_vars["pwidth"]*.20, self.report_vars["pwidth"]*.20], 
                             style=self.normalTable)
        StudentReportTemplate.altBackground(slalom_table_data, slalom_table)
        '------------------------------------------------------------------------------------'
        story.append(slalom_table)
        story.append(PageBreak())

        '- Page 4 -'
        story.append(Spacer(0,50))
        story.append(Paragraph(self.report_headings["LnChTitle"], self.subh2))
        story.append(Spacer(0,20))

        slalomGraph = Image(f'{self.plots_path}/LnCh Graph ' + self.studentId + '.png', width=self.report_vars["pwidth"]-inch)
        # story.append(slalomGraph)
        story.append(StudentReportTemplate.get_image(f'{self.plots_path}/LnCh Graph ' + self.studentId + '.png', width=self.report_vars["pwidth"]-inch))
        story.append(Paragraph(self.report_headings["slalom_text"], style=self.footertxt))
        story.append(Spacer(0,80))
        story.append(Paragraph(self.report_headings["perf_table_title"], self.h3))
        '------------------------------------------------------------------------------------'
        lnch_table_data = [['','',self.report_headings["perf_table_heading"]],
            [self.report_headings["perf_table_completed"], str(int(self.student_specific_vars.prcnt_lc_pass))+"%", str(self.report_artifacts_global_dict["galpoce"])+"%"],
            [self.report_headings["perf_table_runs"], int(self.student_specific_vars.lc_no_runs), self.report_artifacts_global_dict["galnor"]],
            [self.report_headings["perf_table_percetage"], str(int(self.student_specific_vars.avg_ex_control_lc))+"%", str(self.report_artifacts_global_dict["galaoep"])+"%"],
            [self.report_headings["perf_table_control"], str(int(self.student_specific_vars.avg_v_control_lc))+"%", str(self.report_artifacts_global_dict["galaovc"])+"%"],
            [self.report_headings["perf_table_maxControl"], '', str(self.student_specific_vars.lnch_max)+'%']
        ]
        lnch_table = Table(lnch_table_data, colWidths=[self.report_vars["pwidth"]*.40, self.report_vars["pwidth"]*.20, 
                                                       self.report_vars["pwidth"]*.20], style=self.normalTable)
        StudentReportTemplate.altBackground(lnch_table_data, lnch_table)
        '------------------------------------------------------------------------------------'
        story.append(lnch_table)
        story.append(PageBreak())

        '- Page 5 -'

        story.append(Paragraph(self.report_headings["fourthSubTitle"], self.h1))
        story.append(Spacer(0,20))
        story.append(Paragraph(self.report_headings["mse_desc"]))
        story.append(Spacer(0,20))
        story.append(Paragraph(self.report_headings["mse_consoleTitle"], self.h3))
        story.append(Spacer(0,10))

        '------------------------------------------------------------------------------------'
        mse_lnch_graph = StudentReportTemplate.get_image(f'{self.plots_path}/final_lnch_percent-' + self.studentId + '.png', width=self.report_vars["fwidth"]*.20)
        mse_slalom_graph = StudentReportTemplate.get_image(f'{self.plots_path}/final_slalom_percent-' + self.studentId + '.png', width=self.report_vars["fwidth"]*.20)
        mse_reverse_graph = StudentReportTemplate.get_image(f'{self.plots_path}/final_rv_percent-' + self.studentId + '.png', width=self.report_vars["fwidth"]*.20)
        mse_ova_graph = StudentReportTemplate.get_image(f'{self.plots_path}/final_percent-' + self.studentId + '.png', width=self.report_vars["fwidth"]*.30)


        mse_table_data = [[Paragraph(self.report_headings["mse_barricade"]), Paragraph(self.report_headings["mse_slalom"]), 
                           Paragraph(self.report_headings["mse_reverse"]), Paragraph(self.report_headings["mse_ova"])], 
                        [mse_lnch_graph, mse_slalom_graph, mse_reverse_graph, mse_ova_graph]
                        ]
        mse_table = Table(mse_table_data, colWidths=[self.report_vars["fwidth"]*.23, self.report_vars["fwidth"]*.23, 
                                                     self.report_vars["fwidth"]*.23, self.report_vars["fwidth"]*.34], style=self.consoleTable)
        '------------------------------------------------------------------------------------'

        story.append(mse_table)
        story.append(Spacer(0,5))
        story.append(Paragraph(self.report_headings["mse_text"]))
        story.append(PageBreak())

        '- Page 6 -'
        msei = StudentReportTemplate.get_image(f'{self.plots_path}/final_exercise-' + self.studentId + '.png', width=self.report_vars["fwidth"])
        msei_data = [[msei]]

        story.append(Spacer(0,20))

        total_time = StudentReportTemplate.str_to_minute_time(float(self.report_artifacts_global_dict["mseg_t"]))
        self.mse_report["f_time"] = self.mse_report["f_time"].apply(lambda x: StudentReportTemplate.str_to_minute_time(x))
        '------------------------------------------------------------------------------------'
        mse_hist_last_line = [[Paragraph(self.report_headings["gpavg_lvl"]), total_time, 
                               str(self.report_artifacts_global_dict["mseg_rev_pc"])+'%', '','', 
                               self.report_artifacts_global_dict["mseg_c"], self.report_artifacts_global_dict["mseg_g"], 
                               str(self.report_artifacts_global_dict["mseg_perf"])+'%']]
        mse_hist_data = self.report_headings["mseTable_headers"] + np.array(self.mse_report.values).tolist() +np.array(mse_hist_last_line).tolist()

        mse_table = Table(mse_hist_data, colWidths=[
            self.report_vars["pwidth"]*.1, self.report_vars["pwidth"]*.1, self.report_vars["pwidth"]*.1, 
            self.report_vars["pwidth"]*.1, self.report_vars["pwidth"]*.1, self.report_vars["pwidth"]*.1, 
            self.report_vars["pwidth"]*.1, self.report_vars["pwidth"]*.1], style=self.mseTable)

        story.append(Paragraph(self.report_headings["mse_graphTitle"], self.h3))
        story.append(Spacer(0,10))
        story.append(mse_table)
        story.append(Spacer(0,20))
        story.append(Table(msei_data, colWidths=None, rowHeights=None, style=self.consoleTable))
        story.append(Spacer(0,20))
        story.append(Paragraph(self.report_headings["inst_comments_title"], self.h3))
        story.append(Spacer(0,20))
        story.append(Paragraph(self.student_specific_vars.comments))
        story.append(Spacer(0,20))
        story.append(Paragraph(self.report_headings["fn_note"]))
        
        return story

    @staticmethod
    def str_to_minute_time(val):
        if type(val) == float or type(val) == np.float64:
            float_f_time = float("%.2f"%float(val))
            date_f_time = str(pd.to_timedelta(float_f_time, unit='s'))[10:18]
            return date_f_time
        else:
            return val
