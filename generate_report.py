from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import Color, black, blue, red
from reportlab.platypus import Paragraph
import datetime
#from website_backend import *
from PyPDF2 import PdfFileWriter, PdfFileReader
import io
from reportlab.lib.styles import (ParagraphStyle, getSampleStyleSheet)



# width of letter is: 612
# height of letter is: 792
# unit of x,y,width,height is 1/72 of an inch

path  = 'relative path'
places = {"boston": 'bongo-bongo/data/hypothesis_testing_data/boston_bg_census_and_connectivity.geojson',
            "nyc": 'bongo-bongo/data/hypothesis_testing_data/nyc_bg_census_and_connectivity.geojson',
            "chicago": 'bongo-bongo/data/hypothesis_testing_data/chicago_bg_census_and_connectivity.geojson',
            "ri": 'bongo-bongo/data/hypothesis_testing_data/ri_bg_census_and_connectivity.geojson'}

#generate_report(city= city_name, pretty_city=pretty_city, test=test, pretty_test=pretty_test,\
        #      demog_var= demog, pretty_demog_var=pretty_demog, categ1=categ_1, pretty_categ_1= pretty_categ_1, \
        #           categ2 = categ_2, pretty_categ_2= pretty_categ_2, conn_var=conn, pretty_conn_var=pretty_conn)

# def title_page1(c, city= None, test= None, demog_var= None, categ1= None, categ2= None, conn_var= None):
#     df = gpd.read_file(path + places[city])
#     plt.rc('legend', **{'fontsize': 32})
#     if test == "ttest":
#         pvalue, tstats, sig = ttest_results(df, city, demog_var, categ1, categ2, conn_var)
#         graph_connectivity_in_category(df, city, demog_var, categ1, conn_var)
#         graph_connectivity_in_category(df, city, demog_var, categ2, conn_var)
#     elif test == "chi_squared_test":
#         # Note the difference in max's on the color bars. Check your test result to see why this has happened
#         pvalue, tstats, sig = chi_squared_test_results(df, city, demog_var)
#         graph_categories(df, city, "label") # Connectivity
#         graph_categories(df, city, demog_var) # Demog var
#      # Fix the saving of things and the printing of things
#
#
#
#
#     #### TITLE PAGE ####
#
#     theme = Color(255/256, 189/256, 89/256, alpha=1)
#
#     ## ELEMENTS ##
#
#     # Top yellow rectangle
#     c.setFillColor(theme)
#     c.rect(0, 792-3*72, 8.5*72, 3*72, fill=True, stroke=False)
#
#     # Thin line bottom
#     c.rect(612/2-6.7*72/2, 792/2-8*72/2, 6.7*72, 7.2, fill=True, stroke=False)
#
#     # Image
#     c.drawImage("/Users/herberttraub/PycharmProjects/Data_Science/bongo-bongo/report_things/b.png",
#                 612/2-6.7*72/2, 792/2-7*72/2, width=6.7*72, height=8.5*72)
#
#     # Thin line top right
#     c.setFillColor(black)
#     c.rect(7.2 * 72 - 80, 603 + .75 * 72 - 14, 80, 1, fill=True, stroke=False)
#
#     ## TEXT ##
#
#     # 2022 POI Report
#     c.setFillColor(theme)
#     c.setFont('Helvetica-Bold', 53)
#     c.drawString(100,5*72,"2022")
#     c.drawString(100,4*72, "P.O.I.")
#     c.drawString(100, 3*72, "REPORT")
#
#     # Bottom right info
#     c.setFont('Helvetica', 18)
#     lines = [
#         "DEMOGRAPHCICS &",
#         "INFRASTRUCTURE",
#     ]
#     ys = [70,45]
#     for y, line in zip(ys, lines):
#         c.drawRightString(545, y, line)
#
#     # Top right description
#     c.setFillColor(black)
#     size = 13
#     c.setFont('Times-Roman', size)
#     lines = [
#         "A report on the",
#         "difference between x",
#         "and for y and x",
#         "and y and z",
#     ]
#     ys = list(range(int(792 - .8 * 72 - 16), int(792 - .8 * 72 - len(lines) * size -16), -1 * size - 4))
#     for y, line in zip(ys, lines):
#         c.drawRightString(7.2 * 72, y, line)
#
#     # Authors
#     lines = [
#         "William Back",
#         "Dhruv Bhatia",
#         "Niyoshi Parekh",
#         "Herbert Traub",
#     ]
#     ys = list(range(int(792-3*72+.7*72-14), int(792-3*72-len(lines)*size+.7*72-14),-1 * size - 4))
#     for y, line in zip(ys, lines):
#         c.drawRightString(7.2*72, y, line)
#
#     # Bottom left info
#     c.setFont('Times-Roman', 18)
#     c.drawString(612/2-6.7*72/2, 70, "CSCI 1951A")
#     c.drawString(612/2-6.7*72/2,45, f"{datetime.date.today()}")
#     print("Your report has been saved to somewhere.")
#
# #generate_report(city= city_name, pretty_city=pretty_city, test=test, pretty_test=pretty_test,\
#         #      demog_var= demog, pretty_demog_var=pretty_demog, categ1=categ_1, pretty_categ_1= pretty_categ_1, \
#         #           categ2 = categ_2, pretty_categ_2= pretty_categ_2, conn_var=conn, pretty_conn_var=pretty_conn)
#

