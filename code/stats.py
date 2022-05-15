import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.stats import ttest_ind, chi2_contingency
from itertools import combinations
import matplotlib.pyplot as plt

# Global variables
CITIES = ["nyc", "boston", "ri", "chicago"]
DEMOG_DICT = {"majority_race": ["Black or African American alone",
                                "Native Hawaiian and Other Pacific Islander alone", "White alone",
                                "Asian alone", "American Indian and Alaska Native alone",
                                "Some other race alone", "Two or more races"],
              "majority_hispanic": ["Non Hispanic", "Hispanic"],
              "income_group": ['0:low-income', '1:lower-middle', '2:upper-middle', '3:high-income']}
CONN_VARS = ["supermarket", "bank", "library", "park", "hospital", 'school']
TEST_NAMES = ["ttest", "chi_squared_test"]
K_MEANS_DICT = {"ri": 10, "nyc": 10, "boston": 7, "chicago": 7}
LOC_DICT = {"ri": "upper right", "nyc": "upper left", "boston": "upper left", "chicago": "upper right"}

# File Paths
dhruv_full_path = "C:/Users/dhruv/Desktop/college/2022 Spring/Data Science/final_project/"
niyo_full_path = "/Users/niyoshiparekh/Downloads/csci1951a/"
herbert_full_path = '/Users/herberttraub/PycharmProjects/Data_Science/'
william_full_path = "C:/Users/wback/Documents/Coding/Data_Science/"
full_path = herbert_full_path

out_path = full_path + "bongo-bongo/data/website_backend/"

# Dataframe paths
df_paths = {"boston": 'bongo-bongo/data/hypothesis_testing_data/boston_bg_census_and_connectivity.geojson',
            "nyc": 'bongo-bongo/data/hypothesis_testing_data/nyc_bg_census_and_connectivity.geojson',
            "chicago": 'bongo-bongo/data/hypothesis_testing_data/chicago_bg_census_and_connectivity.geojson',
            "ri": 'bongo-bongo/data/hypothesis_testing_data/ri_bg_census_and_connectivity.geojson'}

alpha = 0.05

# Helper functions


# Run two sample ttest and output test statistic and pvalues
def two_sample_ttest(values_a, values_b, equal_var: bool):
    """
    Runs a two sample ttest (using scipy's built in functions).
    :param values_a: First sample of data
    :param values_b: Second sample of data
    :param equal_var: A boolean indicating whether the two datasets can be considered to have
    the same variance
    """
    tstats, pvalue = ttest_ind(values_a, values_b, equal_var=equal_var)
    return tstats, pvalue


def chisquared_independence_test(df, column_a_name: str, column_b_name: str):
    """
    Runs a chisquared independence test (using scipy's built in function),
    where both columns contain categorical data.
    :param df: Data frame to run test on
    :param column_a_name: First sample of data
    :param column_b_name: Second sample of data
    """
    cross_table = pd.crosstab(df[column_a_name], df[column_b_name])
    cross_array = np.array(cross_table)
    chi2, pvalue = chi2_contingency(cross_array)[0:2]
    return chi2, pvalue


def run_hypothesis_test(df, test_type: str, col_a: str, col_b: str, cat_a='', cat_b=''):
    """
    Combines functionality of above two functions, while also checking sample sizes to see whether
    it even makes sense to run the test.
    :param df: Data frame containing data
    :param test_type: Type of test to run
    :param col_a: First variable name (demographic)
    :param col_b: Second variable name (connectivity)
    :param cat_a: Categories under col_a
    :param cat_b: Categories under col_b
    :return:
    """
    if test_type == 'two_sample_t_ind':
        values_a = df[df[col_a] == cat_a][col_b]
        values_b = df[df[col_a] == cat_b][col_b]
        min_size = 5
        if values_a.shape[0] <= min_size or values_b.shape[0] <= min_size:
            raise ValueError("Sample too small, unable to run test")
        else:
            var_a = np.var(values_a)
            var_b = np.var(values_b)
            if min(var_a, var_b) > 0:
                var_ratio = max(var_a, var_b)/min(var_a, var_b)
            else:
                var_ratio = 0
            if var_ratio > 4:
                equal_var = False
            else:
                equal_var = True
        tstats, pvalue = two_sample_ttest(values_a, values_b, equal_var)
        return tstats, pvalue

    if test_type == 'chi_squared_ind':
        # TODO: Error check to make sure col_a and col_b are categorical
        chi2, pvalue = chisquared_independence_test(df, col_a, col_b)
        return chi2, pvalue


