from generate_report import *

# Global variables
CITIES = {"New York City": "nyc", "Boston (Proper)": "boston", "Rhode Island": "ri", "Chicago": "chicago"}
DEMOG_DICT = {"majority_race": ["Black or African American alone",
                                "Native Hawaiian and Other Pacific Islander alone", "White alone",
                                "Asian alone", "American Indian and Alaska Native alone",
                                "Some other race alone", "Two or more races"],
              "majority_hispanic": ["Non Hispanic", "Hispanic"],
              "income_group": ['0:low-income', '1:lower-middle', '2:upper-middle', '3:high-income']}
CONN_VARS = ["Supermarket", "Bank", "Library", "Park", "Hospital", 'School']
TEST_NAMES = {"Chi-Squared Independence Test": "chi_squared_test", "Two-Tailed Independent T Test": "ttest"}
K_MEANS_DICT = {"ri": 10, "nyc": 10, "boston": 7, "chicago": 7}
LOC_DICT = {"ri": "upper left", "nyc": "upper left", "boston": "upper left", "chicago": "upper left"}
path = "/Users/herberttraub/PycharmProjects/Data_Science/"
places = {"boston": 'bongo-bongo/data/hypothesis_testing_data/boston_bg_census_and_connectivity.geojson',
            "nyc": 'bongo-bongo/data/hypothesis_testing_data/nyc_bg_census_and_connectivity.geojson',
            "chicago": 'bongo-bongo/data/hypothesis_testing_data/chicago_bg_census_and_connectivity.geojson',
            "ri": 'bongo-bongo/data/hypothesis_testing_data/ri_bg_census_and_connectivity.geojson'}


# Helper Functions
def take_input(max: int, mes: str):
    """
    Asks the user for an input, with the message mes. It checks 
    if the input is an int, and then further checks if it is within
    the specified range. If not, it keeps asking the user to try again
    until a valid input is given.
    :param max: Input int cannot be larger than max
    :param mes: Message to display
    """
    i = input(mes)
    try:
        n = int(i)
        if n in range(0, max+1):
            return n
        else:
            print(f"Please pick an integer between 0 and {max} inclusive.")
            return take_input(max, mes)
    except ValueError:
        print(f"Please pick an integer between 0 and {max} inclusive.")
        return take_input(max, mes)


def make_category_list(l: list):
    """
    Takes a list of strings, and creates a formatted string with this list (numbered).
    :param l: List to make choices list out of
    """
    lst = ""
    lst += os.linesep
    count = 0
    for category in l:
        lst += f"   {count}) {category}"
        lst += os.linesep
        count += 1

    return lst


def chosen(name):
    """
    Prints a message to the user informing them of their choice.
    :param name: Message to display
    """
    mes = f"You have chosen {name}."
    print(mes)
    print()


# Main Functions
def repl():
    """
    The main Read Evaluate Print Loop. Asks the user for various inputs, 
    after which it creates the relevant report using code from generate_report.py
    """

    city_name, pretty_city = welcome()
    test, pretty_test = test_type(pretty_city)
    demog, pretty_demog = demog_var()
    if test == "ttest":
        categ_1, pretty_categ_1, categ_2, pretty_categ_2 = categories(demog)
        conn, pretty_conn = conn_var()
        df = gpd.read_file(path + places[city_name])

        col_a = demog
        col_b = f"{conn}_score"
        cat_a = categ_1
        cat_b = categ_2
        values_a = df[df[col_a] == cat_a][col_b]
        values_b = df[df[col_a] == cat_b][col_b]
        min_size = 5
        while values_a.shape[0] <= min_size or values_b.shape[0] <= min_size:
            print("The sample size is too small for your chosen categories. Please pick again.")
            categ_1, pretty_categ_1, categ_2, pretty_categ_2 = categories(demog)
            col_a = demog
            col_b = f"{conn}_score"
            cat_a = categ_1
            cat_b = categ_2
            values_a = df[df[col_a] == cat_a][col_b]
            values_b = df[df[col_a] == cat_b][col_b]
        print("Your report is generating...")
        generate_report(city=city_name, pretty_city=pretty_city, test=test, pretty_test=pretty_test,
                        demog_var=demog, pretty_demog_var=pretty_demog, categ1=categ_1,
                        pretty_categ_1=pretty_categ_1, categ2=categ_2, pretty_categ_2=pretty_categ_2,
                        conn_var=conn, pretty_conn_var=pretty_conn)
    else:
        print("Your report is generating...")
        generate_report(city=city_name, pretty_city=pretty_city, test=test, pretty_test=pretty_test,
                        demog_var=demog, pretty_demog_var=pretty_demog)
        pass

    message = '''Thank you for using the Bongo Bongo Accessibility Report Generation Tool!'''
    print(message)
    quit_or_not()


