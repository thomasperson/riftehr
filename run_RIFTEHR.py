import os, sys, argparse
import argparse
import pandas as pd

__author__ = "Thomas Nate Person"
__email__ = "thomas.n.person@gmail.com"
__license__ = "MIT"
__credits__ = ["Fernanda Polubriaginof", "Thomas N. Person", "Katie LaRow, ",
               "Nicholas P. Tatonetti"]


def find_matches(pt_df, ec_df):
    """Matches Paitnes and Emergecy contact information based off of first
    name, last name, phone number, zip code and combinations of all.

    Args:
        ec_df (df): Pandas Dataframe of Emergency Contact Information
        pt_df (df): Pandas Dataframe of Paitent Informationb

    Returns:
        df_cumc_patient: Pandas Dataframe of Matches

    Todo:
        Also match on split first and last name
    """

    # First find unique and subset for those
    pt_df_sub = pt_df[pt_df.groupby(['FirstName'])['MRN'].transform('nunique') == 1]
    pt_df_sub = pt_df[pt_df['FirstName'].isin(pt_df_sub['FirstName'])]

    # Then match on the unique and save to new df with label
    df_fn = pd.merge(pt_df_sub, ec_df, how='inner', left_on='FirstName', right_on='EC_FirstName')
    df_fn = df_fn[['MRN_1', 'EC_Relationship', 'MRN']]
    df_fn['matched_path'] = 'first'

    pt_df_sub = pt_df[pt_df.groupby('LastName')['MRN'].transform('nunique') == 1]
    pt_df_sub = pt_df[pt_df['LastName'].isin(pt_df_sub['LastName'])]

    df_ln = pd.merge(pt_df_sub, ec_df, how='inner', left_on='LastName', right_on='EC_LastName')
    df_ln = df_fn[['MRN_1', 'EC_Relationship', 'MRN']]
    df_ln['matched_path'] = 'last'

    pt_df_sub = pt_df[pt_df.groupby('PhoneNumber')['MRN'].transform('nunique') == 1]
    pt_df_sub = pt_df[pt_df['PhoneNumber'].isin(pt_df_sub['PhoneNumber'])]

    df_ph = pd.merge(pt_df_sub, ec_df, how='inner', left_on='PhoneNumber', right_on='EC_PhoneNumber')
    df_ph = df_fn[['MRN_1', 'EC_Relationship', 'MRN']]
    df_ph['matched_path'] = 'phone'

    pt_df_sub = pt_df[pt_df.groupby('Zipcode')['MRN'].transform('nunique') == 1]
    pt_df_sub = pt_df[pt_df['Zipcode'].isin(pt_df_sub['Zipcode'])]

    df_zip = pd.merge(pt_df_sub, ec_df, how='inner', left_on='Zipcode', right_on='EC_Zipcode')
    df_zip = df_fn[['MRN_1', 'EC_Relationship', 'MRN']]
    df_zip['matched_path'] = 'zip'

    pt_df_sub = pt_df[pt_df.groupby(['FirstName', 'LastName'])['MRN'].transform('nunique') == 1]
    pt_df_sub = pt_df[pt_df.set_index(['FirstName', 'LastName']).index.isin(pt_df_sub.set_index(['FirstName', 'LastName']).index)]

    df_fn_ln = pd.merge(pt_df_sub, ec_df, how='inner', left_on=['FirstName', 'LastName'], right_on=['EC_FirstName', 'EC_LastName'])
    df_fn_ln = df_fn[['MRN_1', 'EC_Relationship', 'MRN']]
    df_fn_ln['matched_path'] = 'first,last'

    pt_df_sub = pt_df[pt_df.groupby(['FirstName', 'PhoneNumber'])['MRN'].transform('nunique') == 1]
    pt_df_sub = pt_df[pt_df.set_index(['FirstName', 'PhoneNumber']).index.isin(pt_df_sub.set_index(['FirstName', 'PhoneNumber']).index)]

    df_fn_ph = pd.merge(pt_df_sub, ec_df, how='inner', left_on=['FirstName', 'PhoneNumber'], right_on=['EC_FirstName', 'EC_PhoneNumber'])
    df_fn_ph = df_fn[['MRN_1', 'EC_Relationship', 'MRN']]
    df_fn_ph['matched_path'] = 'first,phone'

    pt_df_sub = pt_df[pt_df.groupby(['FirstName', 'Zipcode'])['MRN'].transform('nunique') == 1]
    pt_df_sub = pt_df[pt_df.set_index(['FirstName', 'Zipcode']).index.isin(pt_df_sub.set_index(['FirstName', 'Zipcode']).index)]

    df_fn_zip = pd.merge(pt_df_sub, ec_df, how='inner', left_on=['FirstName', 'Zipcode'], right_on=['EC_FirstName', 'EC_Zipcode'])
    df_fn_zip = df_fn[['MRN_1', 'EC_Relationship', 'MRN']]
    df_fn_zip['matched_path'] = 'first,zip'

    pt_df_sub = pt_df[pt_df.groupby(['LastName', 'PhoneNumber'])['MRN'].transform('nunique') == 1]
    pt_df_sub = pt_df[pt_df.set_index(['LastName', 'PhoneNumber']).index.isin(pt_df_sub.set_index(['LastName', 'PhoneNumber']).index)]

    df_ln_ph = pd.merge(pt_df_sub, ec_df, how='inner', left_on=['LastName', 'PhoneNumber'], right_on=['EC_LastName', 'EC_PhoneNumber'])
    df_ln_ph = df_fn[['MRN_1', 'EC_Relationship', 'MRN']]
    df_ln_ph['matched_path'] = 'last,phone'

    pt_df_sub = pt_df[pt_df.groupby(['LastName', 'Zipcode'])['MRN'].transform('nunique') == 1]
    pt_df_sub = pt_df[pt_df.set_index(['LastName', 'Zipcode']).index.isin(pt_df_sub.set_index(['LastName', 'Zipcode']).index)]

    df_ln_zip = pd.merge(pt_df_sub, ec_df, how='inner', left_on=['LastName', 'Zipcode'], right_on=['EC_LastName', 'EC_Zipcode'])
    df_ln_zip = df_fn[['MRN_1', 'EC_Relationship', 'MRN']]
    df_ln_zip['matched_path'] = 'last,zip'

    pt_df_sub = pt_df[pt_df.groupby(['PhoneNumber', 'Zipcode'])['MRN'].transform('nunique') == 1]
    pt_df_sub = pt_df[pt_df.set_index(['PhoneNumber', 'Zipcode']).index.isin(pt_df_sub.set_index(['PhoneNumber', 'Zipcode']).index)]

    df_ph_zip = pd.merge(pt_df_sub, ec_df, how='inner', left_on=['PhoneNumber', 'Zipcode'], right_on=['EC_PhoneNumber', 'EC_Zipcode'])
    df_ph_zip = df_fn[['MRN_1', 'EC_Relationship', 'MRN']]
    df_ph_zip['matched_path'] = 'phone,zip'

    pt_df_sub = pt_df[pt_df.groupby(['FirstName', 'LastName', 'PhoneNumber'])['MRN'].transform('nunique') == 1]
    pt_df_sub = pt_df[pt_df.set_index(['FirstName', 'LastName', 'PhoneNumber']).index.isin(pt_df_sub.set_index(['FirstName', 'LastName', 'PhoneNumber']).index)]

    df_fn_ln_ph = pd.merge(pt_df_sub, ec_df, how='inner', left_on=['FirstName', 'LastName', 'PhoneNumber'], right_on=['EC_FirstName', 'EC_LastName', 'EC_PhoneNumber'])
    df_fn_ln_ph = df_fn[['MRN_1', 'EC_Relationship', 'MRN']]
    df_fn_ln_ph['matched_path'] = 'first,last,phone'

    pt_df_sub = pt_df[pt_df.groupby(['FirstName', 'LastName', 'Zipcode'])['MRN'].transform('nunique') == 1]
    pt_df_sub = pt_df[pt_df.set_index(['FirstName', 'LastName', 'Zipcode']).index.isin(pt_df_sub.set_index(['FirstName', 'LastName', 'Zipcode']).index)]

    df_fn_ln_zip = pd.merge(pt_df_sub, ec_df, how='inner', left_on=['FirstName', 'LastName', 'Zipcode'], right_on=['EC_FirstName', 'EC_LastName', 'EC_Zipcode'])
    df_fn_ln_zip = df_fn[['MRN_1', 'EC_Relationship', 'MRN']]
    df_fn_ln_zip['matched_path'] = 'fist,last,zip'

    pt_df_sub = pt_df[pt_df.groupby(['FirstName', 'PhoneNumber', 'Zipcode'])['MRN'].transform('nunique') == 1]
    pt_df_sub = pt_df[pt_df.set_index(['FirstName', 'PhoneNumber', 'Zipcode']).index.isin(pt_df_sub.set_index(['FirstName', 'PhoneNumber', 'Zipcode']).index)]

    df_fn_ph_zip = pd.merge(pt_df_sub, ec_df, how='inner', left_on=['FirstName', 'PhoneNumber', 'Zipcode'], right_on=['EC_FirstName', 'EC_PhoneNumber', 'EC_Zipcode'])
    df_fn_ph_zip = df_fn[['MRN_1', 'EC_Relationship', 'MRN']]
    df_fn_ph_zip['matched_path'] = 'first,phone,zip'

    pt_df_sub = pt_df[pt_df.groupby(['LastName', 'PhoneNumber', 'Zipcode'])['MRN'].transform('nunique') == 1]
    pt_df_sub = pt_df[pt_df.set_index(['LastName', 'PhoneNumber', 'Zipcode']).index.isin(pt_df_sub.set_index(['LastName', 'PhoneNumber', 'Zipcode']).index)]

    df_ln_ph_zip = pd.merge(pt_df_sub, ec_df, how='inner', left_on=['LastName', 'PhoneNumber', 'Zipcode'], right_on=['EC_LastName', 'EC_PhoneNumber', 'EC_Zipcode'])
    df_ln_ph_zip = df_fn[['MRN_1', 'EC_Relationship', 'MRN']]
    df_ln_ph_zip['matched_path'] = 'last,phone,zip'

    pt_df_sub = pt_df[pt_df.groupby(['FirstName', 'LastName', 'PhoneNumber', 'Zipcode'])['MRN'].transform('nunique') == 1]
    pt_df_sub = pt_df[pt_df.set_index(['FirstName', 'LastName', 'PhoneNumber', 'Zipcode']).index.isin(pt_df_sub.set_index(['FirstName', 'LastName', 'PhoneNumber', 'Zipcode']).index)]

    df_fn_ln_ph_zip = pd.merge(pt_df_sub, ec_df, how='inner', left_on=['FirstName', 'LastName', 'PhoneNumber', 'Zipcode'], right_on=['EC_FirstName', 'EC_LastName', 'EC_PhoneNumber', 'EC_Zipcode'])
    df_fn_ln_ph_zip = df_fn[['MRN_1', 'EC_Relationship', 'MRN']]
    df_fn_ln_ph_zip['matched_path'] = 'first,last,phone,zip'

    # Merge all DF to new, rename column headers, and reindex
    df_cumc_patient = pd.concat([df_fn, df_ln, df_ph, df_zip, df_fn_ln, df_fn_ph, df_fn_zip, df_ln_ph, df_ln_zip, df_ph_zip, df_fn_ln_ph, df_fn_ln_zip, df_fn_ph_zip,  df_ln_ph_zip, df_fn_ln_ph_zip], ignore_index=True)
    df_cumc_patient.columns = ['empi_or_mrn', 'relationship', 'relation_empi_or_mrn', 'matched_path']

    return df_cumc_patient.drop_duplicates()


