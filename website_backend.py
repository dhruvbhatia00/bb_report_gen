import argparse
import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.stats import ttest_1samp, ttest_ind, ttest_rel, chi2_contingency
from itertools import combinations
import matplotlib.pyplot as plt
import json
import os

# global vars
CITIES = ["nyc", "boston", "ri", "chicago"]
DEMOG_DICT = {"majority_race": ["Black or African American alone", "Native Hawaiian and Other Pacific Islander alone", "White alone", "Asian alone", "American Indian and Alaska Native alone", "Some other race alone", "Two or more races"],
                "majority_hispanic": ["Non Hispanic", "Hispanic"], "income_group": ['0:low-income', '1:lower-middle', '2:upper-middle', '3:high-income']}
CONN_VARS = ["supermarket", "bank", "library", "park", "hospital", 'school']
TEST_NAMES = ["ttest", "chi_squared_test"]
K_MEANS_DICT = {"ri": 10, "nyc": 10, "boston": 7, "chicago": 7}
LOC_DICT = {"ri": "upper right", "nyc": "upper left", "boston": "upper left", "chicago": "upper right"}

#file paths
dhruv_full_path = "C:/Users/dhruv/Desktop/college/2022 Spring/Data Science/final_project/"
niyo_full_path = "/Users/niyoshiparekh/Downloads/csci1951a/"
herbert_full_path = '/Users/herberttraub/PycharmProjects/Data_Science/'
full_path = dhruv_full_path

out_path = full_path + "bongo-bongo/data/website_backend/"

# dataframe paths
df_paths = {"boston": 'bongo-bongo/data/hypothesis_testing_data/boston_bg_census_and_connectivity.geojson',
            "nyc": 'bongo-bongo/data/hypothesis_testing_data/nyc_bg_census_and_connectivity.geojson',
            "chicago": 'bongo-bongo/data/hypothesis_testing_data/chicago_bg_census_and_connectivity.geojson',
            "ri": 'bongo-bongo/data/hypothesis_testing_data/ri_bg_census_and_connectivity.geojson'}

alpha = 0.05

# helper functions
def two_sample_ttest(values_a, values_b, equal_var, relation):
    ## Stencil: Error check input - do not modify this part
    
    # TODO: Use scipy's ttest_ind
    # (https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_ind.html)
    # to get the t-statistic and the p-value
    # Note: Be sure to make the function call in a way such that the code will disregard
    # null (nan) values. Additionally, you can assume equal variance.
    tstats, pvalue = ttest_ind(values_a, values_b, equal_var=equal_var, alternative=relation)

    # TODO: You can print out the tstats, pvalue, and other necessary
    # calculations to determine your answer to the questions
    # print('test statistic: ', tstats)
    # print('p-value: ', pvalue)

    # and then we'll return tstats and pvalue
    return tstats, pvalue

def chisquared_independence_test(df, column_a_name, column_b_name):
    ## Stencil: Error check input - do not modify this part
    
    # TODO: Create a cross table between the two columns a and b
    # Hint: If you are unsure how to do this, refer to the stats lab!
    cross_table = pd.crosstab(df[column_a_name], df[column_b_name])
    cross_array = np.array(cross_table)

    # TODO: Use scipy's chi2_contingency
    # (https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.chi2_contingency.html)
    # to get the test statistic and the p-value
    tstats, pvalue = chi2_contingency(cross_array)[0:2]

    # TODO: You can print out the test statistics and pvalue to determine your answer
    # to the questions
    # print('test statistic: ', tstats)
    # print('p-value: ', pvalue)

    # and then we'll return tstats and pvalue
    return tstats, pvalue

def run_hypothesis_test(df, test_type, col_a, col_b, cat_a='', cat_b='', relation=''):
  if test_type == 'two_sample_t_ind':
    # TODO: Error check to make sure cat_a and cat_b are not empty, exist in col_a
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
        var_ratio = 0 #quick fix, should rather look at the data and filter for samples that are too small not allowing hypothesis testing
      if var_ratio > 4:
        equal_var = False
      else:
        equal_var = True
      if relation == '':
        tstats, pvalue = two_sample_ttest(values_a, values_b, equal_var, relation = 'two-sided')
        return tstats, pvalue
      elif relation == 'less' or relation == 'greater':
        tstats, pvalue = two_sample_ttest(values_a, values_b, equal_var, relation)
        return tstats, pvalue
      else:
        raise ValueError("Error in relation field")

  if test_type == 'chi_squared_ind':
    # TODO: Error check to make sure col_a and col_b are categorical
    tstats, pvalue = chisquared_independence_test(df, col_a, col_b)
    return tstats, pvalue

def graph_connectivity_in_category(df, city_name, demog_var, category, conn_var):
    # df = gpd.read_file(full_path + df_paths[city_name])
    fig, ax = plt.subplots(figsize=(30, 30))
    df.geometry.boundary.plot(color=None, linewidth=0.5, ax=ax, edgecolor="k")
    bgs_in_cat = df[df[demog_var] == category]
    bgs_in_cat.plot(conn_var + "_score", legend=True, ax=ax, legend_kwds={"shrink": 0.8, "fontsize": 32})
    # City_name = city_name[0].upper() + city_name[1:]
    # ax.set_title(f"{City_name}")
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    # ax.legend(fontsize='large')
    plt.savefig(out_path + f"{city_name}_{demog_var}_{category}_{conn_var}.png")



