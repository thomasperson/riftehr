import os, sys
import argparse
import pandas as pd

__author__ = "Thomas Nate Person"
__email__ = "thomas.n.person@gmail.com"
__license__ = "MIT"
__credits__ = ["Fernanda Polubriaginof", "Thomas N. Person", "Katie LaRow, ",
               "Nicholas P. Tatonetti"]


def load_references():
    """Loads reference files from /reference_files into dictionary lookup
    tables for use running pipeline

    Returns:
        group_opposite: Dictionary linking various abbreviations and spellings
                        to standardized terms
        rel_abbrev_group: Distionary for flipping relationships.
    """

    group_opposite = dict()
    rel_abbrev_group = dict()

    infile = open('reference_files' + os.sep + 'relationships_lookup.tsv', 'rt')
    for line in infile:
        fields = [x.strip() for x in line.strip().split("\t")]
        group_opposite[fields[2]] = fields[3]
        rel_abbrev_group[fields[0].lower()] = fields[2]
        rel_abbrev_group[fields[1].lower()] = fields[2]
    infile.close()

    infile = open('reference_files' + os.sep + 'relationships_and_opposites.tsv', 'rt')
    for line in infile:
        fields = [x.strip() for x in line.strip().split("\t")]
        group_opposite[fields[0]] = fields[1]

    return group_opposite, rel_abbrev_group


def merge_matches_demog(df_cumc_patient, dg_df):
    """Merges demographic data with match data.

    Args:
        df_cumc_patient (df): Pandas Dataframe of Matches
        dg_df (df): Pandas Dataframe of Demographic data

    Returns:
        df_cumc_patient: Pandas Dataframe of Matches and Demographic Data

    Todo:
        Validate and Standardize Sex data.
    """


    # a.mrn, b.relationship_group, a.relation_mrn, a.matched_path, child.year as DOB_empi, parent.year as DOB_matched, child.year - parent.year as age_dif, null as exclude

    df_cumc_patient = pd.merge(df_cumc_patient, dg_df, how='inner', left_on='empi_or_mrn', right_on='MRN')
    df_cumc_patient = df_cumc_patient.drop(columns=['MRN'])
    df_cumc_patient.columns = ['empi_or_mrn', 'relationship_group', 'relation_empi_or_mrn', 'matched_path', 'DOB_empi','SEX_empi']

    df_cumc_patient = pd.merge(df_cumc_patient, dg_df, how='inner', left_on='relation_empi_or_mrn', right_on='MRN')
    df_cumc_patient = df_cumc_patient.drop(columns=['MRN'])
    df_cumc_patient.columns = ['empi_or_mrn', 'relationship_group', 'relation_empi_or_mrn', 'matched_path', 'DOB_empi','SEX_empi', 'DOB_matched', 'SEX_matched']
    df_cumc_patient['DOB_empi'] = pd.to_numeric(df_cumc_patient['DOB_empi'], downcast="float")
    df_cumc_patient['DOB_matched'] = pd.to_numeric(df_cumc_patient['DOB_matched'], downcast="float")

    # exclude anything with year of birth <1900
    df_cumc_patient = df_cumc_patient[~(df_cumc_patient['DOB_empi'] <= 1900)]
    df_cumc_patient = df_cumc_patient[~(df_cumc_patient['DOB_matched'] <= 1900)]

    df_cumc_patient['age_dif'] = df_cumc_patient['DOB_empi'] - df_cumc_patient['DOB_matched']

    return df_cumc_patient