def graph_connectivity_in_category(df, demog_var: str, category: str,
                                   conn_var: str, save_path=out_path):
    """
    This creates a map of the city with block groups colored by the value in conn_var.
    However, only the block group is colored only if its value under demog_var is category.
    :param df: Data frame containing data
    :param demog_var: Demographic variable
    :param category: Category within demographic variable
    :param conn_var: Connectivity variable
    :param save_path: Path to save image to
    """
    plt.rcParams.update({'font.size': 32})
    fig, ax = plt.subplots(figsize=(30, 30))
    df.geometry.boundary.plot(color=None, linewidth=0.5, ax=ax, edgecolor="k")
    bgs_in_cat = df[df[demog_var] == category]
    g = bgs_in_cat.plot(conn_var + "_score", legend=True, ax=ax, aspect=1, legend_kwds={"shrink": 0.5})
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    plt.savefig(save_path)


def ttest_results(df, city_name: str, demog_var: str, category_1: str, category_2: str, conn_var: str,
                  running_out_sig=None, running_out_insig=None, make_ind_file=True):
    """
    Runs the following hypothesis test (two-sided ttest):

    Null hypothesis: there is no difference between the values of conn_var for block groups in category_1
    vs those in category_2
    Alt hypothesis: there is no difference between the values of conn_var for block groups in category_1
    vs those in category_2

    Saves a text file containing the null/alt hypothesis, the p-value, and whether we accept or reject
    the null hypothesis
    :param df: Data frame with data
    :param city_name: city to query
    :param demog_var: Demographic variable
    :param category_1: Category within demographic variable
    :param category_2: Category within demographic variable
    :param conn_var: Connectivity variable
    :param running_out_sig: Running list of significances
    :param running_out_insig: Running list of significances
    :param make_ind_file: True if you want to make a file for this test
    :return: pvalue, tstats, significance or None, None, None
    """
    text_out = f"""
    Null Hypothesis: {category_1} and {category_2} block groups in {city_name} have the same {conn_var} connectivity scores.
    Alternative Hypothesis: {category_1} and {category_2} block groups in {city_name} have different {conn_var} connectivity scores.
    """
    try:
        tstats, pvalue = run_hypothesis_test(df, 'two_sample_t_ind', demog_var, f'{conn_var}_score', category_1, category_2)
        if pvalue/2 > alpha:
            sig = False
            text_out += f'The two-sided p-value was {pvalue} with t-statistic {tstats}. Since p-value/2 > 0.05, we accept the null hypothesis.'
        else:
            sig = True
            if tstats <= 0:
                text_out += f'The two-sided p-value was {pvalue} with t-statistic {tstats}. Since p-value/2 < 0.05, we reject the null hypothesis. Since t-statistic < 0, we conclude that {category_1} block groups have lower {conn_var} connectivity scores than {category_2} block groups.'
            else:
                text_out += f'The two-sided p-value was {pvalue} with t-statistic {tstats}. Since p-value/2 <= 0.05, we reject the null hypothesis. Since t-statistic > 0, we conclude that {category_1} block groups have higher {conn_var} connectivity scores than {category_2} block groups.'

        if make_ind_file:
            if demog_var == "income_group":
                with open(out_path + f"ttest_{city_name}_{demog_var}_{category_1[2:]}_{category_2[2:]}_{conn_var}.txt", "w") as text_file:
                    text_file.write(text_out)
            else:
                with open(out_path + f"ttest_{city_name}_{demog_var}_{category_1}_{category_2}_{conn_var}.txt", "w") as text_file:
                    text_file.write(text_out)

        if running_out_sig != None and pvalue/2 <= alpha:
            running_out_sig.append(text_out)
        if running_out_insig != None and pvalue/2 > alpha:
            running_out_insig.append(text_out)
        return pvalue, tstats, sig
    except ValueError:
        text_out += "Sample too small, unable to run test"
        return None, None, None
    

def graph_categories(df, city_name: str, col_name: str, save_path=out_path):
    """
    Creates a map of the city with block groups colored according to values under col_name.
    :param df: Data frame with data
    :param city_name: City to query
    :param col_name: Column name to graph
    :param save_path: Path to save graph
    """
    if city_name == "ri" and col_name != "label":
        location = 'lower right'
    else:
        location = LOC_DICT[city_name]
    plt.rcParams.update({'font.size': 32})
    df.plot(col_name, cmap='Spectral', figsize=(30, 30), legend=True, categorical=True, linewidth=1,
            legend_kwds={'loc': location}, aspect=1)
    ax = plt.gca()
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    plt.savefig(save_path + f"{city_name}_{col_name}.png")