def title_page(pretty_city="", pretty_test="", pretty_demog_var="", pretty_categ_1="", pretty_categ_2="",
               pretty_conn_var=None):
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=letter)

    ## ELEMENTS ##
    # Thin line top right
    c.setFillColor(black)
    c.rect(7.2 * 72 - 80, 603 + .75 * 72 - 14, 80, 1, fill=True, stroke=False)

    ## TEXT ##

    # Top right description
    c.setFillColor(black)
    size = 10
    c.setFont('Times-Roman', size)
    if pretty_test == "Chi-Squared Independence Test":
        lines = [
            f"A {pretty_test}",
            "analyzing the relationship ",
            f"between block groups of",
            f"different {pretty_demog_var.lower()}s",
            f"for {pretty_city}",
        ]
    else:
        lines = [
            f"A {pretty_test} on",
            f"{pretty_categ_1} and",
            f"{pretty_categ_2}",
            f"block groups with respect",
            f"to connectivity to {pretty_conn_var}s",
            f"for {pretty_city}",
        ]

    ys = list(range(718, 650, -1 * size - 4))
    for y, line in zip(ys, lines):
        c.drawRightString(7.2 * 72, y, line)


    # Authors
    authors = [
        "William Back",
        "Dhruv Bhatia",
        "Niyoshi Parekh",
        "Herbert Traub",
    ]
    ys = list(range(620, 570,
                    -1 * size - 4))
    for y, line in zip(ys, authors):
        c.drawRightString(7.2 * 72, y, line)
    c.save()

    # move to the beginning of the StringIO buffer
    packet.seek(0)
    # create a new PDF with Reportlab
    new_pdf = PdfFileReader(packet)
    # read your existing PDF
    existing_pdf = PdfFileReader(open("/Users/herberttraub/PycharmProjects/Data_Science/bongo-bongo/report_things/title_page.pdf", "rb"))
    output = PdfFileWriter()
    # add the "watermark" (which is the new pdf) on the existing page
    page = existing_pdf.getPage(0)
    page.mergePage(new_pdf.getPage(0))
    output.addPage(page)
    # finally, write "output" to a real file
    outputStream = open("/Users/herberttraub/PycharmProjects/Data_Science/custom_title_page.pdf", "wb")
    output.write(outputStream)
    outputStream.close()

