import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import black
from reportlab.platypus import Paragraph, Image
from stats import *
from PyPDF2 import PdfFileWriter, PdfFileReader
import io
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
import geopandas as gpd
import PIL as pil


# Useful things to know
# Width of letter is: 612
# Height of letter is: 792
# Unit of x,y,width,height is 1/72 of an inch

MARGIN_WIDTH = 7.3*72

# File paths
full_path = os.getcwd()
data_path = {"boston": full_path + os.sep + 'hypothesis_testing_data' + os.sep + "boston_bg_census_and_connectivity.geojson",
            "nyc": full_path + os.sep + 'hypothesis_testing_data' + os.sep + 'nyc_bg_census_and_connectivity.geojson',
            "chicago": full_path + os.sep + 'hypothesis_testing_data' + os.sep + 'chicago_bg_census_and_connectivity.geojson',
            "ri": full_path + os.sep + 'hypothesis_testing_data' + os.sep + 'ri_bg_census_and_connectivity.geojson'}
templates_path = full_path + os.sep + "report_things" + os.sep + "templates" + os.sep
custom_page_path = full_path + os.sep + "report_things" + os.sep + "custom" + os.sep
image_path = full_path + os.sep + "report_things" + os.sep + "images" + os.sep
final_report_path = full_path + os.sep + "report_things" + os.sep + "final_report" + os.sep + "final_report.pdf"


def title_page(pretty_city=None, pretty_test=None, pretty_demog_var=None, pretty_categ_1=None,
               pretty_categ_2=None, pretty_conn_var=None):
    """
    Generates a custom title page.
    :param pretty_city: Pretty city name
    :param pretty_test: City name
    :param pretty_demog_var: Pretty demographic variable
    :param pretty_categ_1: Pretty category 1 variable
    :param pretty_categ_2:  Pretty category 2 variable
    :param pretty_conn_var:  Pretty connectivity variable
    """
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
    pretty_demog_var = pretty_demog_var if pretty_demog_var != "Ethnicity" else "Ethnicitie"
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
            f"to connectivity to {pretty_conn_var.lower()}s",
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

    packet.seek(0)
    new_pdf = PdfFileReader(packet)
    existing_pdf = PdfFileReader(
        open(f"{templates_path}title_page.pdf", "rb"))
    output = PdfFileWriter()
    page = existing_pdf.getPage(0)
    page.mergePage(new_pdf.getPage(0))
    output.addPage(page)

    # Save file
    outputStream = open(f"{custom_page_path}custom_title_page.pdf", "wb")
    output.write(outputStream)
    outputStream.close()


def cluster_page(city=None):
    """
    Generates a custom clustering page.
    :param city: City name
    """
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=letter)

    ## ELEMENTS ##
    c.setFillColor(black)
    w = 450
    h = 450
    im = Image(f"{image_path}{city}_validation.png", width=w, height=h)
    im.hAlign = "CENTER"
    im.drawOn(c, 612/2-w/2, 140)
    c.save()

    packet.seek(0)
    new_pdf = PdfFileReader(packet)
    existing_pdf = PdfFileReader(open(f"{templates_path}clustering.pdf", "rb"))
    output = PdfFileWriter()
    page = existing_pdf.getPage(0)
    page.mergePage(new_pdf.getPage(0))
    output.addPage(page)

    # Save file
    outputStream = open(f"{custom_page_path}custom_cluster_page.pdf", "wb")
    output.write(outputStream)
    outputStream.close()