def clean_split_names(a_str):
    """Cleans and splits names for matching

    Args:
        s_str (str): String to be split

    Returns:
        list: List containing seperate words from provided spring

    Todo:
        split on space for matching of all portions of hyphenaded names and
        update find_matches() to match on all portions of split names
    """
    return a_str.strip().lower().replace("-", " ")  # .split(" ")  TODO


def normalize_phone_num(a_str):
    """Normalizes Phone Number

    Args:
        s_str (str): String to be Normalizes

    Returns:
        str: Normalized Phone number

    Todo:
        Valadate correct number of digits
    """
    return a_str.strip().lower().replace("-", "").replace("(", "").replace(")", "")


def normalize_load(pt_file, ec_file):
    """Normalizes names from the Emergency Contact and Paitent data and loads
    it into pandas data frame.

    Args:
        pt_file (str): Location of the tab seperated Paitent data file
        ec_file (str): Location of the tab seperated Emergency Contact file

    Returns:
        list: list containing two pandas dataframes of cleaned data

    Todo:
        Validate PhoneNumber, ZipCode and MRN format

    """

    pt_df = pd.read_csv(pt_file, sep='\t', dtype=str)
    ec_df = pd.read_csv(ec_file, sep='\t', dtype=str)

    pt_df['FirstName'] = pt_df['FirstName'].apply(clean_split_names)
    pt_df['LastName'] = pt_df['LastName'].apply(clean_split_names)
    ec_df['EC_FirstName'] = ec_df['EC_FirstName'].apply(clean_split_names)
    ec_df['EC_LastName'] = ec_df['EC_LastName'].apply(clean_split_names)
    ec_df['EC_PhoneNumber'] = ec_df['EC_PhoneNumber'].apply(normalize_phone_num)
    pt_df['PhoneNumber'] = pt_df['PhoneNumber'].apply(normalize_phone_num)

    return pt_df.drop_duplicates(), ec_df.drop_duplicates()


