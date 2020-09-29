import os, sys
import argparse
import copy
import pandas as pd

__author__ = "Thomas Nate Person"
__email__ = "thomas.n.person@gmail.com"
__license__ = "MIT"
__credits__ = ["Fernanda Polubriaginof", "Thomas N. Person", "Katie LaRow, ",
               "Nicholas P. Tatonetti"]


def get_specific_relation(pt_id, relation, dg_dict):
    """Convertes general relation to specific

    Args:
        pt_id (str): PT_ID to look up
        relation (str): General relation to convert
        dg_dict (dict): Dictionary of pt demographics

    Returns:
        specific_relation: Converted Specific Relation

    """
    specific_relation = ""
    if relation == "Parent":
        if dg_dict[pt_id] == "F":
            specific_relation = "Mother"
        else:
            specific_relation = "Father"
    elif relation == "Aunt/Uncle":
        if dg_dict[pt_id] == "F":
            specific_relation = "Aunt"
        else:
            specific_relation = "Uncle"
    return specific_relation


def clean_inferences(file_location, matches_dict, out_file_name):
    """Cleans up infered relationships, and writes the relatiohship linkedlist to a temp file

    Args:
        file_location (str): Location of temp files
        matches_dict (dict): Dictionary of provided and infered relationships
        out_file_name (str): Out file name

    Returns:
        cleaned_matched_list: Cleaned Dictionary Link list of actual and
                              infered relations

    """

    # Conflicting provided relationships removed at data import step

    match_linked_list = dict()

    for pt_id, og_matches in matches_dict.items():
        if tuple([pt_id, og_matches[1]]) in match_linked_list:
            match_linked_list[tuple([pt_id, og_matches[1]])].add(og_matches[0])
        else:
            someSet = set()
            someSet.add(og_matches[0])
            match_linked_list[tuple([pt_id, og_matches[1]])] = someSet

    cleaned_matched_list = dict()

    for match, og_relations in match_linked_list.items():
        if len(relations)>1:
            if 'Parent/Parent-in-law' in og_relations:
                if 'Parent' in relations:
                    cleaned_matched_list[match] = 'Parent'

            elif 'Parent/Aunt/Uncle' in og_relations:
                if 'Parent' in relations:
                    match_linked_list[match] = 'Parent'
                elif 'Aunt/Uncle' in relations:
                    cleaned_matched_list[match] = 'Aunt/Uncle'

            elif 'Sibling/Sibling-in-law' in og_relations:
                if 'Sibling' in relations:
                    cleaned_matched_list[match] = 'Sibling'

            elif 'Sibling/Cousin' in og_relations:
                if 'Sibling' in relations:
                    cleaned_matched_list[match] = 'Sibling'
                elif 'Cousin' in relations:
                    cleaned_matched_list[match] = 'Cousin'

            elif 'Child/Nephew/Niece' in og_relations:
                if 'Child' in relations:
                    cleaned_matched_list[match] = 'Child'
                elif 'Nephew/Niece' in relations:
                    cleaned_matched_list[match] = 'Nephew/Niece'

            elif 'Child/Child-in-law' in og_relations:
                if 'Child' in relations:
                    cleaned_matched_list[match] = 'Child'

            elif 'Nephew/Niece/Nephew-in-law/Niece-in-law' in og_relations:
                if 'Nephew/Niece' in relations:
                    cleaned_matched_list[match] = 'Nephew/Niece'

            elif 'Grandparent/Grandparent-in-law' in og_relations:
                if 'Grandparent' in relations:
                    cleaned_matched_list[match] = 'Grandparent'

            elif 'Grandchild/Grandchild-in-law' in og_relations:
                if 'Grandchild' in relations:
                    cleaned_matched_list[match] = 'Grandchild'

            elif 'Grandnephew/Grandniece/Grandnephew-in-law/Grandniece-in-law' in og_relations:
                if 'Grandnephew/Grandniece' in relations:
                    cleaned_matched_list[match] = 'Grandnephew/Grandniece'

            elif 'Grandaunt/Granduncle/Grandaunt-in-law/Granduncle-in-law' in og_relations:
                if 'Grandaunt/Granduncle' in relations:
                    cleaned_matched_list[match] = 'Grandaunt/Granduncle'

            elif 'Great-grandparent/Great-grandparent-in-law' in og_relations:
                if 'Great-grandparent' in relations:
                    cleaned_matched_list[match] = 'Great-grandparent'

            elif 'Great-grandchild/Great-grandchild-in-law' in og_relations:
                if 'Great-grandchild' in relations:
                    cleaned_matched_list[match] = 'Great-grandchild'
        else:
            cleaned_matched_list[match] = og_relations.pop()

    outfile = open(file_location + os.sep + out_file_name, 'wt')

    for match, relation in cleaned_matched_list.items():
        outfile.write(match[0] + "\t" + relation + "\t" + match[1] + "\n")
    outfile.close()

    return cleaned_matched_list


