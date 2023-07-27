import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Rectangle, Circle
import numpy as np
import matplotlib as mpl
import os
import shortuuid
from django.conf import settings

MEDIA_REPORT_PATH = os.path.join(settings.MEDIA_ROOT, "reports")


class PlotGraphs():
    def __init__(self, language):
        self.language = language
        if not os.path.exists(MEDIA_REPORT_PATH):
            os.mkdir(MEDIA_REPORT_PATH)
        if not os.path.exists(MEDIA_REPORT_PATH + "/plots"):
            os.mkdir(MEDIA_REPORT_PATH + "/plots")


    def plotGlobalExercise(self, data, exercise):
        if self.language == 'EN':
            minimum_lbl = 'Minimum %'
            avg_lbl = 'Average'
            better_lbl = 'Better'
            tries_lbl = 'Number of Tries'
            y_label = '% of the vehicle'
            exercise_lbl = " Exercise Performance"
        else:
            minimum_lbl = '% Mínimo'
            avg_lbl = 'Promedio'
            better_lbl = 'Mejor'
            tries_lbl = 'Número de Intentos'
            y_label = '% del vehículo'
            exercise_lbl = 'Desempeño de Ejercicio'

        fr_slalom_plot = [int(item["value"]) for item in data[exercise]["pvehicles"]]
        x_frplot = [item["participant"] for item in data[exercise]["pvehicles"]]
        fr_slalom_count = [int(item["value"]) for item in data[exercise]["tries"]]
        x_frcount = [item["participant"] for item in data[exercise]["tries"]]
        
        def Average(lst):
            return sum(lst) / len(lst)
        
        average_perf = int(round(Average(fr_slalom_plot), 0))
        average_pass = int(round(Average(fr_slalom_count), 0))

        plt.style.use('seaborn-white')
        fig, ax = plt.subplots(figsize=(12, 5))
        plt.grid(visible=True, axis='x')

        """AX1 Artists"""
        plt.axhline(y=80, color='#C87867', ls='--', lw=3)
        plt.axhline(y=average_perf, color='#FFCCCC', ls='--', lw=3)  # <---- Average Performance Line
        ax.annotate(minimum_lbl, (0, 75), ha='left', va='center', fontsize=12, color='#C87867')  # <-- Minimum Label
        ax.annotate(avg_lbl, (0, (average_perf - 5)), ha='left', va='center', fontsize=12, color='#FFCCCC')

        ax.annotate(better_lbl, xy=(-.4, 115), xytext=(0, -20), fontsize=10,
                    arrowprops=dict(arrowstyle='->', color='#C87867'), va='top', ha='center', rotation=90,
                    textcoords='offset points',
                    color='#C87867')

        plt.title(exercise_lbl + " " + exercise )

        """AX1 Plot"""
        ax.plot(x_frplot, fr_slalom_plot, marker='o', color='red')
        plt.xticks(x_frplot, x_frplot, rotation=45, fontsize=12, ha='right')
        plt.ylim(ymin=0, ymax=120)
        plt.ylabel(y_label)

        ax2 = ax.twinx()

        """Artists for AX2"""
        plt.axhline(y=average_pass, color='#CCCCCC', ls='--', lw=3)  # <---- Average Passes Line
        ax2.annotate(avg_lbl, (0, (average_pass - 1)), ha='left', va='center', fontsize=12, color='#CCCCCC')
        ax.annotate(better_lbl, xy=(-.4, 5), xytext=(0, 20), fontsize=10,
                    arrowprops=dict(arrowstyle='->', color='grey'),
                    va='bottom', ha='center', rotation=90,
                    textcoords='offset points',
                    color='grey')

        """AX2 Plot"""
        ax2.plot((fr_slalom_count), marker='s', color='grey', linestyle='none')
        plt.ylim(ymin=0, ymax=30)
        plt.ylabel(tries_lbl, color='grey')
        plt.yticks(np.arange(0, 31, 5))

        # plt.plot(fr_slalom_plot, color='#001EBA', label = '% Del Ejercicio', linewidth=3)
        # plt.title(plt_title)
        for index, v in enumerate(fr_slalom_plot):
            ax.annotate((str(int(v)) + '%'),
                        xy=(index, v),
                        xytext=(-7, 7),
                        textcoords='offset points',
                        fontsize=12,
                        rotation=45,
                        color='red')

        for index, v, in enumerate(fr_slalom_plot):
            ax2.annotate(str(int(v)), xy=(index, v), xytext=(0, -15), textcoords='offset points', fontsize=12, ha='center')

        fig.align_xlabels()
        fname = os.path.join(MEDIA_REPORT_PATH, 'plots/' + shortuuid.uuid() + '.png')
        plt.tight_layout()
        plt.savefig(fname, dpi=200)
        plt.close()
        return fname

    def plotFinalResultGlobal(self, ls_av, hs_av, glbl_ls_av, glbl_hs_av,  top_student, top_student_final_result, company):
        if self.language == 'EN':
            title_lbl = "Performance (% of Final Exercise)"
            low_lbl = company + "\nLow Stress Average"
            high_lbl = company +"\nHigh Stress Average"
            globalLow_lbl = "Low Stress Global Average"
            globalHigh_lbl = "High Stress Global Average"
            top_student_lbl = "Your Top Student \n"

        else:
            title_lbl = "Rendimiento (% del Ejercicio Final)"
            low_lbl = company + "\nPromedio Bajo Estrés"
            high_lbl = company + "\nPromedio Alto Estrés"
            globalLow_lbl = "Promedio Global Bajo Estrés"
            globalHigh_lbl = "Promedio Global Alto Estrés"
            top_student_lbl = "Tu Mejor Estudiante \n"

        # rotationLow = -20
        # rotationHigh = -20
 
        plt.clf()
        fig, ax = plt.subplots(figsize=(13, 1.10))
        fig.subplots_adjust(bottom=0.5)

        cmap = mpl.cm.Spectral
        norm = mpl.colors.Normalize(vmin=30, vmax=100)

        fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap),
                    cax=ax, orientation='horizontal', label=title_lbl)
        ax.xaxis.set_label_coords(.5, -2.15)


        plt.axvline(x=hs_av, c='r', ls='--', lw=3)

        if ls_av == 0:
            pass
        else:
            plt.axvline(x=ls_av, c='b', ls='--', lw=3)
            plt.annotate((low_lbl),
                    xy=(ls_av, 1.5), xytext=(0, 1), ha='right',
                    xycoords=('data', 'figure fraction'),
                    textcoords='offset points',
                    color='darkblue', fontsize=12,
                    rotation=-20,
        #              arrowprops = dict(arrowstyle="-", color='k')
                    )
        if hs_av == 0:
            pass
        else:
            plt.annotate((high_lbl),
                        xy=(hs_av, 1.5), xytext=(0, 1), ha='right',
                        xycoords=('data', 'figure fraction'),
                        textcoords='offset points',
                        color='red', fontsize=12,
                        rotation=-20
                        )

        # Global Markers
        plt.annotate(globalLow_lbl,
                    xy=(glbl_ls_av, .65), xytext=(0, -5),
                    xycoords=('data', 'figure fraction'),
                    textcoords='offset points',
                    color='grey', fontsize=11,
                    )

        'Arrow Props----------------------------------------------------------'
        plt.annotate('', xy=(glbl_ls_av, 1.0), xytext=(0, -25), ha='right',
                    xycoords=('data', 'figure fraction'),
                    textcoords='offset points',
                    arrowprops = dict(arrowstyle="simple", color='teal'))
        '---------------------------------------------------------------------'


        plt.annotate(globalHigh_lbl,
                    xy=(glbl_hs_av, .65), xytext=(0, -25), ha='left',
                    xycoords=('data', 'figure fraction'),
                    textcoords='offset points',
                    color='grey', fontsize=11,
        #              bbox=dict(facecolor='yellow',alpha=0.3)
                    )
        'Arror Props---------------------------------------------------------'
        plt.annotate('', xy=(glbl_hs_av, 1.0), xytext=(0, -45), ha='right',
                    xycoords=('data', 'figure fraction'),
                    textcoords='offset points',
                    arrowprops = dict(arrowstyle="simple", color='lightcoral'))
        '---------------------------------------------------------------------'

        plt.annotate(top_student_lbl + top_student,
                    xy=(top_student_final_result, 1.4), xytext=(-10, 20), ha='center', va='bottom',
                    xycoords=('data', 'figure fraction'),
                    textcoords='offset points',
                    color='firebrick', fontsize=12,
                    rotation=0,
                    )

        plt.annotate('', xy=(top_student_final_result, 1.4), xytext=(0, 20), ha='right', va='bottom',
                    xycoords=('data', 'figure fraction'),
                    textcoords='offset points',
                    arrowprops = dict(arrowstyle="simple", color='k')
                    )

        ax.add_patch( Circle((glbl_hs_av, .5), .3,
                    color='crimson') )
        ax.add_patch( Circle((glbl_ls_av, .5), .3,
                    color='teal') )


        fname = os.path.join(MEDIA_REPORT_PATH, 'plots/' + shortuuid.uuid() + '.png')
        # plt.tight_layout()
        plt.savefig(fname, bbox_inches='tight', dpi=300)
        
        image = plt.imread(fname)
        # y, x, z = image.shape
        y_cut = 200
        image_new = image[y_cut:, :, :]
        plt.imsave(fname, image_new)
        
        return fname

    def plotTopPerformers(self, data):
        if self.language == 'EN':
            finalResult_lbl = 'Overall Performance'
            percentage_lbl = 'Percentage'
            laneChange_lbl = 'Control Over Barricade'
            slalom_lbl = 'Control Over Slalom'
        else:
            finalResult_lbl = 'Desempeño General'
            percentage_lbl = 'Porcentaje'
            laneChange_lbl = 'Control en Evasion de Barricada'
            slalom_lbl = 'Control en Slalom'
        data_x = [item["first_name"] + " " + item["last_name"] for item in data]
        data_y = [item["final_result"] for item in data]

        data_slalom = [int(item["slalom"]) for item in data]
        data_lnch = [int(item["lane_change"]) for item in data]
        #stress = data['stress']

        x_labels = np.arange(len(data_y))
        width = 0.35

        plt.style.use('seaborn-white')
        fig, ax = plt.subplots(figsize=(6, 5))
        plt.ylim(ymin=10, ymax=120)

        ax.bar(data_x, data_y, label=finalResult_lbl, color='darkred')
        # high_stress = ax.bar(data_y, data_x, label='Low Stress', color=('darkgrey'))
        ax.set_ylabel(percentage_lbl)
        ax.plot(data_x, data_slalom, marker='o',
                color='royalblue',
                label=slalom_lbl,
                lw=4, snap=True
                )
        ax.plot(data_x, data_lnch, marker='d', color='c', label=laneChange_lbl, lw=4, snap=True)
        plt.xticks(rotation=45, fontsize=12, ha='right')
        plt.ylim(ymin=10, ymax=120)
        plt.axhline(y=80, color='#C87867', ls='--', lw=5)

        legend = ax.legend(loc='best', shadow=True, fontsize=12)
        fname = os.path.join(MEDIA_REPORT_PATH,'plots/' + shortuuid.uuid() + '.png')
        plt.savefig(fname, bbox_inches='tight', dpi=300)
        plt.close()
        return fname

    def plotLowPerformers(self, data):
        if self.language == 'EN':
            finalResult_lbl = 'Overall Performance'
            percentage_lbl = 'Percentage'
            laneChange_lbl = 'Control Over Barricade'
            slalom_lbl = 'Control Over Slalom'
        else:
            finalResult_lbl = 'Desempeño General'
            percentage_lbl = 'Porcentaje'
            laneChange_lbl = 'Control en Evasion de Barricada'
            slalom_lbl = 'Control en Slalom'

        data_x = [item["first_name"] + " " + item["last_name"] for item in data]
        data_y = [item["final_result"] for item in data]

        data_slalom = [int(item["slalom"]) for item in data]
        data_lnch = [int(item["lane_change"]) for item in data]
        #stress = data['stress']

        x_labels = np.arange(len(data_y))
        width = 0.35

        plt.style.use('seaborn-white')
        fig, ax = plt.subplots(figsize=(6, 5))
        plt.ylim(ymin=10, ymax=120)

        ax.bar(data_x, data_y, label=finalResult_lbl, color='darkred')
        # high_stress = ax.bar(data_y, data_x, label='Low Stress', color=('darkgrey'))
        ax.set_ylabel(percentage_lbl)
        ax.plot(data_x, data_slalom, marker='o',
                color='royalblue',
                label=slalom_lbl,
                lw=4, snap=True
                )
        ax.plot(data_x, data_lnch, marker='d', color='c', label=laneChange_lbl, lw=4, snap=True)
        plt.xticks(rotation=45, fontsize=12, ha='right')
        plt.ylim(ymin=10, ymax=120)
        plt.axhline(y=80, color='#C87867', ls='--', lw=5)

        legend = ax.legend(loc='best', shadow=True, fontsize=12)
        fname = os.path.join(MEDIA_REPORT_PATH,'plots/' + shortuuid.uuid() + '.png')
        plt.savefig(fname, bbox_inches='tight', dpi=300)
        plt.close()
        return fname
    
    def plotScatterPlot(self, data):
        """
        Y = %Exercise
        X = %Control
        C = %Reversa
        S = Penalties
        """
        if self.language == 'EN':
            y_label = '% of the exercise'
            x_label = '% of control'
            rev_perf = 'Penalties'
            better_lbl = "Security Driver \n Balance"
            better_cont_lbl = 'Faster Driver'
            better_skill_lbl = 'Greater Control/Skill'
        else:
            y_label = '% de ejercicio'
            x_label = '% de control'
            rev_perf = 'Penalizaciones'
            better_lbl = "Balance \n Security Driver"
            better_cont_lbl = 'Manejo Más Rápido'
            better_skill_lbl = 'Mejor Control/Habilidad'

        y = [int(item["final_result"]) for item in data]
        x = [int((item["slalom"] + item["lane_change"]) / 2) for item in data]
        sizes = [int(item["reverse"]*100) for item in data]
        colors = [int(item["penalties"]) for item in data]

        plt.style.use('seaborn-white')
        fig, ax = plt.subplots(figsize=(20, 8))
        plt.ylabel(y_label)
        plt.xlabel(x_label)
        plt.ylim(ymin=70, ymax=100)

        """
        Control Arrow
        """
        ax.arrow(35, 72, 0, 25, head_width=.5, ls='--',
                color='gray')
        ax.annotate(better_cont_lbl, xy=(35, 99), xytext=(-35, 0), fontsize=14,
                    va='top', ha='left', rotation=0,
                    textcoords='offset points',
                    color='grey')
        """
        Skill Arrow
        """
        ax.arrow(35, 72, 50, 0, head_width=.5, ls='--',
                color='gray')
        ax.annotate(better_skill_lbl, xy=(89, 72.5), xytext=(0, 12), fontsize=14,
                    va='top', ha='right', rotation=0,
                    textcoords='offset points',
                    #                 arrowprops=dict(arrowstyle="->"),
                    color='grey')
        """
        Balance Rectangle
        """
        ax.annotate(better_lbl, xy=(80, 90), xytext=(0, 0), fontsize=20,
                    va='bottom', ha='center', rotation=0,
                    textcoords='offset points',
                    color='gray')
        ax.add_patch(Rectangle((70, 80),
                            20, 18,
                            fc='whitesmoke',
                            color='darkred',
                            linewidth=2,
                            linestyle=":"))

        sc = ax.scatter(x, y, c=colors, s=sizes,
                        cmap='turbo')  # Old 'Wistia'
        cbar = plt.colorbar(sc)
        cbar.set_label(rev_perf, rotation=270, labelpad=20)

        """Labels"""
        for i, item in enumerate(data):
            texts = ax.annotate(item["first_name"] + " " + item["last_name"],
                                xy=(int((item["slalom"] + item["lane_change"]) / 2), item['final_result']),
                                xytext=(0, 10),
                                textcoords='offset points',
                                ha='right',
                                fontsize=14,
                                rotation=-15,
                                bbox=dict(facecolor='yellow', alpha=0.3))
        fname = os.path.join(MEDIA_REPORT_PATH,'plots/' + shortuuid.uuid() + '.png')
        plt.savefig(fname, bbox_inches='tight', dpi=300)
        plt.close()
        return fname