def parse_arguments():
    """Parse Command line arguments"""

    parser = argparse.ArgumentParser()

    parser.add_argument('--run_example', action='store_true', default=False,
                        dest='example',
                        help='Runs on Example Files')

    parser.add_argument('--pt_file', action='store',
                        dest='pt_file',
                        type=str,
                        help='Tab seperated file of Paitent data')

    parser.add_argument('--ec_file', action='store',
                        dest='ec_file',
                        type=str,
                        help='Tab seperated file of Emergency Contact data')

    parser.add_argument('--dg_file', action='store',
                        dest='dg_file',
                        type=str,
                        help='Tab seperated file of Paitent Demographic Data')

    parser.add_argument('--out_dir', action='store',
                        dest='out_dir',
                        type=str,
                        help='Output Directory for temp files and results')


    args = parser.parse_args()
    if args.example is False and (args.pt_file is None or args.pt_file is None
                        or args.dg_file is None or args.out_dir is None):

        print("\nNot enough input arguments provided.\n")
        parser.print_help(sys.stderr)
        sys.exit(1)

    return args


def main():
    cli_args = parse_arguments()

    if cli_args.example:
        cli_args.pt_file = "example_files" + os.sep + "pt_file.tsv"
        cli_args.ec_file = "example_files" + os.sep + "ec_file.tsv"
        cli_args.dg_file = "example_files" + os.sep + "pt_demog.tsv"
        cli_args.out_dir = "example_files"

    print(cli_args)

    # Step 1: Load and Match PT to EC
    pt_df, ec_df = normalize_load(cli_args.pt_file, cli_args.ec_file)
    df_cumc_patient = find_matches(pt_df, ec_df)
    df_cumc_patient.to_csv(cli_args.out_dir + os.sep + 'df_cumc_patient.tsv', sep='\t', index=False)

    # Step 2: Relationship Inference


if __name__ == '__main__':
    main()
    exit()