def test_page(city=None, pretty_city=None, test=None, pretty_test=None, category_1=None, pretty_categ1=None, category_2=None, pretty_categ2=None,
              conn_var=None, pretty_conn_var=None):
    style = getSampleStyleSheet()
    yourStyle = ParagraphStyle('yourtitle',
                               fontName="Times-Roman",
                               fontSize=12,
                               parent=style['Heading2'],
                               alignment=0,
                               spaceAfter=2)
    if test=="ttest":
        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=letter)
        pvalue = 0
        tstats=0
        ## TEXT ##
        null = f'''Null Hypothesis: {pretty_categ1} and {pretty_categ2} block groups in {pretty_city} have the same {pretty_conn_var} connectivity scores. <br/><br/>
        Alternative Hypothesis: {pretty_categ1} and {pretty_categ2} block groups in {pretty_city} have different {pretty_conn_var} connectivity scores. <br/><br/>'''

        #c.drawRightString(7.2 * 72, 300, null)

        # alt = Paragraph(f"Alternative Hypothesis: {pretty_categ1} and {pretty_categ2} block groups in {pretty_city} have different {pretty_conn_var} connectivity scores.", style=yourStyle)
        # alt.wrap(7.3*72,100)
        # null.drawOn(c, 42, 100)

        # Result
        text_out = ""
        if pvalue/2 > 0.05:
            null += f'The two-sided p-value was {pvalue} with t-statistic {tstats}. Since p-value/2 > 0.05, we accept the null hypothesis.'
        else:
            if tstats <= 0:
                null += f'The two-sided p-value was {pvalue} with t-statistic {tstats}. Since p-value/2 < 0.05, we reject the null hypothesis. Since t-statistic < 0, we conclude that {category_1} block groups have lower {conn_var} connectivity scores than {category_2} block groups.'
            else:
                null += f'The two-sided p-value was {pvalue} with t-statistic {tstats}. Since p-value/2 <= 0.05, we reject the null hypothesis. Since t-statistic > 0, we conclude that {category_1} block groups have higher {conn_var} connectivity scores than {category_2} block groups.'
        text_out = Paragraph(null, style = yourStyle)

        text_out.wrap(7.3*72,100)

        text_out.drawOn(c, 42, 420)

        # c.drawRightString(500, 200, lines[0])
        # c.drawRightString(550, 180, lines[1])
        c.save()

        # move to the beginning of the StringIO buffer
        packet.seek(0)
        # create a new PDF with Reportlab
        new_pdf = PdfFileReader(packet)
        # read your existing PDF
        existing_pdf = PdfFileReader(open("/Users/herberttraub/PycharmProjects/Data_Science/bongo-bongo/report_things/ttest_page.pdf", "rb"))
        output = PdfFileWriter()
        # add the "watermark" (which is the new pdf) on the existing page
        page = existing_pdf.getPage(0)
        page.mergePage(new_pdf.getPage(0))
        output.addPage(page)
        # finally, write "output" to a real file
        outputStream = open("/Users/herberttraub/PycharmProjects/Data_Science/custom_ttest_page.pdf", "wb")
        output.write(outputStream)
        outputStream.close()



city="ri"
pretty_city="Rhode Island"
test='ttest'
#test='chi_squared_test'
pretty_test="Two-Tailed Independent T Test"
#pretty_test="Chi-Squared Independence Test"
demog_var="race"
pretty_demog_var="Race"
categ1="Black or African American alone"
pretty_categ_1="Black or African American alone"
categ2 ="Native Hawaiian and Other Pacific Islander alone"
pretty_categ_2="Native Hawaiian and Other Pacific Islander alone"
conn_var='School'
pretty_conn_var="School"


def generate_report():
    #title_page(pretty_city, pretty_test, pretty_demog_var, pretty_categ_1, pretty_categ_2, pretty_conn_var)
    test_page(city, pretty_city, test, pretty_test, categ1, pretty_categ_1, categ2, pretty_categ_2,
              conn_var, pretty_conn_var)


# c = canvas.Canvas("report.pdf", pagesize=letter)
# generate_report(c)
#
# c.showPage()
# c.save()

generate_report()