def chi_squared_test_results(df, city_name: str, demog_var: str, running_out_sig=None, running_out_insig=None,
                             make_ind_file=True):
    """
    Runs the following hypothesis test (chi_squared):
    Each block group belongs to one category of demog_var. Similarly, each block group also belongs to a
    connectivity cluster (done in ML -
    we will need to read this data in)

    Null hypothesis: there is no correlation between the demog_var category of a block group and the
    connectivity cluster of a block group
    Alt hypothesis: there is a correlation between the demog_var category of a block group and the
    connectivity cluster of a block group

    Save a text file containing the null/alt hypothesis, the p-value, and whether we accept or reject
    the null hypothesis
    :param df: Data frame with data
    :param city_name: City to query
    :param demog_var: Demographic variable
    :param running_out_sig: Running list of significances
    :param running_out_insig: Running list of significances
    :param make_ind_file: True if you want to make a file for this test
    :return: pvalue, tstats, significance
    """

    text_out = f"""
    Null Hypothesis: Block group connectivity clusters and {demog_var} in {city_name} are independent.
    Alternative Hypothesis: There is an association between block group connectivity clusters and {demog_var} in {city_name}.
    """
    chi2, pvalue = run_hypothesis_test(df, 'chi_squared_ind', 'label', demog_var)
    if pvalue > alpha:
        sig = False
        text_out += f'The p-value was {pvalue} with test statistic {chi2}. Since p-value > 0.05, we accept the null hypothesis.'
    else:
        sig = True
        text_out += f'The p-value was {pvalue} with test statistic {chi2}. Since p-value <= 0.05, we reject the null hypothesis.'
    
    if make_ind_file:
        with open(out_path + f"chisquared_{city_name}_{demog_var}.txt", "w") as text_file:
            text_file.write(text_out)

    if running_out_sig != None and pvalue <= alpha:
        running_out_sig.append(text_out)
    if running_out_insig != None and pvalue > alpha:
        running_out_insig.append(text_out)
    return pvalue, chi2, sig


def all_tests():
    """
    This runs every single possible hypothesis test and collectes the results into two csv files - 
    one for the chi-squared tests, one for the t-tests.
    """
    ttest_results_df = pd.DataFrame(columns=["city_name", "demog_var", "category_1", "category_2", "conn_var",
                                             "pvalue", "tstats", "sig"])
    chisquare_results_df = pd.DataFrame(columns=["city_name", "demog_var", "pvalue", "tstats", "sig"])
    for city_name in CITIES:
        df = gpd.read_file(full_path + df_paths[city_name])
        for demog_var in DEMOG_DICT:
            pvalue, tstats, sig = chi_squared_test_results(df, city_name, demog_var, make_ind_file=False)
            chisquare_results_df.loc[len(chisquare_results_df.index)] = [city_name, demog_var, pvalue, tstats,
                                                                         sig]
            for (categ_1, categ_2) in combinations(DEMOG_DICT[demog_var], 2):
                for conn_var in CONN_VARS:
                    pvalue, tstats, sig = ttest_results(df, city_name, demog_var, categ_1, categ_2, conn_var,
                                                        make_ind_file=False)
                    if pvalue != None:
                        ttest_results_df.loc[len(ttest_results_df.index)] = [city_name, demog_var, categ_1,
                                                                             categ_2, conn_var, pvalue,
                                                                             tstats, sig]

    ttest_results_df.to_csv(out_path + "ttest_results.csv")
    chisquare_results_df.to_csv(out_path + "chisquared_results.csv")


def all_graphs():
    """
    This creates all possible graphs
    """
    plt.rc('legend', **{'fontsize': 32})
    for city_name in CITIES:
        df = gpd.read_file(full_path + df_paths[city_name]).dropna()
        graph_categories(df, city_name, "label")
        for demog_var in DEMOG_DICT:
            graph_categories(df, city_name, demog_var)
            for categ in DEMOG_DICT[demog_var]:
                for conn_var in CONN_VARS:
                    graph_connectivity_in_category(df, city_name, demog_var, categ, conn_var)


if __name__ == "__main__":
    all_tests()
    # all_graphs()