def match_cleanup(df, group_opposite, high_match):
    """Cleans up Matches before infering relationship.  Dropping improbably
    matches and flipping probable but possible incorect relationships

    Args:
        df (df): Pandas Dataframe of Matches and Demographic data
        group_opposite: Dictionary linking Pandas Dataframe of Demographic data
        high_match: (int) Cuttoff for to filter high matches with too

    Returns:
        df: Cleaned Pandas Dataframe of Matches and Demographic Data

    Todo:
        Exclude patients with conflicting year of birth
    """

    # exclude PARENTS with age difference BETWEEN -10 AND 10 years
    indexNames = df[(df['relationship_group'] == 'Parent') & (df['age_dif'] < 10) & (df['age_dif'] > -10)].index
    df.drop(indexNames, inplace=True)

    # exclude CHILD with age difference BETWEEN -10 AND 10 years
    indexNames = df[(df['relationship_group'] == 'Child') & (df['age_dif'] < 10) & (df['age_dif'] > -10)].index
    df.drop(indexNames, inplace=True)

    # exclude GRANDPARENTS with age difference BETWEEN -20 AND 20 years
    indexNames = df[(df['relationship_group'] == 'Grandparent') & (df['age_dif'] < 20) & (df['age_dif'] > -20)].index
    df.drop(indexNames, inplace=True)

    # exclude GRANDCHILD with age difference BETWEEN -20 AND 20 years
    indexNames = df[(df['relationship_group'] == 'Grandchild') & (df['age_dif'] < 20) & (df['age_dif'] > -20)].index
    df.drop(indexNames, inplace=True)

    # flip PARENTS with age difference <-10
    df_sub_p = df[(df['relationship_group'] == 'Parent') & (df['age_dif'] < -10)]
    # flip CHILD with age difference >10
    df_sub_c = df[(df['relationship_group'] == 'Child') & (df['age_dif'] > 10)]
    # flip GRANDPARENTS with age difference <-20
    df_sub_gp = df[(df['relationship_group'] == 'Grandparent') & (df['age_dif'] < -20)]
    # flip GRANDCHILD with age difference >20
    df_sub_gc = df[(df['relationship_group'] == 'Grandchild') & (df['age_dif'] > 20)]

    # merge sub and flip and recombine
    df_sub_concat = pd.concat([df_sub_p, df_sub_c, df_sub_gp, df_sub_gc])
    df_sub_concat['relationship_group'] = df_sub_concat['relationship_group'].map(group_opposite)
    df.loc[df_sub_concat.index, :] = df_sub_concat

    # Remove High matches
    df = df[df.groupby(['relation_empi_or_mrn'])['empi_or_mrn'].transform('nunique') <= high_match]
    df = df[df.groupby(['empi_or_mrn'])['relation_empi_or_mrn'].transform('nunique') <= high_match]

    df = df[['empi_or_mrn','relationship_group','relation_empi_or_mrn']]
    df.columns = ['empi_or_mrn', 'relationship', 'relation_empi_or_mrn']

    return df.drop_duplicates()