def test_page(city=None, pretty_city=None, test=None, demog_var=None, pretty_demog_var=None, category_1=None,
              pretty_categ1=None, category_2=None, pretty_categ2=None, conn_var=None, pretty_conn_var=None):
    """
    Generates a custom test page.
    :param city: City name
    :param pretty_city: Pretty city name
    :param test: Test name
    :param demog_var: Demographic variable
    :param pretty_demog_var: Pretty demographic variable
    :param category_1: Category 1 variable
    :param pretty_categ1: Pretty category 1 variable
    :param category_2: Category 2 variable
    :param pretty_categ2: Pretty category 2 variable
    :param conn_var: Connectivity variable
    :param pretty_conn_var: Pretty connectivity variable
    """
    style = getSampleStyleSheet()
    hyp_style = ParagraphStyle('hypstyle',
                               fontName="Times-Roman",
                               fontSize=12,
                               parent=style['Heading2'],
                               alignment=0,
                               spaceAfter=2,
                               leading=12
                               )
    df = gpd.read_file(data_path[city]).dropna()
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=letter)

    if test == "ttest":
        pvalue, tstats, sig = ttest_results(df, city, demog_var, category_1, category_2, conn_var,
                                            make_ind_file=False)
        graph_connectivity_in_category(df, demog_var, category_1, conn_var, save_path=image_path + f"{city}_{demog_var}_{pretty_categ1}_{conn_var}.png")
        graph_connectivity_in_category(df, demog_var, category_2, conn_var, save_path=image_path + f"{city}_{demog_var}_{pretty_categ2}_{conn_var}.png")

        # IMAGES
        if city == 'nyc':
            nyc_borders = (370, 580, 2700, 2500)
            g1 = pil.Image.open(f"{image_path}{city}_{demog_var}_{pretty_categ1}_{conn_var}.png")
            g1c = g1.crop(nyc_borders)
            g1c.save(image_path+"cropped1.png")
            g2 = pil.Image.open(f"{image_path}{city}_{demog_var}_{pretty_categ2}_{conn_var}.png")
            g2c = g2.crop(nyc_borders)
            g2c.save(image_path + "cropped2.png")
            w = 300
            wh = 300
            im1 = Image(image_path+"cropped1.png", width=w, height=wh)
            im2 = Image(image_path+"cropped2.png", width=w, height=wh)
            im1.hAlign = "CENTER"
            im2.hAlign = "CENTER"
            im2.drawOn(c, 330, 100)
            im1.drawOn(c, 170 - w / 2, 100)
        elif city == 'boston':
            borders = (370, 330, 2500, 2700)
            g1 = pil.Image.open(f"{image_path}{city}_{demog_var}_{pretty_categ1}_{conn_var}.png")
            g1c = g1.crop(borders)
            g1c.save(image_path+"cropped1.png")
            g2 = pil.Image.open(f"{image_path}{city}_{demog_var}_{pretty_categ2}_{conn_var}.png")
            g2c = g2.crop(borders)
            g2c.save(image_path + "cropped2.png")
            w = 270
            wh = 300
            im1 = Image(image_path+"cropped1.png", width=w, height=wh)
            im2 = Image(image_path+"cropped2.png", width=w, height=wh)
            im1.hAlign = "CENTER"
            im2.hAlign = "CENTER"
            im2.drawOn(c, 330, 100)
            im1.drawOn(c, 170 - w / 2, 100)
        elif city == 'chicago':
            borders = (370, 330, 2550, 2700)
            g1 = pil.Image.open(f"{image_path}{city}_{demog_var}_{pretty_categ1}_{conn_var}.png")
            g1c = g1.crop(borders)
            g1c.save(image_path+"cropped1.png")
            g2 = pil.Image.open(f"{image_path}{city}_{demog_var}_{pretty_categ2}_{conn_var}.png")
            g2c = g2.crop(borders)
            g2c.save(image_path + "cropped2.png")
            w = 270
            wh = 300
            im1 = Image(image_path+"cropped1.png", width=w, height=wh)
            im2 = Image(image_path+"cropped2.png", width=w, height=wh)
            im1.hAlign = "CENTER"
            im2.hAlign = "CENTER"
            im2.drawOn(c, 310, 100)
            im1.drawOn(c, 170 - w / 2, 100)
        elif city == 'ri':
            borders = (370, 330, 2550, 2700)
            g1 = pil.Image.open(f"{image_path}{city}_{demog_var}_{pretty_categ1}_{conn_var}.png")
            g1c = g1.crop(borders)
            g1c.save(image_path+"cropped1.png")
            g2 = pil.Image.open(f"{image_path}{city}_{demog_var}_{pretty_categ2}_{conn_var}.png")
            g2c = g2.crop(borders)
            g2c.save(image_path + "cropped2.png")
            w = 270
            wh = 300
            im1 = Image(image_path+"cropped1.png", width=w, height=wh)
            im2 = Image(image_path+"cropped2.png", width=w, height=wh)
            im1.hAlign = "CENTER"
            im2.hAlign = "CENTER"
            im2.drawOn(c, 290, 100)
            im1.drawOn(c, 160 - w / 2, 100)

        ## TEXT ##
        null = f'''<b>Null Hypothesis:</b> {pretty_categ1} and {pretty_categ2} block groups in {pretty_city} have the same {pretty_conn_var.lower()} connectivity scores. <br/><br/>
        <b>Alternative Hypothesis:</b> {pretty_categ1} and {pretty_categ2} block groups in {pretty_city} have different {pretty_conn_var.lower()} connectivity scores. <br/><br/>
        <b>Result:</b> '''

        # Result
        if pvalue/2 > 0.05:
            null += f'The two-sided p-value was {pvalue:.3e} with t-statistic {tstats:.3}. Since the p-value/2 > 0.05: <br/> <br/> <font color="#F49609"> <b> we accept the null hypothesis. </b> </font>'
        else:
            if tstats <= 0:
                null += f'The two-sided p-value was {pvalue:.3e} with t-statistic {tstats:.3}. Since the p-value/2 < 0.05, we reject the null hypothesis. Since the t-statistic < 0, we conclude that: <br/> <br/> <font color="#F49609"> <b> {pretty_categ1} block groups have lower {conn_var.lower()} connectivity scores than {pretty_categ2} block groups.</b> </font>'
            else:
                null += f'The two-sided p-value was {pvalue:.3e} with t-statistic {tstats:.3}. Since the p-value/2 <= 0.05, we reject the null hypothesis. Since the t-statistic > 0, we conclude that: <br/> <br/> <font color="#F49609"> <b> {pretty_categ1} block groups have higher {conn_var.lower()} connectivity scores than {pretty_categ2} block groups.</b> </font>'
        null += f'''<br/><br/>The two graphs below have highlighted block groups based on the demographic variables you chose. The color of the block group corresponds to its {type} connectivity score. 
        Note the difference in the maxima of the color bars (this has to do with the infrastructure inequity we've analyzed). On the left, you see majority {pretty_categ1} block groups. On the right, you see majority {pretty_categ2} block groups.'''

        text_out = Paragraph(null, style=hyp_style)
        text_out.wrap(MARGIN_WIDTH, 100)
        text_out.drawOn(c, 42, 400)

        c.save()

        packet.seek(0)
        new_pdf = PdfFileReader(packet)
        existing_pdf = PdfFileReader(open(f"{templates_path}ttest_page.pdf", "rb"))
        output = PdfFileWriter()
        page = existing_pdf.getPage(0)
        page.mergePage(new_pdf.getPage(0))
        output.addPage(page)

        # Save file
        outputStream = open(f"{custom_page_path}custom_test_page.pdf", "wb")
        output.write(outputStream)
        outputStream.close()

    elif test == "chi_squared_test":
        pvalue, tstats, sig = chi_squared_test_results(df, city, demog_var, make_ind_file=False)
        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=letter)
        graph_categories(df, city, "label", image_path)  # Connectivity
        graph_categories(df, city, demog_var, image_path)  # Demog var
        if city == 'ri':
            borders = (750, 350, 2350, 2680)
            g1 = pil.Image.open(f"{image_path}{city}_label.png")
            g1c = g1.crop(borders)
            g1c.save(image_path+"cropped1.png")
            g2 = pil.Image.open(f"{image_path}{city}_{demog_var}.png")
            g2c = g2.crop(borders)
            g2c.save(image_path + "cropped2.png")
            w = 200
            wh = 300
            im1 = Image(image_path+"cropped1.png", width=w, height=wh)
            im2 = Image(image_path+"cropped2.png", width=w, height=wh)
            im1.hAlign = "CENTER"
            im2.hAlign = "CENTER"
            im2.drawOn(c, 340, 110)
            im1.drawOn(c, 170 - w / 2, 110)
        elif city == 'boston':
            borders = (370, 330, 2500, 2700)
            g1 = pil.Image.open(f"{image_path}{city}_label.png")
            g1c = g1.crop(borders)
            g1c.save(image_path+"cropped1.png")
            g2 = pil.Image.open(f"{image_path}{city}_{demog_var}.png")
            g2c = g2.crop(borders)
            g2c.save(image_path + "cropped2.png")
            w = 270
            wh = 300
            im1 = Image(image_path+"cropped1.png", width=w, height=wh)
            im2 = Image(image_path+"cropped2.png", width=w, height=wh)
            im1.hAlign = "CENTER"
            im2.hAlign = "CENTER"
            im2.drawOn(c, 280, 100)
            im1.drawOn(c, 160 - w / 2, 100)
        elif city == 'chicago':
            borders = (370, 330, 2550, 2700)
            g1 = pil.Image.open(f"{image_path}{city}_label.png")
            g1c = g1.crop(borders)
            g1c.save(image_path+"cropped1.png")
            g2 = pil.Image.open(f"{image_path}{city}_{demog_var}.png")
            g2c = g2.crop(borders)
            g2c.save(image_path + "cropped2.png")
            w = 270
            wh = 300
            im1 = Image(image_path+"cropped1.png", width=w, height=wh)
            im2 = Image(image_path+"cropped2.png", width=w, height=wh)
            im1.hAlign = "CENTER"
            im2.hAlign = "CENTER"
            im2.drawOn(c, 300, 100)
            im1.drawOn(c, 158 - w / 2, 100)
        elif city == 'nyc':
            borders = (370, 330, 2720, 2700)
            g1 = pil.Image.open(f"{image_path}{city}_label.png")
            g1c = g1.crop(borders)
            g1c.save(image_path+"cropped1.png")
            g2 = pil.Image.open(f"{image_path}{city}_{demog_var}.png")
            g2c = g2.crop(borders)
            g2c.save(image_path + "cropped2.png")
            w = 240
            wh = 330
            im1 = Image(image_path+"cropped1.png", width=w, height=wh)
            im2 = Image(image_path+"cropped2.png", width=w, height=wh)
            im1.hAlign = "CENTER"
            im2.hAlign = "CENTER"
            im2.drawOn(c, 330, 100)
            im1.drawOn(c, 160 - w / 2, 100)

        ## TEXT ##
        null = f"""
    <b>Null Hypothesis:</b> Block group connectivity clusters and {pretty_demog_var.lower()} in {pretty_city} are independent. <br/><br/>
    <b>Alternative Hypothesis:</b> There is an association between block group connectivity clusters and {pretty_demog_var.lower()} in {pretty_city}.<br/><br/>
    <b>Result:</b>
    """
        if pvalue > 0.05:
            null += f'The p-value was {pvalue:.3e} with test statistic {tstats:.3}. Since p-value > 0.05: <br/> <br/> <font color="#F49609"> <b> we accept the null hypothesis.</b> </font>'
        else:
            null += f'The p-value was {pvalue:.3e} with test statistic {tstats:.3}. Since p-value <= 0.05: <br/> <br/> <font color="#F49609"> <b> we reject the null hypothesis.</b> </font>'
        null += f'''<br/><br/>The two graphs below show block groups in {pretty_city} grouped through K-Means clustering.
        On the left, you see the results of K-Means clustering based on connectivity scores, where each
        integer label corresponds to a cluster. On the right, you see block groups grouped by majority {pretty_demog_var.lower()}.'''

        text_out = Paragraph(null, style=hyp_style)
        text_out.wrap(MARGIN_WIDTH, 100)
        text_out.drawOn(c, 42, 435)

        c.save()

        packet.seek(0)
        new_pdf = PdfFileReader(packet)
        existing_pdf = PdfFileReader(open(f"{templates_path}csquared_page.pdf", "rb"))
        output = PdfFileWriter()
        page = existing_pdf.getPage(0)
        page.mergePage(new_pdf.getPage(0))
        output.addPage(page)

        # Save file
        outputStream = open(f"{custom_page_path}custom_test_page.pdf", "wb")
        output.write(outputStream)
        outputStream.close()