def welcome():
    """
    Prints a welcome message explaining the tool, and then asks the user to choose a city.
    Returns the choice, along with the pretty (string formatted) version of the choice.
    :return: City chosen and its pretty version
    """
    welcome_message = f'''Welcome to the Bongo Bongo Accessibility Report Generation Tool!
Here, you will run a statistical test to analyze the relationship between the demographic 
makeup of block groups and the density of critical infrastructure within them. To start, 
please choose one of the following numbers that corresponds to the city/state you wish to analyze:
    0) {list(CITIES.keys())[0]}
    1) {list(CITIES.keys())[1]}
    2) {list(CITIES.keys())[2]}
    3) {list(CITIES.keys())[3]}'''
    print(welcome_message)
    n = take_input(3, "Your input goes here: ")
    chosen(list(CITIES.keys())[n])
    return CITIES[list(CITIES.keys())[n]], list(CITIES.keys())[n]
    

def test_type(city_name):
    """
    Prints a message explaining the types of tests available, and asks the user to choose one.
    Returns the choice, along with the pretty (string formatted) version of the choice.
    :param city_name: City from previous input
    :return: Test chosen and its pretty version
    """
    message = f'''Next, you will choose the kind of test you wish to use. {city_name} is broken into small
regions called block groups. We collected data from the US Census for each block group
to understand its demographic makeup. We also queried the Google Maps API to find the
critical infrastructure within the range of each block group. The chi-squared independence
test can tell us whether there is a statistically significant correlation between a demographic 
variable and the connectivity of block groups to infrastructure. The two-tailed independent 
T-test does something similar, but at a more granular level - it can help you analyze whether 
there is a statistically significant difference between the connectivity of block groups with 
differing demographics to a certain type of infrastructure.
    0) {list(TEST_NAMES.keys())[0]}
    1) {list(TEST_NAMES.keys())[1]}
    '''
    print(message)
    n = take_input(1, "Your input goes here: ")
    chosen(list(TEST_NAMES.keys())[n])
    return TEST_NAMES[list(TEST_NAMES.keys())[n]], list(TEST_NAMES.keys())[n]


def demog_var():
    """
    Asks the user to choose a demographic variable.
    Returns the choice, along with the pretty (string formatted) version of the choice.
    :return: Demographic chosen and its pretty version
    """
    message = f'''Please choose which demographic variable you would like to analyze.
    0) Race
    1) Ethnicity
    2) Income
    '''
    print(message)
    n = take_input(2, "Your input goes here: ")
    if n == 0:
        demog_var = "majority_race"
        chosen("Race")
        return demog_var, "Race"
    elif n == 1:
        demog_var = "majority_hispanic"
        chosen("Ethnicity")
        return demog_var, "Ethnicity"
    elif n == 2:
        demog_var = "income_group"
        chosen("Income")
        return demog_var, "Income"
    

def conn_var():
    """
    Asks the user to choose a connectivity variable.
    Returns the choice, along with the pretty (string formatted) version of the choice.
    :return: Connectivity variable chosen and its pretty version
    """

    message = f'''Please choose which connectivity variable you would like to analyze.
    0) {CONN_VARS[0]}
    1) {CONN_VARS[1]}
    2) {CONN_VARS[2]}
    3) {CONN_VARS[3]}
    4) {CONN_VARS[4]}
    5) {CONN_VARS[5]}
    '''
    print(message)
    n = take_input(5, "Your input goes here: ")
    chosen(CONN_VARS[n])
    return CONN_VARS[n].lower(), CONN_VARS[n]


def categories(demog_var):
    """
    Asks the user to choose two categories within the demographic variable they chose earlier.
    Returns the choices, along with the pretty (string formatted) versions of the choices.
    :param demog_var: Demographic variable from previous input
    :return: Categories chosen and their pretty versions
    """ 
    message = "Because you chose a T-test, you will need to choose the two categories you wish to compare."
    options = DEMOG_DICT[demog_var].copy()
    pretty_options = options.copy()
    if options == ['0:low-income', '1:lower-middle', '2:upper-middle', '3:high-income']:
        pretty_options = ["Low Income", "Lower-Middle Income", "Upper-Middle Income", "High Income"]
    message += make_category_list(pretty_options)
    print(message)
    n1 = take_input(len(options) - 1, "Your first input goes here: ")
    categ_1 = options[n1]
    pretty_categ_1 = pretty_options[n1]
    options.remove(categ_1)
    pretty_options.remove(pretty_categ_1)

    message2 = '''Please choose your second category. 
Please note the options have changed based on your previous selection.'''
    message2 += make_category_list(pretty_options)
    print(message2)
    n2 = take_input(len(options) - 1, "Your second input goes here: ")
    categ_2 = options[n2]
    pretty_categ_2 = pretty_options[n2]
    chosen(pretty_categ_1 + " and " + pretty_categ_2)

    return categ_1, pretty_categ_1, categ_2, pretty_categ_2


def quit_or_not():
    """
    Asks the user whether they would like to quit, or whether they'd like to create another report.
    If they wish to create another report, repl is called again, starting the loop over.
    """
    message = '''Would you like to make another report (y/n)?
Please note that your previous report will be overwritten. Please save it somewhere else before generating another report!
Your input goes here: '''
    i = input(message)
    if (i != "y") and (i != "n"):
        print("Your input must be 'y' or 'n'.")
        quit_or_not()
    elif i == "y":
        repl()


if __name__ == "__main__":
    """starts the loop"""
    repl()