def find_matches(pt_df, ec_df):
    """Finds uniques paitents and emergency contact matches based off of first
    name, last name, phone number, zip code combinations.  Only matches on
    atleast two fields considered.

    Args:
        ec_df (df): Pandas Dataframe of Emergency Contact Information
        pt_df (df): Pandas Dataframe of Paitent Informationb

    Returns:
        df_cumc_patient: Pandas Dataframe of Matches

    Todo:
        Also match on all pieces of split first and last name.  Just does
        full string match now
    """

    # All single matches dropped in cleanup step.  Skipping all matching on a
    # single field.

    # Unique First Name
    # pt_df_sub = pt_df[pt_df.groupby(['FirstName'])['MRN'].transform('nunique') == 1]
    # pt_df_sub = pt_df[pt_df['FirstName'].isin(pt_df_sub['FirstName'])]

    # df_fn = pd.merge(pt_df_sub, ec_df, how='inner', left_on='FirstName', right_on='EC_FirstName')
    # df_fn = df_fn[['MRN_1', 'EC_Relationship', 'MRN']]
    # df_fn['matched_path'] = 'first'

    # Unique Last Name
    # pt_df_sub = pt_df[pt_df.groupby('LastName')['MRN'].transform('nunique') == 1]
    # pt_df_sub = pt_df[pt_df['LastName'].isin(pt_df_sub['LastName'])]

    # df_ln = pd.merge(pt_df_sub, ec_df, how='inner', left_on='LastName', right_on='EC_LastName')
    # df_ln = df_ln[['MRN_1', 'EC_Relationship', 'MRN']]
    # df_ln['matched_path'] = 'last'

    # Unique Phone Number
    # pt_df_sub = pt_df[pt_df.groupby('PhoneNumber')['MRN'].transform('nunique') == 1]
    # pt_df_sub = pt_df[pt_df['PhoneNumber'].isin(pt_df_sub['PhoneNumber'])]

    # df_ph = pd.merge(pt_df_sub, ec_df, how='inner', left_on='PhoneNumber', right_on='EC_PhoneNumber')
    # df_ph = df_ph[['MRN_1', 'EC_Relationship', 'MRN']]
    # df_ph['matched_path'] = 'phone'

    # Unique Zip Code
    # pt_df_sub = pt_df[pt_df.groupby('Zipcode')['MRN'].transform('nunique') == 1]
    # pt_df_sub = pt_df[pt_df['Zipcode'].isin(pt_df_sub['Zipcode'])]

    # df_zip = pd.merge(pt_df_sub, ec_df, how='inner', left_on='Zipcode', right_on='EC_Zipcode')
    # df_zip = df_zip[['MRN_1', 'EC_Relationship', 'MRN']]
    # df_zip['matched_path'] = 'zip'

    # Unique First and Last Name
    pt_df_sub = pt_df[pt_df.groupby(['FirstName', 'LastName'])['MRN'].transform('nunique') == 1]
    pt_df_sub = pt_df[pt_df.set_index(['FirstName', 'LastName']).index.isin(pt_df_sub.set_index(['FirstName', 'LastName']).index)]

    df_fn_ln = pd.merge(pt_df_sub, ec_df, how='inner', left_on=['FirstName', 'LastName'], right_on=['EC_FirstName', 'EC_LastName'])
    df_fn_ln = df_fn_ln[['MRN_1', 'EC_Relationship', 'MRN']]
    df_fn_ln['matched_path'] = 'first,last'

    # Unique First Name and Phone Number
    pt_df_sub = pt_df[pt_df.groupby(['FirstName', 'PhoneNumber'])['MRN'].transform('nunique') == 1]
    pt_df_sub = pt_df[pt_df.set_index(['FirstName', 'PhoneNumber']).index.isin(pt_df_sub.set_index(['FirstName', 'PhoneNumber']).index)]

    df_fn_ph = pd.merge(pt_df_sub, ec_df, how='inner', left_on=['FirstName', 'PhoneNumber'], right_on=['EC_FirstName', 'EC_PhoneNumber'])
    df_fn_ph = df_fn_ph[['MRN_1', 'EC_Relationship', 'MRN']]
    df_fn_ph['matched_path'] = 'first,phone'

    # Unique First Name and Zipcode
    pt_df_sub = pt_df[pt_df.groupby(['FirstName', 'Zipcode'])['MRN'].transform('nunique') == 1]
    pt_df_sub = pt_df[pt_df.set_index(['FirstName', 'Zipcode']).index.isin(pt_df_sub.set_index(['FirstName', 'Zipcode']).index)]

    df_fn_zip = pd.merge(pt_df_sub, ec_df, how='inner', left_on=['FirstName', 'Zipcode'], right_on=['EC_FirstName', 'EC_Zipcode'])
    df_fn_zip = df_fn_zip[['MRN_1', 'EC_Relationship', 'MRN']]
    df_fn_zip['matched_path'] = 'first,zip'

    # Unique Last Name and Phone Number
    pt_df_sub = pt_df[pt_df.groupby(['LastName', 'PhoneNumber'])['MRN'].transform('nunique') == 1]
    pt_df_sub = pt_df[pt_df.set_index(['LastName', 'PhoneNumber']).index.isin(pt_df_sub.set_index(['LastName', 'PhoneNumber']).index)]

    df_ln_ph = pd.merge(pt_df_sub, ec_df, how='inner', left_on=['LastName', 'PhoneNumber'], right_on=['EC_LastName', 'EC_PhoneNumber'])
    df_ln_ph = df_ln_ph[['MRN_1', 'EC_Relationship', 'MRN']]
    df_ln_ph['matched_path'] = 'last,phone'

    # Unique Last Name and Zipcode
    pt_df_sub = pt_df[pt_df.groupby(['LastName', 'Zipcode'])['MRN'].transform('nunique') == 1]
    pt_df_sub = pt_df[pt_df.set_index(['LastName', 'Zipcode']).index.isin(pt_df_sub.set_index(['LastName', 'Zipcode']).index)]

    df_ln_zip = pd.merge(pt_df_sub, ec_df, how='inner', left_on=['LastName', 'Zipcode'], right_on=['EC_LastName', 'EC_Zipcode'])
    df_ln_zip = df_ln_zip[['MRN_1', 'EC_Relationship', 'MRN']]
    df_ln_zip['matched_path'] = 'last,zip'

    # Unique PhoneNumber and Zipcode
    pt_df_sub = pt_df[pt_df.groupby(['PhoneNumber', 'Zipcode'])['MRN'].transform('nunique') == 1]
    pt_df_sub = pt_df[pt_df.set_index(['PhoneNumber', 'Zipcode']).index.isin(pt_df_sub.set_index(['PhoneNumber', 'Zipcode']).index)]

    df_ph_zip = pd.merge(pt_df_sub, ec_df, how='inner', left_on=['PhoneNumber', 'Zipcode'], right_on=['EC_PhoneNumber', 'EC_Zipcode'])
    df_ph_zip = df_ph_zip[['MRN_1', 'EC_Relationship', 'MRN']]
    df_ph_zip['matched_path'] = 'phone,zip'

    # Unique FirstName, Last Name and PhoneNumber
    pt_df_sub = pt_df[pt_df.groupby(['FirstName', 'LastName', 'PhoneNumber'])['MRN'].transform('nunique') == 1]
    pt_df_sub = pt_df[pt_df.set_index(['FirstName', 'LastName', 'PhoneNumber']).index.isin(pt_df_sub.set_index(['FirstName', 'LastName', 'PhoneNumber']).index)]

    df_fn_ln_ph = pd.merge(pt_df_sub, ec_df, how='inner', left_on=['FirstName', 'LastName', 'PhoneNumber'], right_on=['EC_FirstName', 'EC_LastName', 'EC_PhoneNumber'])
    df_fn_ln_ph = df_fn_ln_ph[['MRN_1', 'EC_Relationship', 'MRN']]
    df_fn_ln_ph['matched_path'] = 'first,last,phone'

    # Unique FirstName, Last Name and ZipCode
    pt_df_sub = pt_df[pt_df.groupby(['FirstName', 'LastName', 'Zipcode'])['MRN'].transform('nunique') == 1]
    pt_df_sub = pt_df[pt_df.set_index(['FirstName', 'LastName', 'Zipcode']).index.isin(pt_df_sub.set_index(['FirstName', 'LastName', 'Zipcode']).index)]

    df_fn_ln_zip = pd.merge(pt_df_sub, ec_df, how='inner', left_on=['FirstName', 'LastName', 'Zipcode'], right_on=['EC_FirstName', 'EC_LastName', 'EC_Zipcode'])
    df_fn_ln_zip = df_fn_ln_zip[['MRN_1', 'EC_Relationship', 'MRN']]
    df_fn_ln_zip['matched_path'] = 'fist,last,zip'

    # Unique FirstName, PhoneNumber and ZipCode
    pt_df_sub = pt_df[pt_df.groupby(['FirstName', 'PhoneNumber', 'Zipcode'])['MRN'].transform('nunique') == 1]
    pt_df_sub = pt_df[pt_df.set_index(['FirstName', 'PhoneNumber', 'Zipcode']).index.isin(pt_df_sub.set_index(['FirstName', 'PhoneNumber', 'Zipcode']).index)]

    df_fn_ph_zip = pd.merge(pt_df_sub, ec_df, how='inner', left_on=['FirstName', 'PhoneNumber', 'Zipcode'], right_on=['EC_FirstName', 'EC_PhoneNumber', 'EC_Zipcode'])
    df_fn_ph_zip = df_fn_ph_zip[['MRN_1', 'EC_Relationship', 'MRN']]
    df_fn_ph_zip['matched_path'] = 'first,phone,zip'

    # Unique Last Name, PhoneNumber and ZipCode
    pt_df_sub = pt_df[pt_df.groupby(['LastName', 'PhoneNumber', 'Zipcode'])['MRN'].transform('nunique') == 1]
    pt_df_sub = pt_df[pt_df.set_index(['LastName', 'PhoneNumber', 'Zipcode']).index.isin(pt_df_sub.set_index(['LastName', 'PhoneNumber', 'Zipcode']).index)]

    df_ln_ph_zip = pd.merge(pt_df_sub, ec_df, how='inner', left_on=['LastName', 'PhoneNumber', 'Zipcode'], right_on=['EC_LastName', 'EC_PhoneNumber', 'EC_Zipcode'])
    df_ln_ph_zip = df_ln_ph_zip[['MRN_1', 'EC_Relationship', 'MRN']]
    df_ln_ph_zip['matched_path'] = 'last,phone,zip'

    # Unique FirstName, LastName, PhoneNumber and ZipCode
    pt_df_sub = pt_df[pt_df.groupby(['FirstName', 'LastName', 'PhoneNumber', 'Zipcode'])['MRN'].transform('nunique') == 1]
    pt_df_sub = pt_df[pt_df.set_index(['FirstName', 'LastName', 'PhoneNumber', 'Zipcode']).index.isin(pt_df_sub.set_index(['FirstName', 'LastName', 'PhoneNumber', 'Zipcode']).index)]

    df_fn_ln_ph_zip = pd.merge(pt_df_sub, ec_df, how='inner', left_on=['FirstName', 'LastName', 'PhoneNumber', 'Zipcode'], right_on=['EC_FirstName', 'EC_LastName', 'EC_PhoneNumber', 'EC_Zipcode'])
    df_fn_ln_ph_zip = df_fn_ln_ph_zip[['MRN_1', 'EC_Relationship', 'MRN']]
    df_fn_ln_ph_zip['matched_path'] = 'first,last,phone,zip'

    # Merge all DF to new, rename column headers, and reindex
    # df_cumc_patient = pd.concat([df_fn, df_ln, df_ph, df_zip, df_fn_ln, df_fn_ph, df_fn_zip, df_ln_ph, df_ln_zip, df_ph_zip, df_fn_ln_ph, df_fn_ln_zip, df_fn_ph_zip,  df_ln_ph_zip, df_fn_ln_ph_zip], ignore_index=True)
    df_cumc_patient = pd.concat([df_fn_ph, df_fn_zip, df_ln_ph, df_ln_zip, df_ph_zip, df_fn_ln_ph, df_fn_ln_zip, df_fn_ph_zip,  df_ln_ph_zip, df_fn_ln_ph_zip], ignore_index=True)
    df_cumc_patient.columns = ['empi_or_mrn', 'relationship', 'relation_empi_or_mrn', 'matched_path']

    # remove blank and self relationships
    df_cumc_patient = df_cumc_patient[df_cumc_patient.relationship != ""]
    df_cumc_patient = df_cumc_patient.loc[~(df_cumc_patient['empi_or_mrn'] == df_cumc_patient['relation_empi_or_mrn'])]

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
    return a_str.strip().lower().replace("-", "").replace("(", "").replace(")", "").replace(" ", "")