def infer_relations(file_location, in_file_name, out_file_name):
    """Infers relations through already found relations.

    Args:
        file_location (str): Location of temp files
        in_file_name (str): Name of input file with relations
        out_file_name (str): Name of file to output infered relations to

    Returns:
        match_dict: Dictionary containtaining actual and infered matches

    """
    matches_dict = dict()

    infile = open(file_location + os.sep + in_file_name, 'rt')
    outfile = open(file_location + os.sep + out_file_name, 'wt')

    for i, line in enumerate(infile):
        if i == 0:
            outfile.write(line)
            continue
        fields = line.strip().split("\t")
        if fields[0].strip() == fields[2].strip():
            continue
        if fields[0].strip() in matches_dict:
            matches_dict[fields[0].strip()].add(tuple([fields[1].strip(), fields[2].strip()]))
        else:
            someSet = set()
            someSet.add(tuple([fields[1].strip(), fields[2].strip()]))
            matches_dict[fields[0].strip()] = someSet
    infile.close()

    # NOTE!!  JULIA STARTS ARRAYS AT 1!!!!
    a = 1
    while a > 0:  # while because we are going to loop till no more updates are found.
        a = 0  # break while variable
        for empi_key, or_emp_rel in matches_dict.items():
            emp_rel = or_emp_rel.copy()
            # for i in keys(x) ###i is the key of the dictionary (EMPI)
            for match in or_emp_rel:   ### j are the pairs of relationships associated with the empi i
                if match[1] in matches_dict:    # tries to find the empi from the pair as key
                    for match_rel in matches_dict[match[1]]:    # z are the relationships from the empi that was found as a key
                        if empi_key == match_rel[1]:      # we won't infer relationships from the individual to themselves
                            continue


                        if match[0] == "Parent":
                            # The Siblings of a Parent are Aunts/Uncles
                            if match_rel[0] == "Sibling":
                                if tuple(["Aunt/Uncle", match_rel[1]]) not in emp_rel:
                                    emp_rel.add(tuple(["Aunt/Uncle", match_rel[1]]))
                                    a += 1
                            elif match_rel[0] == "Aunt/Uncle":
                                if tuple(["Grandaunt/Granduncle", match_rel[1]]) not in emp_rel:
                                    emp_rel.add(tuple(["Grandaunt/Granduncle", match_rel[1]]))
                                    a += 1
                            elif match_rel[0] == "Child":
                                if tuple(["Sibling", match_rel[1]]) not in emp_rel:
                                    emp_rel.add(tuple(["Sibling", match_rel[1]]))
                                    a += 1
                            elif match_rel[0] == "Grandchild":
                                if tuple(["Child/Nephew/Niece", match_rel[1]]) not in emp_rel:
                                    emp_rel.add(tuple(["Child/Nephew/Niece", match_rel[1]]))
                                    a += 1
                            elif match_rel[0] == "Grandparent":
                                if tuple(["Great-grandparent", match_rel[1]]) not in emp_rel:
                                    emp_rel.add(tuple(["Great-grandparent", match_rel[1]]))
                                    a += 1
                            elif match_rel[0] == "Nephew/Niece":
                                if tuple(["Cousin", match_rel[1]]) not in emp_rel:
                                    emp_rel.add(tuple(["Cousin", match_rel[1]]))
                                    a += 1
                            elif match_rel[0] == "Parent":
                                if tuple(["Grandparent", match_rel[1]]) not in emp_rel:
                                    emp_rel.add(tuple(["Grandparent", match_rel[1]]))
                                    a += 1

                        elif match[0] == "Child":
                            if match_rel[0] == "Sibling":
                                if tuple(["Child", match_rel[1]]) not in emp_rel:
                                    emp_rel.add(tuple(["Child", match_rel[1]]))
                                    a += 1
                            elif match_rel[0] == "Aunt/Uncle":
                                if tuple(["Sibling/Sibling-in-law", match_rel[1]]) not in emp_rel:
                                    emp_rel.add(tuple(["Sibling/Sibling-in-law", match_rel[1]]))
                                    a += 1
                            elif match_rel[0] == "Child":
                                if tuple(["Grandchild", match_rel[1]]) not in emp_rel:
                                    emp_rel.add(tuple(["Grandchild", match_rel[1]]))
                                    a += 1
                            elif match_rel[0] == "Grandchild":
                                if tuple(["Great-grandchild", match_rel[1]]) not in emp_rel:
                                    emp_rel.add(tuple(["Great-grandchild", match_rel[1]]))
                                    a += 1
                            elif match_rel[0] == "Grandparent":
                                if tuple(["Parent/Parent-in-law", match_rel[1]]) not in emp_rel:
                                    emp_rel.add(tuple(["Parent/Parent-in-law", match_rel[1]]))
                                    a += 1
                            elif match_rel[0] == "Nephew/Niece":
                                if tuple(["Grandchild/Grandchild-in-law", match_rel[1]]) not in emp_rel:
                                    emp_rel.add(tuple(["Grandchild/Grandchild-in-law", match_rel[1]]))
                                    a += 1
                            elif match_rel[0] == "Parent":
                                if tuple(["Spouse", match_rel[1]]) not in emp_rel:
                                    emp_rel.add(tuple(["Spouse", match_rel[1]]))
                                    a += 1

                        elif match[0] == "Sibling":
                            if match_rel[0] == "Sibling":
                                if tuple(["Sibling", match_rel[1]]) not in emp_rel:
                                    emp_rel.add(tuple(["Sibling", match_rel[1]]))
                                    a += 1
                            elif match_rel[0] == "Aunt/Uncle":
                                if tuple(["Aunt/Uncl", match_rel[1]]) not in emp_rel:
                                    emp_rel.add(tuple(["Aunt/Uncl", match_rel[1]]))
                                    a += 1
                            elif match_rel[0] == "Child":
                                if tuple(["Nephew/Niece", match_rel[1]]) not in emp_rel:
                                    emp_rel.add(tuple(["Nephew/Niece", match_rel[1]]))
                                    a += 1
                            elif match_rel[0] == "Grandchild":
                                if tuple(["Grandnephew/Grandniece", match_rel[1]]) not in emp_rel:
                                    emp_rel.add(tuple(["Grandnephew/Grandniece", match_rel[1]]))
                                    a += 1
                            elif match_rel[0] == "Grandparent":
                                if tuple(["Grandparent", match_rel[1]]) not in emp_rel:
                                    emp_rel.add(tuple(["Grandparent", match_rel[1]]))
                                    a += 1
                            elif match_rel[0] == "Nephew/Niece":
                                if tuple(["Child/Nephew/Niece", match_rel[1]]) not in emp_rel:
                                    emp_rel.add(tuple(["Child/Nephew/Niece", match_rel[1]]))
                                    a += 1
                            elif match_rel[0] == "Parent":
                                if tuple(["Parent", match_rel[1]]) not in emp_rel:
                                    emp_rel.add(tuple(["Parent", match_rel[1]]))
                                    a += 1

                        elif match[0] == "Aunt/Uncle":
                            if match_rel[0] == "Sibling":
                                if tuple(["Parent/Aunt/Uncle", match_rel[1]]) not in emp_rel:
                                    emp_rel.add(tuple(["Parent/Aunt/Uncle", match_rel[1]]))
                                    a += 1
                            elif match_rel[0] == "Aunt/Uncle":
                                if tuple(["Grandaunt/Granduncle/Grandaunt-in-law/Granduncle-in-law", match_rel[1]]) not in emp_rel:
                                    emp_rel.add(tuple(["Grandaunt/Granduncle/Grandaunt-in-law/Granduncle-in-law", match_rel[1]]))
                                    a += 1
                            elif match_rel[0] == "Child":
                                if tuple(["Cousin", match_rel[1]]) not in emp_rel:
                                    emp_rel.add(tuple(["Cousin", match_rel[1]]))
                                    a += 1
                            elif match_rel[0] == "Grandchild":
                                if tuple(["First cousin once removed", match_rel[1]]) not in emp_rel:
                                    emp_rel.add(tuple(["First cousin once removed", match_rel[1]]))
                                    a += 1
                            elif match_rel[0] == "Grandparent":
                                if tuple(["Great-grandparent/Great-grandparent-in-law", match_rel[1]]) not in emp_rel:
                                    emp_rel.add(tuple(["Great-grandparent/Great-grandparent-in-law", match_rel[1]]))
                                    a += 1
                            elif match_rel[0] == "Nephew/Niece":
                                if tuple(["Sibling/Cousin", match_rel[1]]) not in emp_rel:
                                    emp_rel.add(tuple(["Sibling/Cousin", match_rel[1]]))
                                    a += 1
                            elif match_rel[0] == "Parent":
                                if tuple(["Grandparent/Grandparent-in-law", match_rel[1]]) not in emp_rel:
                                    emp_rel.add(tuple(["Grandparent/Grandparent-in-law", match_rel[1]]))
                                    a += 1

                        elif match[0] == "Grandchild":
                            if match_rel[0] == "Sibling":
                                if tuple(["Grandchild", match_rel[1]]) not in emp_rel:
                                    emp_rel.add(tuple(["Grandchild", match_rel[1]]))
                                    a += 1
                            elif match_rel[0] == "Aunt/Uncle":
                                if tuple(["Child/Child-in-law", match_rel[1]]) not in emp_rel:
                                    emp_rel.add(tuple(["Child/Child-in-law", match_rel[1]]))
                                    a += 1
                            elif match_rel[0] == "Child":
                                if tuple(["Great-grandchild", match_rel[1]]) not in emp_rel:
                                    emp_rel.add(tuple(["Great-grandchild", match_rel[1]]))
                                    a += 1
                            elif match_rel[0] == "Grandchild":
                                if tuple(["Great-great-grandchild", match_rel[1]]) not in emp_rel:
                                    emp_rel.add(tuple(["Great-great-grandchild", match_rel[1]]))
                                    a += 1
                            elif match_rel[0] == "Grandparent":
                                if tuple(["Spouse", match_rel[1]]) not in emp_rel:
                                    emp_rel.add(tuple(["Spouse", match_rel[1]]))
                                    a += 1
                            elif match_rel[0] == "Nephew/Niece":
                                if tuple(["Great-grandchild/Great-grandchild-in-law", match_rel[1]]) not in emp_rel:
                                    emp_rel.add(tuple(["Great-grandchild/Great-grandchild-in-law", match_rel[1]]))
                                    a += 1
                            elif match_rel[0] == "Parent":
                                if tuple(["Child/Child-in-law", match_rel[1]]) not in emp_rel:
                                    emp_rel.add(tuple(["Child/Child-in-law", match_rel[1]]))
                                    a += 1

                        elif match[0] == "Grandparent":
                            if match_rel[0] == "Sibling":
                                if tuple(["Grandaunt/Granduncle", match_rel[1]]) not in emp_rel:
                                    emp_rel.add(tuple(["Grandaunt/Granduncle", match_rel[1]]))
                                    a += 1
                            elif match_rel[0] == "Aunt/Uncle":
                                if tuple(["Great-grandaunt/Great-granduncle", match_rel[1]]) not in emp_rel:
                                    emp_rel.add(tuple(["Great-grandaunt/Great-granduncle", match_rel[1]]))
                                    a += 1
                            elif match_rel[0] == "Child":
                                if tuple(["Parent/Aunt/Uncle", match_rel[1]]) not in emp_rel:
                                    emp_rel.add(tuple(["Parent/Aunt/Uncle", match_rel[1]]))
                                    a += 1
                            elif match_rel[0] == "Grandchild":
                                if tuple(["Sibling/Cousin", match_rel[1]]) not in emp_rel:
                                    emp_rel.add(tuple(["Sibling/Cousin", match_rel[1]]))
                                    a += 1
                            elif match_rel[0] == "Grandparent":
                                if tuple(["Great-great-grandparent", match_rel[1]]) not in emp_rel:
                                    emp_rel.add(tuple(["Great-great-grandparent", match_rel[1]]))
                                    a += 1
                            elif match_rel[0] == "Nephew/Niece":
                                if tuple(["First cousin once removed", match_rel[1]]) not in emp_rel:
                                    emp_rel.add(tuple(["First cousin once removed", match_rel[1]]))
                                    a += 1
                            elif match_rel[0] == "Parent":
                                if tuple(["Great-grandparent", match_rel[1]]) not in emp_rel:
                                    emp_rel.add(tuple(["Great-grandparent", match_rel[1]]))
                                    a += 1

                        elif match[0] == "Nephew/Niece":
                            if match_rel[0] == "Sibling":
                                if tuple(["Nephew/Niece/Nephew-in-law/Niece-in-law", match_rel[1]]) not in emp_rel:
                                    emp_rel.add(tuple(["Nephew/Niece/Nephew-in-law/Niece-in-law", match_rel[1]]))
                                    a += 1
                            elif match_rel[0] == "Aunt/Uncle":
                                if tuple(["Sibling/Sibling-in-law", match_rel[1]]) not in emp_rel:
                                    emp_rel.add(tuple(["Sibling/Sibling-in-law", match_rel[1]]))
                                    a += 1
                            elif match_rel[0] == "Child":
                                if tuple(["Grandnephew/Grandniece", match_rel[1]]) not in emp_rel:
                                    emp_rel.add(tuple(["Grandnephew/Grandniece", match_rel[1]]))
                                    a += 1
                            elif match_rel[0] == "Grandchild":
                                if tuple(["Great-grandnephew/Great-grandniece", match_rel[1]]) not in emp_rel:
                                    emp_rel.add(tuple(["Great-grandnephew/Great-grandniece", match_rel[1]]))
                                    a += 1
                            elif match_rel[0] == "Grandparent":
                                if tuple(["Parent/Parent-in-law", match_rel[1]]) not in emp_rel:
                                    emp_rel.add(tuple(["Parent/Parent-in-law", match_rel[1]]))
                                    a += 1
                            elif match_rel[0] == "Nephew/Niece":
                                if tuple(["Grandnephew/Grandniece/Grandnephew-in-law/Grandniece-in-law", match_rel[1]]) not in emp_rel:
                                    emp_rel.add(tuple(["Grandnephew/Grandniece/Grandnephew-in-law/Grandniece-in-law", match_rel[1]]))
                                    a += 1
                            elif match_rel[0] == "Parent":
                                if tuple(["Sibling/Sibling-in-law", match_rel[1]]) not in emp_rel:
                                    emp_rel.add(tuple(["Sibling/Sibling-in-law", match_rel[1]]))
                                    a += 1

            matches_dict[empi_key]=emp_rel
        if a == 0:
            break

    for ptid,match_rel in matches_dict.items():
        for x in match_rel:
            if ptid == x[-1]:
                continue
            outfile.write(ptid+"\t")
            outfile.write("\t".join(x))
            outfile.write("\n")
    outfile.close()

    return matches_dict


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
        high_match: (int) Cuttoff to filter high number of matches too

    Returns:
        df: Cleaned Pandas Dataframe of Matches and Demographic Data

    """

    # Conflicting ages dropped in import step

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

    # Drop duplicate rows
    pt_df = pt_df.drop_duplicates()
    ec_df = ec_df.drop_duplicates()

    # Drop duplicate records by MRN.
    pt_df = pt_df.drop_duplicates(subset=['MRN'], keep=False)
    ec_df = ec_df.drop_duplicates(subset=['MRN_1'], keep=False)

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
                        help='Maximum number of matches for a emergency contact or Paitent')

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
    dg_df = dg_df.drop_duplicates()
    dg_df = dg_df.drop_duplicates(subset=['MRN'], keep=False)

    dg_dict = dict()

    for index, row in dg_df:
        dg_dict[row['MRN']] = row['Sex']


    df_cumc_patient_wdg = merge_matches_demog(df_cumc_patient, dg_df)
    df_cumc_patient_wdg.to_csv(cli_args.out_dir + os.sep + 'df_cumc_patient_wdg.tmp.tsv', sep='\t', index=False)
    df_cumc_patient_wdg_clean = match_cleanup(df_cumc_patient_wdg, group_opposite, cli_args.high_match)
    df_cumc_patient_wdg_clean.to_csv(cli_args.out_dir + os.sep + 'patient_relations_w_opposites_clean.tsv', sep='\t', index=False)

    matches_dict = infer_relations(cli_args.out_dir, "patient_relations_w_opposites_clean.tsv","output_actual_and_inferred_relationships.tsv")
    clean_inferences(cli_args.out_dir, matches_dict, "patient_relations_w_infered1.tsv")

    cleaned_matched_link_list = dict()

    # Lets run it a few time.
    for i in range(2,4):
        matches_dict = infer_relations(cli_args.out_dir, "patient_relations_w_infered"+str(i-1)+".tsv","output_actual_and_inferred_relationships"+str(i)+".tsv")
        cleaned_matched_link_list = clean_inferences(cli_args.out_dir, matches_dict, "patient_relations_w_infered"+str(i)+".tsv")





    return


if __name__ == '__main__':
    main()
    exit()
