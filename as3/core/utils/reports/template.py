from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.styles import ParagraphStyle as PS
from reportlab.platypus import PageBreak, Table, NextPageTemplate, Image, Spacer, Flowable, TableStyle
from reportlab.platypus.paragraph import Paragraph
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from reportlab.pdfbase.pdfmetrics import registerFont, registerFontFamily
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.platypus.frames import Frame
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm, inch
from reportlab.lib import colors
from functools import partial
from reportlab.lib.pagesizes import letter
from reportlab.lib.fonts import addMapping
from PIL import Image as pImage
import os
import io
from django.conf import settings

dir_path = settings.STATIC_ROOT + "/reports/"

'-----------------------------------------------------------------------------'
'Template'
'-----------------------------------------------------------------------------'
class DocTemplate(BaseDocTemplate):
    def __init__(self, filename, language, **kw):
        self.allowSplitting = 0
        BaseDocTemplate.__init__(self, filename, **kw)
        print("LANGUAGE: ",language)
        self.regitser_fonts()
        self.add_mapping()
        self.set_page_writers()
        self.set_styles()
        self.header_content, self.footer_content = self.create_deco(language)
        page_size = letter
        pwidth, pheight = letter
        if language == 'EN':
            template_CoverPage = PageTemplate('CoverPage',
                                              [Frame(.8 * cm, pheight / 2 - (inch * 1.5), pwidth / 2, 130, id='F1',
                                                     showBoundary=0)],
                                              onPage=self.createCover,
                                              )
        else:
            template_CoverPage = PageTemplate('CoverPage',
                                              [Frame(.8 * cm, pheight / 2 - (inch * 1.5), pwidth / 2, 130, id='F1',
                                                     showBoundary=0)],
                                              onPage=self.createCoverEspaniol,
                                              )


        template_NormalPage = PageTemplate('NormalPage',
                                           [Frame(pwidth * .08, 2.5 * cm, pwidth * .84, pheight * .8, id='F2',
                                                  showBoundary=0)],
                                           onPage=partial(self.header_and_footer,
                                                          header_content=self.header_content,
                                                          footer_content=self.footer_content),
                                           pagesize=page_size)

        template_SecondPage = PageTemplate('SecondPage',
                                           [Frame(pwidth * .08, pheight * .37, pwidth * .84, pheight * .50, id='F3',
                                                  showBoundary=0),
                                            Frame(pwidth * .08, 3 * cm, pwidth * .42, pheight * .25, id='F4',
                                                  showBoundary=0),
                                            Frame(pwidth * .50, 3 * cm, pwidth * .42, pheight * .25, id='F5',
                                                  showBoundary=0)],
                                           onPage=partial(self.header_and_footer,
                                                          header_content=self.header_content,
                                                          footer_content=self.footer_content),
                                           pagesize=page_size)

        self.addPageTemplates([template_CoverPage, template_NormalPage, template_SecondPage])

    '-----------------------------------------------------------------------------'
    'Cover Page'
    '-----------------------------------------------------------------------------'
    @staticmethod
    def createCover(canvas, doc):
        page_width, page_height = canvas._pagesize
        file_path = os.path.join(dir_path, 'logos/Cover-Page---Performance-Reports.png')
        image = pImage.open(file_path)
        image_width, image_height = image.size
        draw_width, draw_height = page_width, page_height

        canvas.drawImage(
            file_path,
            0, 0, width=draw_width, height=draw_height,
            preserveAspectRatio=True
        )

    def create_deco(self, language):
        ## Header -----------
        pwidth, pheight = letter
        '-----------------------------------------------------------------------------'
        'Variables'
        '-----------------------------------------------------------------------------'
        logo_int = os.path.join(dir_path, 'logos/Logo---AS3-international-200x200.png')
        ceo_cfo = os.path.join(dir_path, 'logos/The-CFO-to-the-CEO---Logo.png')
        ceo_cfo_inv = os.path.join(dir_path, 'logos/The-CFO-to-the-CEO---Logo_Inverted.png')
        ceo_cfo_inv_es = os.path.join(dir_path, 'logos/[ES]-The-CFO-to-the-CEO---Logo_inv.png')
        as3_logo = os.path.join(dir_path, 'logos/AS3 Driver Training - Logo.png')
        
        header_center_text = 'header_center_text foo'
        footer_center_text = 'footer_center_text bar'
        Header_caption = ((header_center_text))
        A = 'Author'
        if language == 'EN':
            Header_table_data = [[Image(ceo_cfo_inv, width=230, height=73)]]

            Header_table = Table(Header_table_data,
                                colWidths=[pwidth * .84],
                                rowHeights=[3 * cm],
                                style=[
                                    # ('GRID',(0,0),(1,2),1,colors.black),
                                    # #('ALIGN',(0,0),(1,0),'CENTER'),
                                    ('ALIGN', (0, 0), (0, 0), 'RIGHT'),
                                    # ('VALIGN',(0,0),(3,2),'MIDDLE'),
                                    # ('ALIGN',(2,0),(3,2),'RIGHT'),
                                    # ('SPAN',(0,0),(0,2)),
                                    # ('SPAN',(1,0),(1,2)),
                                    # ('BOX',(2,0),(-1,-1),1,colors.black),
                                    # ('TEXTCOLOR',(0,0),(3,0),colors.Color(49/255,71/255,137/255))
                                ])
            # 'Footer' ----------
            Footer_table_data = [[Image(as3_logo,
                                        width=144,
                                        height=60),
                                Paragraph(
                                    '<para color="black">WWW.</para><para color="#C10230">AS3</para><para color="black">INTERNATIONAL.US</para>',
                                    self.h2)]
                                ]
            Footer_table = Table(Footer_table_data, colWidths=[(pwidth * .84) / 2, (pwidth * .84) / 2], rowHeights=[1 * cm],
                                style=[
                                    # ('GRID',(0,0),(-1,-1),1,colors.black),
                                    # ('ALIGN',(0,0),(1,0),'CENTER'),
                                    ('ALIGN', (0, 1), (-1, -1), 'RIGHT'),
                                    ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
                                    # ('ALIGN',(0,0),(3,0),'CENTER'),
                                    # ('TEXTCOLOR',(0,0),(3,0),colors.Color(49/255,71/255,137/255))
                                ])
        else:
            Header_table_data = [[Image(ceo_cfo_inv_es, width=230, height=73)]]
            Header_table = Table(Header_table_data,
                                colWidths=[pwidth * .84],
                                rowHeights=[3 * cm],
                                style=[
                                    # ('GRID',(0,0),(1,2),1,colors.black),
                                    # #('ALIGN',(0,0),(1,0),'CENTER'),
                                    ('ALIGN', (0, 0), (0, 0), 'RIGHT'),
                                    # ('VALIGN',(0,0),(3,2),'MIDDLE'),
                                    # ('ALIGN',(2,0),(3,2),'RIGHT'),
                                    # ('SPAN',(0,0),(0,2)),
                                    # ('SPAN',(1,0),(1,2)),
                                    # ('BOX',(2,0),(-1,-1),1,colors.black),
                                    # ('TEXTCOLOR',(0,0),(3,0),colors.Color(49/255,71/255,137/255))
                                ])
            ## 'Footer'
            Footer_table_data = [[Image(as3_logo,
                                        width=144,
                                        height=60),
                                Paragraph(
                                    '<para color="black">WWW.SECURITYDRIVING.MX</para>',
                                    self.h2)]
                                ]
            Footer_table = Table(Footer_table_data, colWidths=[(pwidth * .84) / 2, (pwidth * .84) / 2], rowHeights=[1 * cm],
                                style=[
                                    # ('GRID',(0,0),(-1,-1),1,colors.black),
                                    # ('ALIGN',(0,0),(1,0),'CENTER'),
                                    ('ALIGN', (0, 1), (-1, -1), 'RIGHT'),
                                    ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
                                    # ('ALIGN',(0,0),(3,0),'CENTER'),
                                    # ('TEXTCOLOR',(0,0),(3,0),colors.Color(49/255,71/255,137/255))
                                ])


        # footer_content = Footer_table
        # header_content = Header_table
        return Header_table, Footer_table
    
    @staticmethod
    def createCoverEspaniol(canvas, doc):
        page_width, page_height = canvas._pagesize
        image = pImage.open(os.path.join(dir_path, 'logos/[ES]-Cover-Page---Performance-Reports.png'))
        image_width, image_height = image.size
        draw_width, draw_height = page_width, page_height

        canvas.drawImage(
            os.path.join(dir_path, 'logos/[ES]-Cover-Page---Performance-Reports.png'),
            0, 0, width=draw_width, height=draw_height,
            preserveAspectRatio=True)

    def afterFlowable(self, flowable):
        "Registers TOC entries."
        if flowable.__class__.__name__ == 'Paragraph':
            text = flowable.getPlainText()
            style = flowable.style.name
            if style == 'Heading1':
                self.notify('TOCEntry', (0, text, self.page))
            if style == 'Heading2':
                self.notify('TOCEntry', (1, text, self.page))

    '-----------------------------------------------------------------------------'
    'Header and Footer'
    '-----------------------------------------------------------------------------'
    def header(self, canvas, doc, content):
        canvas.saveState()
        w, h = content.wrap(doc.width, doc.topMargin)
        content.drawOn(canvas, doc.leftMargin - 22.4, doc.height + doc.bottomMargin + doc.topMargin - h - 10)
        canvas.restoreState()

    def footer(self, canvas, doc, content):
        self.drawPageNumber(canvas, doc)
        canvas.saveState()
        w, h = content.wrap(doc.width, doc.bottomMargin)
        content.drawOn(canvas, doc.leftMargin - 22.4, h)
        canvas.restoreState()

    def header_and_footer(self, canvas, doc, header_content, footer_content):
        self.header(canvas, doc, header_content)
        self.footer(canvas, doc, footer_content)

    def drawPageNumber(self, canvas, doc):
        pageNumber = canvas.getPageNumber()
        # canvas.setFont("Helvetica",11)
        # canvas.drawCentredString(17.4*cm, 1.35*cm, 'Page '+str(pageNumber))

    def PageNumber(self, canvas, doc):
        return (canvas.getPageNumber())
    
    def set_styles(self):
        self.normalTable = TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Montserrat'),
            ('FONTNAME', (0, -1), (-1, -1), 'Montserrat'),
            ('FONTNAME', (0, 1), (-1, -2), 'MontserratLight'),
            #     ('GRID',(0,0),(-1,-1),.5,colors.black),
            ('ALIGN', (1, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.black),
            ('LINEABOVE', (0, -1), (-1, -1), .5, colors.black),
            ('LINEBELOW', (0, -1), (-1, -1), 2, colors.black),
        ])

        self.subTable = TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'MontserratLight'),
            #     ('GRID',(0,0),(-1,-1),.5,colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('TOPPADDING', (0, 0), (0, 0), 10)
        ])

    def set_page_writers(self):
        self.h1 = PS(name='Heading1',
            fontSize=18,
            leading=20,
            fontName='MontserratBold',
            textColor="#C10230",
            spaceAfter=8,
            spaceBefore=8)

        self.h2 = PS(name='Heading2',
                fontSize=14,
                fontName='MontserratBold',
                leading=16,
                leftIndent=5)
        self.subh2 = PS(name='SubHeading2',
                fontSize=14,
                fontName='Montserrat',
                leading=16,
                leftIndent=5)
        self.l0 = PS(name='list0',
                fontSize=12,
                leading=14,
                leftIndent=0,
                rightIndent=0,
                spaceBefore=12,
                spaceAfter=0
                )
        self.pstyle = PS(name='ms',
                    fontName='MontserratLight',
                    fontSize=10,
                    leading=14,
                    spaceAfter=8,
                    spaceBefore=8
                    )
        self.footertxt = PS(name='footer',
                    fontName='MontserratThin',
                    fontSize=9,
                    leading=9,
                    )
        self.super_h1 = PS(name='Super_Heading1',
                    fontSize=80,
                    leading=0,
                    fontName='MontserratBold',
                    textColor="#C10230",
                    spaceAfter=0,
                    spaceBefore=0)
        self.ttl = PS(name='Title',
                fontSize=24,
                leading=25,
                fontName='MontserratBlack',
                textColor="#FFFFFF",
                spaceAfter=20,
                spaceBefore=20)

    @staticmethod
    def regitser_fonts():
        '-----------------------------------------------------------------------------'
        'Register Fonts'
        '-----------------------------------------------------------------------------'
        registerFont(TTFont('MontserratBold',
                            os.path.join(dir_path,'fonts/Montserrat-ExtraBold.ttf')))
        registerFont(
            TTFont('MontserratBlack', os.path.join(dir_path,'fonts/Montserrat-Black.ttf')))
        registerFont(
            TTFont('Montserrat', os.path.join(dir_path,'fonts/Montserrat-Regular.ttf')))
        registerFont(
            TTFont('MontserratLight', os.path.join(dir_path,'fonts/Montserrat-Light.ttf')))
        registerFont(
            TTFont('MontserratThin', os.path.join(dir_path, 'fonts/Montserrat-Thin.ttf')))

    @staticmethod
    def add_mapping():
        # addMapping('SabonRom', 0, 0, 'SabonRom') #normal
        # addMapping('SabonRom', 0, 1, 'SabonIta') #italic
        addMapping('MontserratLight', 1, 0, 'MontserratBold')  # bold
        # addMapping('SabonRom', 1, 1, 'SabonBolIta') #italic and bold
        # heavy = ParagraphStyle(name='normal', fontName='SabonRom', fontSize=10, leading=1.4*10 )