def normalize_load(pt_file, ec_file, rel_abbrev_group):
    """Normalizes names from the Emergency Contact and Paitent data and loads
    it into pandas data frame.

    Args:
        pt_file (str): Location of the tab seperated Paitent data file
        ec_file (str): Location of the tab seperated Emergency Contact file

    Returns:
        list: list containing two pandas dataframes of cleaned data

    Todo:
        Validate PhoneNumber, ZipCode and MRN format.

    """

    pt_df = pd.read_csv(pt_file, sep='\t', dtype=str)
    ec_df = pd.read_csv(ec_file, sep='\t', dtype=str)

    # Clean up PT info
    pt_df['FirstName'] = pt_df['FirstName'].apply(clean_split_names)
    pt_df['LastName'] = pt_df['LastName'].apply(clean_split_names)
    pt_df['PhoneNumber'] = pt_df['PhoneNumber'].apply(normalize_phone_num)

    # Clean up Emergency Contact
    ec_df['EC_FirstName'] = ec_df['EC_FirstName'].apply(clean_split_names)
    ec_df['EC_LastName'] = ec_df['EC_LastName'].apply(clean_split_names)
    ec_df['EC_PhoneNumber'] = ec_df['EC_PhoneNumber'].apply(normalize_phone_num)

    # Standardize relationships
    ec_df['EC_Relationship'] = ec_df['EC_Relationship'].str.lower()
    ec_df['EC_Relationship'] = ec_df['EC_Relationship'].map(rel_abbrev_group)

    # drop unknown relationship
    ec_df = ec_df.loc[ec_df["EC_Relationship"].isin(rel_abbrev_group.values())]

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

    parser.add_argument('--high_match', action='store', default=20,
                        dest='high_match',
                        type=int,
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

    group_opposite, rel_abbrev_group = load_references()

    # Step 1: Load and Match PT to EC
    pt_df, ec_df = normalize_load(cli_args.pt_file, cli_args.ec_file, rel_abbrev_group)
    df_cumc_patient = find_matches(pt_df, ec_df)
    df_cumc_patient.to_csv(cli_args.out_dir + os.sep + 'df_cumc_patient.tmp.tsv', sep='\t', index=False)

    # Step 2: Clean Matches and Relationship Inference
    dg_df = pd.read_csv(cli_args.dg_file, sep='\t', dtype=str)
    df_cumc_patient_wdg = merge_matches_demog(df_cumc_patient, dg_df)
    df_cumc_patient_wdg.to_csv(cli_args.out_dir + os.sep + 'df_cumc_patient_wdg.tmp.tsv', sep='\t', index=False)
    df_cumc_patient_wdg_clean = match_cleanup(df_cumc_patient_wdg, group_opposite, cli_args.high_match)
    df_cumc_patient_wdg_clean.to_csv(cli_args.out_dir + os.sep + 'patient_relations_w_opposites_clean.csv', sep=',', index=False)

    pass

    return


if __name__ == '__main__':
    main()
    exit()
