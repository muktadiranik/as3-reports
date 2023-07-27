import os

import shortuuid
from as3.core.utils.reports.plotter import PlotGraphs
from as3.core.utils.reports.template import DocTemplate
from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (Image, NextPageTemplate, PageBreak, Spacer,
                                Table, TableStyle)
from reportlab.platypus.paragraph import Paragraph
from reportlab.platypus.tableofcontents import TableOfContents

dir_path = settings.STATIC_ROOT + "/reports/"
MEDIA_PATH = settings.MEDIA_ROOT

class GlobalCompanyReport(DocTemplate):
    def __init__(self, language, company, reportDateRange):
        self.language = language
        self.company = company
        self.reportDateRange = reportDateRange
        self.plotter = PlotGraphs(language)
        
        self.regitser_fonts()
        self.add_mapping()
        self.set_page_writers()
        self.set_styles()

    def generate_pdf(self, story):
        fname = os.path.join(os.path.join(MEDIA_PATH, 'reports/' + shortuuid.uuid() + '.pdf'))
        doc = DocTemplate(fname, self.language, pagesize=letter)
        doc.multiBuild(story)
        return fname
    
    def toc(self):
        story = []
        toc = TableOfContents()
        # For conciseness we use the same styles for headings and TOC entries
        toc.levelStyles = [self.h1, self.h2]
        story.append(NextPageTemplate('CoverPage'))
        story.append(Paragraph(self.company, self.ttl))
        story.append(Paragraph(self.reportDateRange, self.ttl))
        story.append(NextPageTemplate('SecondPage'))
        story.append(PageBreak())
        return story, []

    def introduction_section(self, data):
        story = []
        
        universalColorbar = self.plotter.plotFinalResultGlobal(
            data["qs"]["ls"] or 0,
            data["qs"]["hs"] or 0,
            data["global"]["ls"] or 0,
            data["global"]["hs"] or 0,
            data["qs"]["top_student"] or "",
            data["qs"]["max"] or 0,
            self.company or ""
        )
        pwidth, pheight = letter
        passCount = data["qs"]["pass_count"]
        student_number = data["qs"]["total_students"]
        
        if self.language == 'EN':
            with open(os.path.join(dir_path, 'texts/HMA_intro.txt'), 'r', newline='') as file:
                intro_pre = file.read()
                intro_text = intro_pre
                
            story.append(Paragraph('INTRODUCTION', self.h1))
            story.append(Spacer(0, 20))
            story.append(Paragraph(intro_text, self.pstyle))
            story.append(PageBreak())
            story.append(Paragraph('THE SECURITY DRIVER UNIVERSE', self.h1))
            story.append(Paragraph('This report compares a total of ' + str(
                student_number) + ' students that were sent from ' + self.company + ' to all of our programs during the period ' + self.reportDateRange,
                                self.h2))
            story.append(Image(universalColorbar, width=514, height=125))
            story.append(Spacer(0, 20))
            story.append(Paragraph(
                """This graph allows us to compare this group to a universal average; this average is taken from every student who has undergone a similar course anywhere in the world where AS3 Driver Training has operations and is an ever-changing number.""",
                self.footertxt))
            story.append(Spacer(0, 20))

            # ------------------------------- Percentages Table
            pct_table_data = [[
                Paragraph(str(student_number), self.super_h1), Paragraph('STUDENTS ATTENDED', self.h2)],
                ['', Paragraph(str(passCount) + """ ABOVE THE 80% STANDARD QUALIFICATION""", self.subh2)]
            ]
        else:
            with open(os.path.join(dir_path, 'texts/[es]HMA_intro.txt'), 'r', newline='') as file:
                        intro_pre = file.read()
                        intro_text = intro_pre
            story.append(Paragraph('INTRODUCCIÓN', self.h1))
            story.append(Spacer(0, 20))
            story.append(Paragraph(intro_text, self.pstyle))
            story.append(PageBreak())
            story.append(Paragraph('EL UNIVERSO DE CONDUCTORES DE SEGURIDAD', self.h1))
            story.append(Paragraph('Este informe compara un total de ' + str(
                student_number) + ' estudiantes que fueron enviados desde ' + self.company + ' a todos nuestros programas durante el periodo ' + self.reportDateRange,
                                self.h2))
            story.append(Image(universalColorbar, width=514, height=100))
            story.append(Spacer(0, 20))
            story.append(Paragraph(
                """Este gráfico nos permite comparar este grupo con el promedio universal; este promedio se toma de cada estudiante que ha realizado un curso similar en \
                    cualquier parte del mundo donde AS3 Driver Training tiene operaciones y es un número en constante cambio.""",
                self.footertxt))
            story.append(Spacer(0, 20))

            # ------------------------------- Percentages Table
            pct_table_data = [[
                Paragraph(str(student_number), self.super_h1), Paragraph('ESTUDIANTES ATENDIDOS', self.h2)],
                ['', Paragraph(str(passCount) + """ POR ENCIMA DEL ESTÁNDAR DE CALIFICACIÓN DEL 80%""", self.subh2)]
            ]

        story.append(Table(pct_table_data, colWidths=[(pwidth * .20), (pwidth * .50)], hAlign='LEFT', style=[
            #     ('GRID',(0,0),(-1,-1),1,colors.black),
            ('SPAN', (0, 0), (0, 1)),
            # ('ALIGN',(0,0),(1,0),'CENTER'),
            ('ALIGN', (1, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (0, 0), (0, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (1, 0), (1, 0), 9),
            ('TOPPADDING', (0, 0), (0, 0), -15),
            # ('ALIGN',(0,0),(3,0),'CENTER'),
            # ('TEXTCOLOR',(0,0),(3,0),colors.Color(49/255,71/255,137/255))
        ]))
        story.append(Spacer(0, 30))
        
        return story, [universalColorbar]

    def vehicles_section(self, vehicles_json):
        story = []
        usedVehicles = []
        for vehicle in vehicles_json["items"][:4]: # todo: only max 4 vehicles are shown due to next page
            image_path = os.path.join(MEDIA_PATH, vehicle["img_path"])
            if not vehicle["img_path"] or not os.path.exists(image_path):
                image_path = os.path.join(dir_path, 'images/chrysler300.png') # chrysler300  default
                
            usedVehicles.append({
                "image": image_path,
                "vehicle": vehicle["name"],
                "latAcc": vehicle["lat_acc"],
                "top_speed_slalom": vehicle["top_speed_slalom"],
                "top_speed_lnch": vehicle["top_speed_lnch"],
            })
        # --------------------------------Variables
        vehiclesData = []

        vImageWidth = 100
        vImageHeight = vImageWidth / 2

        for index, row in enumerate(usedVehicles):
            img = str(row['image'])
            car = str(row['vehicle'])
            latacc = str(row['latAcc'])
            if self.language == 'EN':
                vehicleTopSpeed_slalom = row["top_speed_slalom"]
                vehicleTopSpeed_lnch = row["top_speed_lnch"]

                vehicleImage = Image(img,
                                    width=vImageWidth, height=vImageHeight)

                vehicleDescription = Paragraph(
                    """<span fontName=MontserratBold>Vehicle:</span> """ + car + '<br/> <span fontName=MontserratBold>Lat Acc Capability:</span> ' + latacc + 'Gs<br/><span fontName=MontserratBold>Slalom Top Speed:</span> ' + str(
                        vehicleTopSpeed_slalom) + 'MPH<br/> <span fontName=MontserratBold>Barricade Top Speed:</span> ' + str(
                        vehicleTopSpeed_lnch) + 'MPH<br/><br/>')
                vehiclesData.append([vehicleImage, vehicleDescription])

            else:
                vehicleTopSpeed_slalom = row["top_speed_slalom"]
                vehicleTopSpeed_lnch = row["top_speed_lnch"]

                vehicleImage = Image(img,
                                    width=vImageWidth, height=vImageHeight)

                vehicleDescription = Paragraph(
                    """<span fontName=MontserratBold>Vehículo:</span> """ + car + '<br/> <span fontName=MontserratBold>Capacidad Lat Acc:</span> ' + latacc + 'Gs<br/><span fontName=MontserratBold>Mayor Velocidad Slalom:</span> ' + str(
                        vehicleTopSpeed_slalom) + 'KPH<br/> <span fontName=MontserratBold>Mayor Velocidad Barricada:</span> ' + str(
                        vehicleTopSpeed_lnch) + 'KPH<br/><br/>')
                vehiclesData.append([vehicleImage, vehicleDescription])

        vehicleDataTable = Table(vehiclesData, colWidths=[(vImageWidth), (157)], style=self.subTable)

        # --------------------------------Table
        vehicleTableData = [[vehicleImage,
                            vehicleDescription]]

        if self.language == 'EN':
            story.append(Paragraph('VEHICLES USED', self.h1))
        else:
            story.append(Paragraph('VEHÍCULOS USADOS', self.h1))

        story.append(vehicleDataTable)
        story.append(NextPageTemplate('NormalPage'))
        story.append(PageBreak())
        
        return story, []

    def performers_section(self, performers):
        story = []
        to_show = 7
        low_performers = sorted(performers["items"], key=lambda d: d['final_result'])[0:to_show]
        top_performers = sorted(performers["items"], key=lambda d: d['final_result'], reverse=True)[0:to_show]

        low_performers_names = [item["first_name"] + ' ' + item["last_name"] for item in low_performers[0:3]]
        top_perf_graph = self.plotter.plotTopPerformers(top_performers)
        low_perf_graph = self.plotter.plotLowPerformers(low_performers)
        
        if self.language == 'EN':
            # 10, 80
            '-----------------------------------------------------------------------------'
            'Top / Low Performers'
            '-----------------------------------------------------------------------------'
            top_perf_para = """These are the Top """ + "10"  + """ performers for the """ + self.reportDateRange + """ term. To be on this list, each student must have achieved a grade of at least 80% or higher during the final exercise.<br/>
            <br/>
            A higher Performance means a faster driver; this means the driver is more confident with his vehicle. Anyone above the group's """ + "80" + """ % average can be considered a good driver, primarily if that is achieved under stress.<br/>
            <br/>
            On the other hand, Slalom & Barricade will relate the amount of control for each student; a higher number means more experience. The ideal driver should achieve above 80% in slalom and barricade; anyone above the group's """ + str(
                "control_avg") + """% average should be considered a good driver.<br/>"""
            top_perf_rev_para = """The reverse is probably the most crucial part of the final exercise, and students are required to do this in under 20% of their overall time; statistically, the safest way out of a possible ambush is backward, not being able to achieve this places the driver at a significant disadvantage."""

            low_perf_para = """Being a low-performing student could be due to several things; the most important is lack of experience and/or confidence with the vehicle, which results in lost time during the exercise.<br/>
            <br/>
            The key factors to watch for here are that a lower than 60% of the performance result could mean a severe lack of skill and should be considered a risk factor for a professional driver; anything below 40% is considered a dangerous driver. <br/>
            <br/>
            When a driver gets a low result on this exercise is usually due to failure to control the vehicle under pressure, this results in hitting obstacles or missing gates and being penalized because of it; this is usually due to lack of experience and could be corrected with stress inoculation training."""
            low_perf_para_lower = """Students like """ + ", ".join(low_performers_names) + """ need to be exposed to more deliberate practice to ensure the proper reaction at a time of crisis."""
        else:
            '-----------------------------------------------------------------------------'
            'Top / Low Performers'
            '-----------------------------------------------------------------------------'
            top_perf_para = """Estos son los mejores """ + "10" + """ en desempeño para el rango """ + self.reportDateRange + """. Para estar en esta lista, cada estudiante debe haber logrado un calificación de al menos 80% o superior durante el ejercicio final.<br/>
            <br/>
            Un mayor rendimiento significa un conductor más rápido; esto significa que el conductor tiene más confianza con su vehículo. Cualquiera que supere el """ + "80" + """ % promedio del grupo puede considerarse un buen conductor, principalmente si se logra bajo estrés.<br/>
            <br/>
            Por otro lado, Slalom & Barricada nos relata la cantidad de control que logra cada alumno; un número más alto significa más experiencia. El conductor ideal debería estar por encima del 80% en slalom y barricada; cualquier persona por encima del promedio """ + str(
                "control_avg") + """% del grupo es considerado un buen conductor.<br/>"""
            top_perf_rev_para = """La reversa es probablemente la parte más crucial del ejercicio final, y los estudiantes deben hacer esto en menos del 20% de su tiempo total; estadísticamente, la forma más segura de salir de una posible emboscada es hacia atrás, no poder lograr esto coloca al conductor en una desventaja significativa."""

            low_perf_para = """Ser un alumno de bajo rendimiento puede deberse a varias cosas, la más importante es la falta de experiencia y/o confianza con el vehículo, lo que se traduce en pérdida de tiempo durante el ejercicio.<br/>
            <br/>
            Los factores clave a tener en cuenta aquí son que un resultado inferior al 60 % del rendimiento podría significar una grave falta de habilidad y debería considerarse un factor de riesgo para un conductor profesional; cualquier cosa por debajo del 40% se considera un conductor peligroso. <br/>
            <br/>
            Cuando un conductor obtiene un resultado bajo en este ejercicio, generalmente se debe a que no controló el vehículo bajo presión, lo que resulta en chocar con obstáculos o slatarse puertas y ser penalizado por ello; esto generalmente se debe a la falta de experiencia y podría corregirse con capacitación en inoculación de estrés."""
            low_perf_para_lower = """Estudiantes como """+  ", ".join(low_performers_names)  +""" deben estar expuestos a más práctica deliberada para garantizar la reacción adecuada en un momento de crisis."""

        performers_columns = ['FULLNAME', 'STRESS\n LEVEL', 'REVERSE\n (%)', 'SLALOM\n TEST (%)', 'BARRICADE\n EVASION (%)','PERFORMANCE\n (%)']
        performers_values = []

        averages = {
            "reverse": 0,
            "slalom": 0,
            "lane_change": 0,
            "final_result": 0,
        }
        for perf in low_performers:
            averages["reverse"] += perf["reverse"]
            averages["slalom"] += perf["slalom"] 
            averages["lane_change"] += perf["lane_change"] 
            averages["final_result"] += perf["final_result"] 
            performers_values.append(
                [f'{perf["first_name"]} {perf["last_name"]}', 
                perf["stress"], int(perf["reverse"]), int(perf["slalom"]), 
                int(perf["lane_change"]), int(perf["final_result"])]
            )
        for k, v in averages.items():
            averages[k] = int(v/len(low_performers))

        lpt = Table( 
            [performers_columns] + performers_values + [['GROUP AVERAGE', ''] + list(averages.values())],
            colWidths=[170, 50, 60, 60, 60, 90],
            hAlign='LEFT', style=self.normalTable
        )
                
        averages={
            "reverse": 0,
            "slalom": 0,
            "lane_change": 0,
            "final_result": 0
        }
        performers_values = []
        for perf in top_performers:
            averages["reverse"] += perf["reverse"]
            averages["slalom"] += perf["slalom"] 
            averages["lane_change"] += perf["lane_change"] 
            averages["final_result"] += perf["final_result"] 
            performers_values.append(
                [f'{perf["first_name"]} {perf["last_name"]}', 
                perf["stress"], int(perf["reverse"]), int(perf["slalom"]), 
                int(perf["lane_change"]), int(perf["final_result"])]
            )
        for k, v in averages.items():
            averages[k] = int(v/len(top_performers))

        tpt = Table(
            [performers_columns] + performers_values + [['GROUP AVERAGE', ''] + list(averages.values())],
            colWidths=[170, 50, 60, 60, 60, 90],
            hAlign='LEFT', style=self.normalTable
        )

        tpt_graph = [[Paragraph(top_perf_para, style=self.pstyle), Image(top_perf_graph, width=250, height=200)]]
        lpt_graph = [[Paragraph(low_perf_para, style=self.pstyle), Image(low_perf_graph, width=250, height=200)]]
        tpt_text = Paragraph(top_perf_para, style=self.pstyle)
        tpt_img = Image(top_perf_graph, width=250, height=200, hAlign='RIGHT')

        def altBackground(data, table):
            data_len = len(data) + 1
            for each in range(data_len):
                if each % 2 == 0:
                    bg_color = colors.white
                else:
                    bg_color = colors.lightgrey

                table.setStyle(TableStyle([('BACKGROUND', (0, each), (-1, each), bg_color)]))

        altBackground(low_performers, lpt)
        altBackground(top_performers, tpt)

        if self.language == 'EN':
            '--------------------------------------------------------------------'
            story.append(Paragraph('TOP PERFORMERS', self.h1))
            story.append(
                Paragraph(
                "These are your team's top performers for the period specified on the cover of this report, all names included in this list must have achieved the minimum of 80% control over the car's capabilities.",
                self.pstyle))
            story.append(tpt)
            story.append(Spacer(0, 10))
            story.append(Table(tpt_graph, colWidths=[257, 257], style=self.subTable))
            story.append(Paragraph(top_perf_rev_para, style=self.pstyle))
            story.append(PageBreak())
            story.append(Paragraph('<para color="green">LOW PERFORMERS</para>', self.h1))
            story.append(Paragraph(
                "These are your team's low performers for this period, these include the students that might need some more practice or that were not able to achieve the minimum of 80% contol over the car's capabilities.",
                self.pstyle))
        else:
            '--------------------------------------------------------------------'
            story.append(Paragraph('MEJORES DESEMPEÑOS', self.h1))
            story.append(Paragraph(
                "Estos son los mejores conductores de su equipo durante el período especificado en la portada de este informe, todos los nombres incluidos en esta lista deben haber logrado un control mínimo del 80% sobre la capacidad del automóvil.",
                self.pstyle))
            story.append(tpt)
            story.append(Spacer(0, 10))
            story.append(Table(tpt_graph, colWidths=[257, 257], style=self.subTable))
            story.append(Paragraph(top_perf_rev_para, style=self.pstyle))
            story.append(PageBreak())
            story.append(Paragraph('<para color="green">PEORES DESEMPEÑOS</para>', self.h1))
            story.append(Paragraph(
                "Estos son los jugadores de menor desempeño de su equipo durante este período, estos incluyen a los estudiantes que podrían necesitar más práctica o que no pudieron lograr el control mínimo del 80% sobre las capacidades del automóvil.",
                self.pstyle))
        story.append(lpt)
        story.append(Spacer(0, 20))
        story.append((Table(lpt_graph, colWidths=[257, 257], style=self.subTable)))
        story.append(Paragraph(low_perf_para_lower, style=self.pstyle))
        story.append(PageBreak())
        return story, [top_perf_graph, low_perf_graph]

    def excercise_section(self, performances):
        '-----------------------------------------------------------------------------'
        'Exercise Graphs'
        '-----------------------------------------------------------------------------'
        story = []

        slalom_graph = [self.plotter.plotGlobalExercise(performances["items"], "slalom"), ]
        lnCh_graph = [self.plotter.plotGlobalExercise(performances["items"], "lane_change"), ]
        # count = 2
        # for i in range(1,count):
        #     slalom_plot = 'plots/globalslalomGraph' + str(self.idCompany) + '-' + str(i) +'.png'
        #     lnCh_plot = 'plots/globallane_changeGraph' + str(self.idCompany) + '-' + str(i) +'.png'
        #     slalom_graph.append(slalom_plot)
        #     lnCh_graph.append(lnCh_plot)

        if self.language == "EN":
            with open(os.path.join(dir_path,'texts/[en]slalom_description.txt'), 'r', newline='') as file:
                slalom_pre = file.read()
                slalom_text = slalom_pre
            with open(os.path.join(dir_path,'texts/[en]lnch_description.txt'), 'r', newline='') as file:
                lnch_pre = file.read()
                lnch_text = lnch_pre
            slalom_avg_control_txt = """The group's average top performance was: """ + str(performances["items"]["slalom"]["avg_pvehicles"]) + """%"""
            slalom_above_below_txt = str(performances["items"]["slalom"]["pvehicles_above_avg"]) + """ students are above the average of control, while """ + str(performances["items"]["slalom"]["pvehicles_below_avg"]) + """ where below the group average."""
            slalom_avg_tries_txt = """<span fontName=MontserratBold>The group's average tries was:</span> """ + str(performances["items"]["slalom"]["avg_tries"]) + """, and the students achieved the minimum standard on average """ + str(performances["items"]["slalom"]["gp_met_std"]) + """ times (please refer to the individual reports for each student stats)."""
            # ------------------------------------
            lnch_avg_control_txt = """The group's average top performance was: """ + str(performances["items"]["lane_change"]["avg_pvehicles"]) + """%"""
            lnch_above_below_txt = str(performances["items"]["lane_change"]["pvehicles_above_avg"]) + """ students are above the average of control, while """ + str(performances["items"]["lane_change"]["pvehicles_below_avg"]) + """ where below the group average."""
            lnch_avg_tries_txt = """<span fontName=MontserratBold>The group's average tries was:</span> """ + str(performances["items"]["lane_change"]["avg_tries"]) + """, a considerable improvement over slalom's average of """ + str(performances["items"]["slalom"]["avg_tries"]) + """, at this point skill buildup starts to become evident; the students achieved the minimum standard on average """ + str(performances["items"]["lane_change"]["gp_met_std"]) + """ times (please refer to the individual reports for each student stats)."""
        else:
            with open(os.path.join(dir_path,'texts/[es]slalom_description.txt'), 'r', newline='') as file:
                slalom_pre = file.read()
                slalom_text = slalom_pre
            with open(os.path.join(dir_path,'texts/[es]lnch_description.txt'), 'r', newline='') as file:
                lnch_pre = file.read()
                lnch_text = lnch_pre
            # ------------------------------------
            slalom_avg_control_txt = """El rendimiento máximo promedio del grupo fue: """ + str(performances["items"]["slalom"]["avg_pvehicles"]) + """%"""
            slalom_above_below_txt = str(performances["items"]["slalom"]["pvehicles_above_avg"]) + """ los estudiantes están por encima del promedio de control, mientras que """ + str(performances["items"]["slalom"]["pvehicles_below_avg"]) + """ están por debajo del promedio del grupo."""
            slalom_avg_tries_txt = """<span fontName=MontserratBold>El promedio de intentos del grupo fue:</span> """ + str(performances["items"]["slalom"]["avg_tries"]) + """, y los estudiantes lograron el estándar mínimo en promedio """ + str(performances["items"]["slalom"]["gp_met_std"]) + """ veces (consulte los informes individuales para las estadísticas de cada estudiante)."""
            # ------------------------------------
            lnch_avg_control_txt = """El rendimiento máximo promedio del grupo fue: """ + str(performances["items"]["lane_change"]["avg_pvehicles"]) + """%"""
            lnch_above_below_txt = str(performances["items"]["lane_change"]["pvehicles_above_avg"]) + """ estudiantes están por encima del promedio de control, mientras que """ + str(performances["items"]["lane_change"]["pvehicles_below_avg"]) + """ están por debajo del promedio del grupo."""
            lnch_avg_tries_txt = """<span fontName=MontserratBold>El promedio de intentos del grupo fue:</span> """ + str(performances["items"]["lane_change"]["avg_tries"]) + """, una mejora considerable sobre promedio de slalom de """ + str(performances["items"]["slalom"]["avg_tries"]) + """, en este punto la acumulación de habilidades comienza a ser evidente; los estudiantes alcanzaron el estándar mínimo en promedio """ + str(performances["items"]["lane_change"]["gp_met_std"]) + """ veces (consulte los reportes individuales para las estadísticas de cada alumno)."""


        # -------------------------------Slalom Graph
        story.append(Paragraph('SLALOM', self.h1))
        story.append(Paragraph(slalom_text, self.pstyle))
        story.append(Spacer(0, 20))
        if self.language == 'EN':
            story.append(Paragraph(
                '<para font=MontserratBold>Type:</para><para font=MontserratLight> Regular Slalom – 4 Cones (50ft Chord)</para>',
                style=self.h2))
            story.append(
                Paragraph('<para font=MontserratBold>Difficulty Level:</para><para font=MontserratLight> Medium / Hard</para>',
                        style=self.h2))
        else:
            story.append(Paragraph(
                '<para font=MontserratBold>Tipo:</para><para font=MontserratLight> Slalom Regular – 4 Conos (15.24m Chord)</para>',
                style=self.h2))
            story.append(
                Paragraph(
                    '<para font=MontserratBold>Nivel De Dificultad:</para><para font=MontserratLight> Medio / Difícil</para>',
                    style=self.h2))
        story.append(Spacer(0, 20))
        for graph in slalom_graph: story.append(Image(graph, width=514, height=214))
        story.append(Paragraph(slalom_avg_control_txt, style=self.h2))
        story.append(Paragraph(slalom_above_below_txt, style=self.subh2))
        story.append(Spacer(0, 20))
        story.append(Paragraph(slalom_avg_tries_txt, style=self.subh2))
        story.append(PageBreak())
        # -------------------------------Lane Chage Graph
        if self.language == 'EN':
            story.append(Paragraph('BARRICADE EVASION (Lane Change)', self.h1))
            story.append(Paragraph(lnch_text, self.pstyle))
            story.append(Spacer(0, 20))
            story.append(Paragraph(
                '<para font=MontserratBold>Type:</para><para font=MontserratLight> Regular LnCh – .75 Sec Reaction time (100ft Chord)</para>',
                style=self.h2))
            story.append(
                Paragraph('<para font=MontserratBold>Difficulty Level:</para><para font=MontserratLight> Medium</para>',
                        style=self.h2))
        else:
            story.append(Paragraph('EVASIÓN DE BARRICADA (Lane Change)', self.h1))
            story.append(Paragraph(lnch_text, self.pstyle))
            story.append(Spacer(0, 20))
            story.append(Paragraph(
                '<para font=MontserratBold>Tipo:</para><para font=MontserratLight> LnCh Regular – .75 Seg Tiempo de Reacción (30.48m Chord)</para>',
                style=self.h2))
            story.append(
                Paragraph('<para font=MontserratBold>Nivel de Dificultad:</para><para font=MontserratLight> Medio</para>',
                        style=self.h2))


        story.append(Spacer(0, 20))
        for graph in lnCh_graph : story.append(Image(graph, width=514, height=214))
        story.append(Paragraph(lnch_avg_control_txt, style=self.h2))
        story.append(Paragraph(lnch_above_below_txt, style=self.subh2))
        story.append(Spacer(0, 20))
        story.append(Paragraph(lnch_avg_tries_txt, style=self.subh2))
        story.append(PageBreak())
        all_images = []
        all_images.extend(slalom_graph)
        all_images.extend(lnCh_graph)
        return story, all_images
    
    def final_excercise_section(self, data):
        story = []
        mse_graph = self.plotter.plotScatterPlot(data["items"])

        if self.language == 'EN':
            with open(os.path.join(dir_path,'texts/[en]final_exercise.txt'), 'r', newline='') as file:
                mse_pre = file.read()
                mse_text = mse_pre
            story.append(Paragraph('FINAL EXERCISE', self.h1))
        else:
            with open(os.path.join(dir_path,'texts/[es]final_exercise.txt'), 'r', newline='') as file:
                mse_pre = file.read()
                mse_text = mse_pre
            story.append(Paragraph('EJERCICIO FINAL', self.h1))
        story.append(Paragraph(mse_text, self.pstyle))
        story.append(Spacer(0, 20))
        # story.append(Paragraph('<para font=MontserratBold>Type:</para><para font=MontserratLight> Regular LnCh – .75 Sec Reaction time (100ft Chord)</para>', style=h2))
        # story.append(Paragraph('<para font=MontserratBold>Difficulty Level:</para><para font=MontserratLight> Medium</para>', style=h2))
        # story.append(Spacer(0,10))
        story.append(Image(mse_graph, width=514, height=226))
        story.append(PageBreak())

        return story, [mse_graph]
    
    def conclusion_section(self):
        story = []
        if self.language == 'EN':
            with open(os.path.join(dir_path, 'texts/[en]conclusions.txt'), 'r', newline='') as file:
                conclusions_pre = file.read()
                conclusions_text = conclusions_pre
        else:
            with open(os.path.join(dir_path, 'texts/[es]conclusions.txt'), 'r', newline='') as file:
                conclusions_pre = file.read()
                conclusions_text = conclusions_pre
        # ------------------------------Conclusions --------------------------
        story.append(Paragraph('CONCLUSION', style=self.h1))
        story.append(Spacer(0, 20))
        story.append(Paragraph(conclusions_text, style=self.pstyle))
        
        return story, []