def generate_report(city=None, pretty_city=None, test=None, pretty_test=None, demog_var=None,
                    pretty_demog_var=None, categ1=None, pretty_categ_1=None, categ2=None,
                    pretty_categ_2=None, conn_var=None, pretty_conn_var=None):
    """
    Generates a custom report page.
    :param city: City name
    :param pretty_city: Pretty city name
    :param test: Test name
    :param pretty_test: Pretty test name
    :param demog_var: Demographic variable
    :param pretty_demog_var: Pretty demographic variable
    :param categ1: Category 1 variable
    :param pretty_categ_1: Pretty category 1 variable
    :param categ2: Category 2 variable
    :param pretty_categ_2: Pretty category 2 variable
    :param conn_var: Connectivity variable
    :param pretty_conn_var: Pretty connectivity variable
    """
    title_page(pretty_city, pretty_test, pretty_demog_var, pretty_categ_1, pretty_categ_2, pretty_conn_var)
    cluster_page(city)
    test_page(city, pretty_city, test, demog_var, pretty_demog_var, categ1, pretty_categ_1, categ2,
              pretty_categ_2, conn_var, pretty_conn_var)

    # The same for all
    background = open(f"{templates_path}background.pdf", 'rb')
    final_thoughts = open(f"{templates_path}final_thoughts.pdf", 'rb')

    # Customized
    cluster = open(f"{custom_page_path}custom_cluster_page.pdf", 'rb')
    titlePage = open(f"{custom_page_path}custom_title_page.pdf", 'rb')
    testPage = open(f"{custom_page_path}custom_test_page.pdf", 'rb')

    # Read the files
    page1 = PdfFileReader(titlePage)
    page2 = PdfFileReader(background)
    page2a = PdfFileReader(cluster)
    page3 = PdfFileReader(testPage)
    page4 = PdfFileReader(final_thoughts)

    report = PdfFileWriter()
    report.addPage(page1.getPage(0))
    report.addPage(page2.getPage(0))
    report.addPage(page2a.getPage(0))
    report.addPage(page3.getPage(0))
    report.addPage(page4.getPage(0))

    final_report = open(final_report_path, 'wb')
    report.write(final_report)

    # Close all files
    final_report.close()
    background.close()
    final_thoughts .close()
    titlePage.close()
    testPage.close()
    cluster.close()
    print(f"Your report has been saved to {final_report_path}.")