def ttest_results(df, city_name : str, demog_var: str, category_1: str, category_2 : str, conn_var : str, running_out_sig = None, running_out_insig = None, make_ind_file= True):
    '''this should run the following hypothesis test (two-sided ttest):
    null hypothesis: there is no difference between the values of conn_var for block groups in category_1 vs those in category_2
    alt hypothesis: there is no difference between the values of conn_var for block groups in category_1 vs those in category_2
    
    save a text file containing the null/alt hypothesis, the p-value, and whether we accept or reject the null hypothesis
    
    Then, it should create a map containing all the block groups in the city. for each block group, the map should tell us what category
    the bg was in, and also what the value of conn_var was there. Not sure what format is best for this, but we can talk that through.
    This should be saved too'''
    # df = gpd.read_file(full_path + df_paths[city_name])
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
            sig= True
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
        # print("PROBLEM")
        # print(city_name,demog_var, category_1, category_2, conn_var)
        return None, None, None
    

def graph_categories(df, city_name, col_name):
    # df = gpd.read_file(full_path + df_paths[city_name])
    # if col_name == "label":
    #     df['label'] = df['label'].astype(str)
    #     order = list(range())
    
    df.plot(col_name, cmap='Spectral', figsize=(30, 30), legend=True, categorical=True, linewidth=1, legend_kwds={'loc': LOC_DICT[city_name]})
    ax = plt.gca()
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    plt.savefig(out_path + f"{city_name}_{col_name}.png")


def chi_squared_test_results(df, city_name : str, demog_var : str, running_out_sig = None, running_out_insig = None, make_ind_file = True):
    # TODO
    '''This should run the following hypothesis test (chi_squared):
    Each block group belongs to one category of demog_var. Similarly, each block group also belongs to a connectivity cluster (done in ML - 
    we will need to read this data in)

    null hypothesis: there is no correlation between the demog_var category of a block group and the connectivity cluster of a block group
    alt hypothesis: there is a correlation between the demog_var category of a block group and the connectivity cluster of a block group

    save a text file containing the null/alt hypothesis, the p-value, and whether we accept or reject 
    the null hypothesis
    
    Then, it should create 2 maps side by side: one has bgs colored by their demog_var categories, and one has bgs colored by their connectivity 
    clusters. This should be saved too
    '''
    # df = gpd.read_file(full_path + df_paths[city_name])
    text_out = f"""
    Null Hypothesis: Block group connectivity clusters and {demog_var} in {city_name} are independent.
    Alternative Hypothesis: There is an association between block group connectivity clusters and {demog_var} in {city_name}.
    """
    tstats, pvalue = run_hypothesis_test(df, 'chi_squared_ind', 'label', demog_var)
    if pvalue > alpha:
        sig = False
        text_out += f'The p-value was {pvalue} with test statistic {tstats}. Since p-value > 0.05, we accept the null hypothesis.'
    else:
        sig = True
        text_out += f'The p-value was {pvalue} with test statistic {tstats}. Since p-value <= 0.05, we reject the null hypothesis.'
    
    if make_ind_file:
        with open(out_path + f"chisquared_{city_name}_{demog_var}.txt", "w") as text_file:
            text_file.write(text_out)

    if running_out_sig != None and pvalue <= alpha:
        running_out_sig.append(text_out)
    if running_out_insig != None and pvalue > alpha:
        running_out_insig.append(text_out)
    return pvalue, tstats, sig
    


def parse_args():
    parser = argparse.ArgumentParser(description='bongo-bongo_website_backend')
    parser.add_argument('-city', help='City name', default="")
    parser.add_argument('-demog_var', help='Demographic variable', default="")
    parser.add_argument('-categ_1', help='Category 1 of demog_var', default="")
    parser.add_argument('-categ_2', help='Category 2 of demog_var', default="")
    parser.add_argument('-conn_var', help='Connectivity variable', default="")
    parser.add_argument('-test', help='Test name', default="")
    return parser.parse_args()

def main():
    args = parse_args()
    assert args.test in TEST_NAMES

    if args.test == "ttest":
        assert args.city in CITIES
        assert args.demog_var in DEMOG_DICT
        assert args.categ_1 in DEMOG_DICT[args.demog_var]
        assert args.categ_2 in DEMOG_DICT[args.demog_var]
        assert args.conn_var in CONN_VARS
        ttest_results(args.city, args.demog_var, args.ceteg_1, args.categ_2, args.conn_var)
    elif args.test == "chi_squared_test":
        assert args.city in CITIES
        assert args.demog_var in DEMOG_DICT
        chi_squared_test_results(args.city, args.demog_var)

def main2():
    ttest_results_df = pd.DataFrame(columns=["city_name","demog_var","category_1","category_2","conn_var","pvalue","tstats","sig"])
    chisquare_results_df = pd.DataFrame(columns=["city_name","demog_var","pvalue","tstats","sig"])
    for city_name in CITIES:
        # print(city_name)
        df = gpd.read_file(full_path + df_paths[city_name])
        for demog_var in DEMOG_DICT:
            # print("    " + demog_var)
            pvalue, tstats, sig = chi_squared_test_results(df, city_name, demog_var, make_ind_file=False)
            chisquare_results_df.loc[len(chisquare_results_df.index)] = [city_name, demog_var, pvalue, tstats, sig]
            for (categ_1, categ_2) in combinations(DEMOG_DICT[demog_var], 2):
                # print("        " + categ_1 + ", " + categ_2)
                for conn_var in CONN_VARS:
                    # print("            " + conn_var)
                    pvalue, tstats, sig = ttest_results(df, city_name, demog_var, categ_1, categ_2, conn_var, make_ind_file=False)
                    if pvalue != None:
                        ttest_results_df.loc[len(ttest_results_df.index)] = [city_name, demog_var, categ_1, categ_2, conn_var, pvalue, tstats, sig]

    ttest_results_df.to_csv(out_path + "ttest_results.csv")
    chisquare_results_df.to_csv(out_path + "chisquared_results.csv")


def main3():
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
    main2()
    # main3()