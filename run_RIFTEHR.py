import os, sys
import argparse
import copy
import pandas as pd
import networkx as nx
import networkx.algorithms.isomorphism as iso
import cchardet as chardet
import unidecode


__author__ = "Thomas Nate Person"
__email__ = "thomas.n.person@gmail.com"
__license__ = "MIT"
__credits__ = ["Fernanda Polubriaginof", "Thomas Nate Person", "Katie LaRow, ",
               "Nicholas P. Tatonetti"]

"""
This is a python3 implementation of the http://riftehr.tatonettilab.org/

"""


def get_family_groups(file_location, in_file_name):
    """Use graph theory packages to identify disconnected subgraphs of the
    inferred relationship. Each disconnected subgraph is called a "family."
    Each family is assigned a single identifer.

    Args:
        out_dir (str): Directory output files are saved to
        in_file_name (str): Input File name to write family assignements too

    """

    infile = open(file_location + os.sep + in_file_name, 'rt')

    all_relationships = set()

    for line in infile:
        fields = [x.strip() for x in line.strip().split("\t")]
        all_relationships.add(tuple([fields[0], fields[-1], fields[1]]))
    infile.close()

    u = nx.Graph()  # directed graph

    for r in all_relationships:
        u.add_edge(r[0], r[1], rel=r[2])

    # Components sorted by size
    comp = sorted(nx.connected_component_subgraphs(u), key=len, reverse=True)

    outfile = open(file_location + os.sep + "all_family_IDS.tsv", 'wt')

    outfile.write("family_id\tindividual_id\n")

    for family_id in range(len(comp)):
        for individual_id in comp[family_id].nodes():
            outfile.write(str(family_id)+"\t"+individual_id+"\n")
    outfile.close()

    return


def bi_directional(relation):
    """
    Flips relation for bidriectional directed relation
    Args:
        relation (str): Relationship
    Returns:
        new_relation(str): Flipped relationship or None
    """
    new_relation = None
    if relation == 'Parent':
        new_relation = 'Child'
    elif relation == 'Child':
        new_relation = 'Parent'
    elif relation == 'Sibling':
        new_relation = 'Sibling'
    elif relation == 'Cousin':
        new_relation = 'Cousin'
    elif relation == 'Grandparent':
        new_relation = 'Grandchild'
    elif relation == 'Grandchild':
        new_relation = 'Grandparent'
    elif relation == 'Great-grandparent':
        new_relation = 'Great-grandchild'
    elif relation == 'Great-grandchild':
        new_relation = 'Great-grandparent'
    elif relation == 'Aunt/Uncle':
        new_relation = 'Nephew/Niece'
    elif relation == 'Nephew/Niece':
        new_relation = 'Aunt/Uncle'
    elif relation == 'Grandaunt/Granduncle':
        new_relation = 'Grandnephew/Grandniece'
    elif relation == 'Grandnephew/Grandniece':
        new_relation = 'Grandaunt/Granduncle'

    return new_relation


def fix_sex(a_str):
    """Strips to single letter sex abbreviation

    Args:
        a_str (str): String indicating Sex

    Returns:
        n_str (str): Single Character indicating sex or None
    """
    n_str = a_str.strip().upper()[:1]

    if n_str == "F" or n_str == "M":
        return n_str
    else:
        return None


def find_encoding(fname):
    """
    Finds file encoding for loading

    Args:
        fname (str): Name of file to analyze for character encoding

    Returns:
        charenc: Detected encoding
    """
    r_file = open(fname, 'rb').read()
    result = chardet.detect(r_file)
    charenc = result['encoding']
    return charenc


def stats_and_load_other_links(file_location, of_file, mc_file, cleaned_matched_link_list, dg_dict, rel_abbrev_group, pt_df, ec_df):
    """
    Loads additonal relationship files if and calculates sensitivity
    and the positive predictive value for the infered relatons based off of
    provided mother child linkages

    Args:
        file_location (str): Output Directory of ouput files
        of_file (str): Input file of other Familial Relations
        mc_file (str): Input file of Mother/Child Links
        cleaned_matched_link_list (dict): Link List dictionary of imputed familial links
        dg_dict (dict): Dictionary of demographic data
        rel_abbrev_group (dict): Dictionary of group abbreviaton converstions
        pt_df (df): Pandas Dataframe of the PT contact data
        ec_df (df): Pandas Dataframe of emergency contact data

    Returns:
        cleaned_matched_link_list (dict): Updated link list dictionary with additonal provided data


    """

    outfile = open(file_location + os.sep + "QC_stats.tsv", 'at')

    of_link = dict()
    mc_link = dict()

    mc_link_test = dict()
    mc_imput_link_test = dict()

    if of_file is not None:
        infile = open(of_file, 'rt')
        for line in infile:
            if line.strip() == "" or "mrn" in line.lower():
                continue
            fields = [x.strip() for x in line.strip().split("\t")]
            relation = fields[-1].lower()
            if relation in rel_abbrev_group:
                relation_group = rel_abbrev_group[relation]
                of_link[tuple([fields[0], fields[1]])] = relation_group
                new_relation = bi_directional(relation_group)
                if new_relation is not None:
                    of_link[tuple([fields[1], fields[0]])] = new_relation

        infile.close()

    all_no_ec_data = set()
    all_no_pt_data = set()
    all_no_dg_data = set()

    test_missing_ec_data = set()

    mc_count = 0

    if mc_file is not None:

        infile = open(mc_file, 'rt')
        for line in infile:
            if line.strip() == "" or "mrn" in line.lower():
                continue
            fields = [x.strip() for x in line.strip().split("\t")]

            mc_count += 1

            if fields[0] not in dg_dict:
                all_no_dg_data.add(fields[0])
            if fields[-1] not in dg_dict:
                all_no_dg_data.add(fields[-1])

            if fields[0] not in pt_df['MRN'].values:
                all_no_pt_data.add(fields[0])
            if fields[-1] not in pt_df['MRN'].values:
                all_no_pt_data.add(fields[-1])

            if fields[0] not in ec_df['MRN_1'].values:
                all_no_ec_data.add(fields[0])
            if fields[-1] not in ec_df['MRN_1'].values:
                all_no_ec_data.add(fields[-1])

            # TP for mc stats, only those with good demographic or contact information
            if fields[0] in dg_dict and fields[-1] in dg_dict and fields[0] not in all_no_pt_data and fields[-1] not in all_no_pt_data:
                mc_link_test[tuple([fields[0], fields[-1]])] = "Child"
                if fields[0] in all_no_ec_data or fields[-1] in all_no_ec_data:
                    test_missing_ec_data.add(tuple([fields[0], fields[-1]]))

                # MC Test data get both directions:
                if tuple([fields[0], fields[-1]]) in cleaned_matched_link_list:
                    mc_imput_link_test[tuple([fields[0], fields[-1]])] = cleaned_matched_link_list[tuple([fields[0], fields[-1]])]
                elif tuple([fields[-1], fields[0]]) in cleaned_matched_link_list:
                    new_relation = bi_directional(cleaned_matched_link_list[tuple([fields[-1], fields[0]])])
                    mc_imput_link_test[tuple([fields[0], fields[-1]])] = new_relation

            # add both directions
            mc_link[tuple([fields[0], fields[-1]])] = "Child"
            mc_link[tuple([fields[-1], fields[0]])] = "Parent"

        infile.close()

        outfile.write("Total provided Mother/Child links:\t" + str(mc_count)+"\n")
        outfile.write("Total Number of Mother/Child IDs w/o proper contact information:\t"+ str(len(all_no_pt_data))+"\n")
        outfile.write("Total Number of Mother/Child IDs w/o proper demographic information:\t"+ str(len(all_no_dg_data))+"\n")
        outfile.write("Total Number of Mother/Child IDs w/o proper emergency contact information:\t"+ str(len(all_no_ec_data))+"\n")

        outfile.write("Number of Provided TP Mother/Child links:\t" + str(len(mc_link_test))+"\n")
        outfile.write("Number of Test Imputed Mother/Child links:\t" + str(len(mc_imput_link_test))+"\n")

        outfile.write("Number of Test TP links w/missing EC data:\t"+str(len(test_missing_ec_data))+"\n")

        MC_TP_count = 0
        MC_FP_count = 0
        MC_FN_count = 0
        # No TN_count
        MC_FN_NO_EC = 0

        for match, relation in mc_link_test.items():
            if match in mc_imput_link_test:
                if mc_imput_link_test[match] == mc_link_test[match]:
                    MC_TP_count += 1
                else:
                    MC_FP_count += 1
                    # print("match:\t"+str(match)+"\t"+str(mc_imput_link_test[match]) + "\t!=\t" + str(mc_link_test[match]))
                    # print(str(mc_imput_link_test[match]) + "\t!=\t" + str(mc_link_test[match]))
            else:
                MC_FN_count += 1
                if match in test_missing_ec_data:
                    MC_FN_NO_EC += 1

        outfile.write("MC_TP_Links_Tested\t"+str(len(mc_link_test))+"\n")
        outfile.write("MC_Links_Imputed\t"+str(len(mc_imput_link_test))+"\n")
        outfile.write("MC_TP_count\t"+str(MC_TP_count)+"\n")
        outfile.write("MC_FP_count\t"+str(MC_FP_count)+"\n")
        outfile.write("MC_FN_count\t"+str(MC_FN_count)+"\n")
        outfile.write("MC_FN_NO_EC\t"+str(MC_FN_NO_EC)+"\n")
        if MC_TP_count > 0 or MC_FN_count > 0:
            outfile.write("MC sensitivity\t" + str(MC_TP_count/(MC_TP_count+MC_FN_count)) + "\n")
            if MC_FN_NO_EC > 0:
                # can still get a match if some EC data is missing
                outfile.write("MC Reduced Denominator (Removed Missing EC) data Sensitivity\t" + str(MC_TP_count/(MC_TP_count+MC_FN_count-MC_FN_NO_EC)) + "\n")
        if MC_TP_count > 0 or MC_FP_count > 0:
            outfile.write("MC ppv\t" + str(MC_TP_count/(MC_TP_count+MC_FP_count)) + "\n\n")
    else:
        outfile.write("\nNo Mother/Child TP link data provided\n\n")
    outfile.close()

    cleaned_matched_link_list.update(of_link)
    cleaned_matched_link_list.update(mc_link)

    return cleaned_matched_link_list


def get_specific_relation(pt_id, relation, dg_dict):
    """
    Convertes general relation to specific

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
    if relation == "Sibling":
        if dg_dict[pt_id] == "F":
            specific_relation = "Sister"
        else:
            specific_relation = "Brother"
    elif relation == "Aunt/Uncle":
        if dg_dict[pt_id] == "F":
            specific_relation = "Aunt"
        else:
            specific_relation = "Uncle"
    elif relation == 'Nephew/Niece':
        if dg_dict[pt_id] == "F":
            specific_relation = "Niece"
        else:
            specific_relation = "Nephew"
    elif relation == 'Grandnephew/Grandniece':
        if dg_dict[pt_id] == "F":
            specific_relation = "Grandniece"
        else:
            specific_relation = "Grandnephew"
    elif relation == 'Grandaunt/Granduncle':
        if dg_dict[pt_id] == "F":
            specific_relation = "Grandaunt"
        else:
            specific_relation = "Granduncle"

    return specific_relation


def clean_inferences(file_location, matches_dict, out_file_name):
    """
    Cleans up infered relationships and writes the relationship linklist
        to a temp file

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
        for g in og_matches:
            if tuple([pt_id, g[1]]) in match_linked_list.keys():
                match_linked_list[tuple([pt_id, g[1]])].add(g[0])
            else:
                someSet = set()
                someSet.add(g[0])
                match_linked_list[tuple([pt_id, g[1]])] = someSet

    cleaned_matched_list = dict()

    for match, og_relations in match_linked_list.items():
        if len(og_relations) > 1:
            if 'Parent/Parent-in-law' in og_relations:
                if 'Parent' in og_relations:
                    cleaned_matched_list[match] = 'Parent'

            elif 'Parent/Aunt/Uncle' in og_relations:
                if 'Parent' in og_relations:
                    match_linked_list[match] = 'Parent'
                elif 'Aunt/Uncle' in og_relations:
                    cleaned_matched_list[match] = 'Aunt/Uncle'

            elif 'Sibling/Sibling-in-law' in og_relations:
                if 'Sibling' in og_relations:
                    cleaned_matched_list[match] = 'Sibling'

            elif 'Sibling/Cousin' in og_relations:
                if 'Sibling' in og_relations:
                    cleaned_matched_list[match] = 'Sibling'
                elif 'Cousin' in og_relations:
                    cleaned_matched_list[match] = 'Cousin'

            elif 'Child/Nephew/Niece' in og_relations:
                if 'Child' in og_relations:
                    cleaned_matched_list[match] = 'Child'
                elif 'Nephew/Niece' in og_relations:
                    cleaned_matched_list[match] = 'Nephew/Niece'

            elif 'Child/Child-in-law' in og_relations:
                if 'Child' in og_relations:
                    cleaned_matched_list[match] = 'Child'

            elif 'Nephew/Niece/Nephew-in-law/Niece-in-law' in og_relations:
                if 'Nephew/Niece' in og_relations:
                    cleaned_matched_list[match] = 'Nephew/Niece'

            elif 'Grandparent/Grandparent-in-law' in og_relations:
                if 'Grandparent' in og_relations:
                    cleaned_matched_list[match] = 'Grandparent'

            elif 'Grandchild/Grandchild-in-law' in og_relations:
                if 'Grandchild' in og_relations:
                    cleaned_matched_list[match] = 'Grandchild'

            elif 'Grandnephew/Grandniece/Grandnephew-in-law/Grandniece-in-law' in og_relations:
                if 'Grandnephew/Grandniece' in og_relations:
                    cleaned_matched_list[match] = 'Grandnephew/Grandniece'

            elif 'Grandaunt/Granduncle/Grandaunt-in-law/Granduncle-in-law' in og_relations:
                if 'Grandaunt/Granduncle' in og_relations:
                    cleaned_matched_list[match] = 'Grandaunt/Granduncle'

            elif 'Great-grandparent/Great-grandparent-in-law' in og_relations:
                if 'Great-grandparent' in og_relations:
                    cleaned_matched_list[match] = 'Great-grandparent'

            elif 'Great-grandchild/Great-grandchild-in-law' in og_relations:
                if 'Great-grandchild' in og_relations:
                    cleaned_matched_list[match] = 'Great-grandchild'
        else:
            cleaned_matched_list[match] = og_relations.pop()

    # Add bidirectional relations
    to_add = dict()
    for match, relation in cleaned_matched_list.items():
        new_relation = bi_directional(relation)
        if new_relation is not None:
            to_add[tuple([match[1], match[0]])] = new_relation

    cleaned_matched_list.update(to_add)

    outfile = open(file_location + os.sep + out_file_name, 'wt')

    for match, relation in cleaned_matched_list.items():
        outfile.write(match[0] + "\t" + relation + "\t" + match[1] + "\n")
    outfile.close()

    return cleaned_matched_list


def infer_relations(file_location, in_file_name, out_file_name):
    """
    Infers relations through already found relations.

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
        if "mrn" in line.lower():
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
    while a > 0:  # while because we loop till no more updates are found.
        a = 0  # break while variable
        for empi_key, or_emp_rel in matches_dict.items():
            emp_rel = or_emp_rel.copy()
            for match in or_emp_rel:   # looping through all the matches for empi_key
                if match[1] in matches_dict:    # if match also has other matches, get those to loop through.
                    for match_rel in matches_dict[match[1]]:    # loop through their relationships
                        if empi_key == match_rel[1]:      # we won't infer relationships from the individual to themselves
                            continue

                        if match[0] == "Parent":  # parent of match[1] is emp_rel

                            if match_rel[0] == "Sibling":  # match[1] siblings are aunt/uncle of empi_key
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
    """
    Loads reference files from /reference_files into dictionary lookup
    tables for use running pipeline

    Returns:
        group_opposite: Dictionary linking various abbreviations and spellings
                        to standardized terms
        rel_abbrev_group: Distionary for flipping relationships.
    """
    dir_path = os.path.dirname(os.path.realpath(__file__))
    group_opposite = dict()
    rel_abbrev_group = dict()

    infile = open(dir_path+os.sep+'reference_files' + os.sep + 'relationships_lookup.tsv', 'rt')
    for line in infile:
        if line.strip() == "":
            continue
        fields = [x.strip() for x in line.strip().split("\t")]
        group_opposite[fields[2]] = fields[3]
        rel_abbrev_group[fields[0].lower()] = fields[2]
        rel_abbrev_group[fields[1].lower()] = fields[2]
    infile.close()

    infile = open(dir_path+os.sep+'reference_files' + os.sep + 'relationships_and_opposites.tsv', 'rt')
    for line in infile:
        if line.strip() == "":
            continue
        fields = [x.strip() for x in line.strip().split("\t")]
        group_opposite[fields[0]] = fields[1]

    return group_opposite, rel_abbrev_group


def merge_matches_demog(df_cumc_patient, dg_df):
    """
    Merges demographic data with match data.

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
    """
    Cleans up Matches before infering relationship.  Dropping improbably
    matches and flipping probable but possible incorect relationships

    Args:
        df (df): Pandas Dataframe of Matches and Demographic data
        group_opposite: Dictionary linking Pandas Dataframe of Demographic data
        high_match: (int) Cuttoff to filter high number of matches too.

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

    # exclude Same Sex Spouses as do not contribute to heritability
    indexNames = df[(df['SEX_empi'] == df['SEX_matched']) & (df['relationship_group'] =='Spouse')].index
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

    # Swap columns into standard linked list format
    # swaps are done later.
    # df = df.reindex(columns= ['relation_empi_or_mrn', 'relationship', 'empi_or_mrn'])

    return df.drop_duplicates()


def find_matches(pt_df, ec_df):
    """
    Finds uniques patients and emergency contact matches based off of first
    name, last name, phone number, zip code combinations.  Only matches on
    atleast two fields considered.

    Args:
        ec_df (df): Pandas Dataframe of Emergency Contact Information
        pt_df (df): Pandas Dataframe of Patient Informationb

    Returns:
        df_cumc_patient: Pandas Dataframe of Matches

    Todo:
        Also match on all pieces of split first and last name.  Just does
        full string match now
    """

    # All single matches dropped in cleanup step.  Skipping all matching on a
    # single field.

    # Unique First Name
    pt_df_sub = pt_df[pt_df.groupby(['FirstName'])['MRN'].transform('nunique') == 1]
    pt_df_sub = pt_df[pt_df['FirstName'].isin(pt_df_sub['FirstName'])]

    df_fn = pd.merge(pt_df_sub, ec_df, how='inner', left_on='FirstName', right_on='EC_FirstName')
    df_fn = df_fn[['MRN_1', 'EC_Relationship', 'MRN']]
    df_fn['matched_path'] = 'first'

    # Unique Last Name
    pt_df_sub = pt_df[pt_df.groupby('LastName')['MRN'].transform('nunique') == 1]
    pt_df_sub = pt_df[pt_df['LastName'].isin(pt_df_sub['LastName'])]

    df_ln = pd.merge(pt_df_sub, ec_df, how='inner', left_on='LastName', right_on='EC_LastName')
    df_ln = df_ln[['MRN_1', 'EC_Relationship', 'MRN']]
    df_ln['matched_path'] = 'last'

    # Unique Phone Number
    pt_df_sub = pt_df[pt_df.groupby('PhoneNumber')['MRN'].transform('nunique') == 1]
    pt_df_sub = pt_df[pt_df['PhoneNumber'].isin(pt_df_sub['PhoneNumber'])]

    df_ph = pd.merge(pt_df_sub, ec_df, how='inner', left_on='PhoneNumber', right_on='EC_PhoneNumber')
    df_ph = df_ph[['MRN_1', 'EC_Relationship', 'MRN']]
    df_ph['matched_path'] = 'phone'

    # Unique Zip Code
    pt_df_sub = pt_df[pt_df.groupby('Zipcode')['MRN'].transform('nunique') == 1]
    pt_df_sub = pt_df[pt_df['Zipcode'].isin(pt_df_sub['Zipcode'])]

    df_zip = pd.merge(pt_df_sub, ec_df, how='inner', left_on='Zipcode', right_on='EC_Zipcode')
    df_zip = df_zip[['MRN_1', 'EC_Relationship', 'MRN']]
    df_zip['matched_path'] = 'zip'

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
    """
    Cleans and splits names for matching.  Unidecode coverted Unicode characters to UTF-8 ones.

    Args:
        s_str (str): String to be split

    Returns:
        n_str: (str) New cleaned and normalized string

    Todo:
        Split on space for matching of all portions of hyphenaded names and
        update find_matches() to match on all portions of split names
    """

    #unicode letters and symbols to
    n_str = unidecode.unidecode(a_str.strip())

    if n_str.strip().lower() == 'none':
        n_str=None

    return a_str.strip().lower().replace("-", " ")  # .split(" ")  TODO


def normalize_phone_num(a_str):
    """
    Normalizes Phone Number, removing any seperators and country codes.

    Args:
        a_str (str): String to be Normalizes

    Returns:
        c_str (str): Cleaned and normalized Phone number String

    """

    # Normalize
    c_str = a_str.strip().lower().replace("-", "").replace("(", "").replace(")", "").replace(" ", "").replace(".", "").replace("*", "").replace("#", "").replace("+", "").strip()

    # remove extentions
    if "," in c_str:
        c_str = c_str.split(",")[0]

    if "x" in c_str.lower():
        c_str = c_str.lower().split("x")[0]

    if "e" in c_str.lower():
        c_str = c_str.split("e")[0]

    # Drop country codes, only the last 10 digits
    if len(c_str) > 10:
        c_str=c_str[-10:]

    # empty phone number
    if c_str.strip()=="0000000000":
        return None

    # 10 minium.
    if len(c_str) < 10:
        return None

    # Only numbers in a phone number
    if not c_str.isnumeric():
        return None

    return c_str


def normalize_zip_code(a_str):
    """
    Normalizes Zip Code

    Args:
        a_str (str): A string to be Normalized

    Returns:
        c_str (str): Cleaned and normalized zip code string

    """

    # Normalize
    c_str = a_str.strip().lower().replace("-", "").replace("(", "").replace(")", "").replace(" ", "").replace(".", "").replace("*", "").replace("#", "").strip()

    # Drop 4 digit
    if len(c_str) >5:
        c_str=c_str[:5]

    # 5 minium.
    if len(c_str)<5:
        return None

    # Only numbers
    if not c_str.isnumeric():
        return None

    return c_str


def normalize_load(pt_file, ec_file, dg_file, rel_abbrev_group, file_location):
    """
    Normalizes names from the Emergency Contact and Patient data and loads
    it into pandas data frame.

    Args:
        pt_file (str): Location of the tab seperated Patient data file
        ec_file (str): Location of the tab seperated Emergency Contact file

    Returns:
        list: list containing two pandas dataframes of cleaned data

    Todo:
        Validate MRN format.

    """

    outfile = open(file_location + os.sep + "QC_stats.tsv", 'wt')

    my_encoding = find_encoding(pt_file)
    pt_df = pd.read_csv(pt_file, sep='\t', dtype=str, encoding=my_encoding)
    pt_df.columns = ['MRN', 'FirstName', 'LastName', 'PhoneNumber', 'Zipcode']
    pt_row_count = len(pt_df.index)

    # print("Raw number of records in PT_FILE:\t" + str(pt_row_count))
    outfile.write("Raw number of records in PT_FILE:\t" + str(pt_row_count)+"\n")

    my_encoding = find_encoding(ec_file)
    ec_df = pd.read_csv(ec_file, sep='\t', dtype=str, encoding=my_encoding)
    ec_df.columns = ['MRN_1', 'EC_FirstName', 'EC_LastName', 'EC_PhoneNumber', 'EC_Zipcode', 'EC_Relationship']
    ec_row_count = len(ec_df.index)

    # print("Raw number of records in EC_FILE:\t" + str(ec_row_count))
    outfile.write("Raw number of records in EC_FILE:\t" + str(ec_row_count)+"\n")

    # Drop duplicate rows
    pt_df = pt_df.drop_duplicates()
    ec_df = ec_df.drop_duplicates()

    # Drop duplicate records by MRN.
    #pt_df = pt_df.drop_duplicates(subset=['MRN'], keep=False)

    # print("Raw row duplicates dropped from PT_FILE:\t" + str(pt_row_count - len(pt_df.index)))
    # print("Raw row duplicates dropped from EC_FILE:\t" + str(ec_row_count - len(ec_df.index)))
    outfile.write("Raw row duplicates dropped from PT_FILE:\t" + str(pt_row_count - len(pt_df.index))+"\n")
    outfile.write("Raw row duplicates dropped from EC_FILE:\t" + str(ec_row_count - len(ec_df.index))+"\n")

    pt_row_count = len(pt_df.index)
    ec_row_count = len(ec_df.index)

    pt_uniq_pt_count = pt_df['MRN'].nunique()
    ec_uniq_pt_count = ec_df['MRN_1'].nunique()

    # Clean up PT info
    pt_df = pt_df.astype(str)
    pt_df['FirstName'] = pt_df['FirstName'].apply(clean_split_names)
    pt_df['LastName'] = pt_df['LastName'].apply(clean_split_names)
    pt_df['PhoneNumber'] = pt_df['PhoneNumber'].apply(normalize_phone_num)
    pt_df['Zipcode'] = pt_df['Zipcode'].apply(normalize_zip_code)

    # Clean up Emergency Contact
    ec_df = ec_df.astype(str)
    ec_df['EC_FirstName'] = ec_df['EC_FirstName'].apply(clean_split_names)
    ec_df['EC_LastName'] = ec_df['EC_LastName'].apply(clean_split_names)
    ec_df['EC_PhoneNumber'] = ec_df['EC_PhoneNumber'].apply(normalize_phone_num)
    ec_df['EC_Zipcode'] = ec_df['EC_Zipcode'].apply(normalize_zip_code)

    # Standardize relationships
    ec_df['EC_Relationship'] = ec_df['EC_Relationship'].str.lower()
    ec_df['EC_Relationship'] = ec_df['EC_Relationship'].map(rel_abbrev_group)

    # drop unknown relationship
    ec_df = ec_df.loc[ec_df["EC_Relationship"].isin(rel_abbrev_group.values())]

    pt_df = pt_df.drop_duplicates()
    ec_df = ec_df.drop_duplicates()

    # Require First, Last, Phone Number, and EC Relation not be Null
    ec_df.dropna(subset=['EC_FirstName'], inplace=True)
    ec_df.dropna(subset=['EC_PhoneNumber'], inplace=True)
    ec_df.dropna(subset=['EC_LastName'], inplace=True)
    ec_df.dropna(subset=['EC_Relationship'], inplace=True)

    # Require First, Last, Phone Number not be Null
    pt_df_hasNA = pt_df[pt_df.isna().any(axis=1)]
    pt_df.dropna(subset=['FirstName'], inplace=True)
    pt_df.dropna(subset=['LastName'], inplace=True)
    pt_df.dropna(subset=['PhoneNumber'], inplace=True)

    pt_df = pt_df.drop_duplicates()
    ec_df = ec_df.drop_duplicates()

    # pt_row_count = len(pt_df.index)
    # ec_row_count = len(ec_df.index)

    # print("Total rows dropped from PT_FILE for incomplete data:\t" + str(pt_row_count - len(pt_df.index)))
    # print("Total rows dropped from EC_FILE for incomplete data:\t" + str(ec_row_count - len(ec_df.index)))
    outfile.write("Total rows dropped from PT_FILE for incomplete data:\t" + str(pt_row_count - len(pt_df.index))+"\n")
    outfile.write("Total rows dropped from EC_FILE for incomplete data:\t" + str(ec_row_count - len(ec_df.index))+"\n")

    # pt_uniq_pt_count = pt_df['MRN'].nunique()
    # ec_uniq_pt_count = ec_df['MRN_1'].nunique()

    # print("Number of PT Record IDs dropped from analysis for incomplete data:\t"+ str(pt_uniq_pt_count - pt_df['MRN'].nunique()))
    # print("Number of EC Record IDs dropped from analysis for incomplete data:\t"+ str(ec_uniq_pt_count - ec_df['MRN_1'].nunique()))
    outfile.write("Number of PT Record IDs dropped from analysis for incomplete data:\t"+ str(pt_uniq_pt_count - pt_df['MRN'].nunique())+"\n")
    outfile.write("Number of EC Record IDs dropped from analysis for incomplete data:\t"+ str(ec_uniq_pt_count - ec_df['MRN_1'].nunique())+"\n")

    # print("Number of PT Record IDs for analysis:\t"+ str(pt_df['MRN'].nunique()))
    # print("Number of EC Record IDs for analysis:\t"+ str(ec_df['MRN_1'].nunique()))
    outfile.write("Number of PT Record IDs for analysis:\t"+ str(pt_df['MRN'].nunique())+"\n")
    outfile.write("Number of EC Record IDs for analysis:\t"+ str(ec_df['MRN_1'].nunique())+"\n")

    my_encoding = find_encoding(dg_file)
    dg_df = pd.read_csv(dg_file, sep='\t', dtype=str, encoding=my_encoding)
    dg_df.columns = ['MRN', 'BirthYear', 'Sex']

    # print("Raw number of Demographic Record rows for analysis:\t"+ str(len(dg_df.index)))
    outfile.write("Raw number of Demographic Records rows for analysis:\t"+ str(len(dg_df.index))+"\n")

    # print("Raw number of Demographic Record IDs for analysis:\t"+ str(dg_df['MRN'].nunique()))
    outfile.write("Raw number of Demographic Record IDs for analysis:\t"+ str(dg_df['MRN'].nunique())+"\n")

    dg_df = dg_df.drop_duplicates()
    dg_uniqe_ids = dg_df['MRN'].nunique()
    #outfile.write("Raw number of duplicate demographic Records dropped:\t"+ str(len(dg_df.index))+"\n")

    # Set Sex to the letters F or M and drop any non conforming
    dg_df['Sex'] = dg_df['Sex'].apply(fix_sex)
    dg_df_hasNA = dg_df[dg_df.isna().any(axis=1)]
    dg_df.dropna(subset=['Sex'], inplace=True)

    dg_df = dg_df.drop_duplicates()

    #outfile.write("PT MRNs dropped for incomplete Demographic Data:\t")
    #for v in dg_df_hasNA["MRN"]:
    #    outfile.write(str(v)+", ")
    #outfile.write("\n")

    dg_df = dg_df.drop_duplicates(subset=['MRN'], keep=False)

    outfile.write("Number of Demographic Records dropped form analysis for incomplete data:\t"+ str(dg_uniqe_ids - dg_df['MRN'].nunique())+"\n\n")

    # print("Number of demographic Record IDs for analysis:\t"+ str(dg_df['MRN'].nunique()))
    outfile.write("Number of Demographic Record IDs for analysis:\t"+ str(dg_df['MRN'].nunique())+"\n\n")

    dg_dict = dict()

    for index, row in dg_df.iterrows():
        dg_dict[row['MRN']] = tuple([row['Sex'], row['BirthYear']])

    return pt_df, ec_df, dg_df, dg_dict


def parse_arguments():
    """
    Parses Command line arguments

    Returns:
        args: argpase object of input arguemnts
    """

    parser = argparse.ArgumentParser()

    parser.add_argument('--run_example', action='store_true', default=False,
                        dest='example',
                        help='Runs on Example Files')

    parser.add_argument('--pt_file', action='store',
                        dest='pt_file',
                        type=str,
                        help='Tab seperated file of Patient data')

    parser.add_argument('--ec_file', action='store',
                        dest='ec_file',
                        type=str,
                        help='Tab seperated file of Emergency Contact data')

    parser.add_argument('--dg_file', action='store',
                        dest='dg_file',
                        type=str,
                        help='Tab seperated file of Patient Demographic Data')

    parser.add_argument('--out_dir', action='store',
                        dest='out_dir',
                        type=str,
                        help='Output Directory for temp files and results')

    parser.add_argument('--high_match', action='store', default=20,
                        dest='high_match',
                        type=int,
                        help='Maximum number of matches for a emergency contact or Patient')

    parser.add_argument('--mc_link', action='store',
                        dest='mc_link',
                        type=str,
                        help='Mother/Child link extracted from EHR records.  Used as TP for calulating accuracy of imputed data and integration into families')

    parser.add_argument('--of_link', action='store',
                        dest='of_link',
                        type=str,
                        help='Other Familial linkcages captured in the EHR for integration into families')

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
        cli_args.mc_link = "example_files" + os.sep + "mc_file.tsv"
        cli_args.of_link = "example_files" + os.sep + "of_file.tsv"
        cli_args.out_dir = "example_files"

    print(cli_args)

    print("Loading Data")
    group_opposite, rel_abbrev_group = load_references()

    # Step 1: Load and Match PT to EC
    pt_df, ec_df, dg_df, dg_dict = normalize_load(cli_args.pt_file, cli_args.ec_file, cli_args.dg_file, rel_abbrev_group, cli_args.out_dir)
    print("Finding Matches")
    df_cumc_patient = find_matches(pt_df, ec_df)
    df_cumc_patient.to_csv(cli_args.out_dir + os.sep + 'df_cumc_patient.tmp.tsv', sep='\t', index=False)

    # Step 2: Clean Matches and Relationship Inference
    print("Cleaning Matches")
    df_cumc_patient_wdg = merge_matches_demog(df_cumc_patient, dg_df)
    df_cumc_patient_wdg.to_csv(cli_args.out_dir + os.sep + 'df_cumc_patient_wdg.tmp.tsv', sep='\t', index=False)
    df_cumc_patient_wdg_clean = match_cleanup(df_cumc_patient_wdg, group_opposite, cli_args.high_match)
    df_cumc_patient_wdg_clean.to_csv(cli_args.out_dir + os.sep + 'patient_relations_w_opposites_clean.tmp.tsv', sep='\t', index=False)

    print("Infering relations")
    matches_dict = infer_relations(cli_args.out_dir, "patient_relations_w_opposites_clean.tmp.tsv","output_actual_and_inferred_relationships1.tmp.tsv")
    cleaned_matched_link_list = clean_inferences(cli_args.out_dir, matches_dict, "patient_relations_w_infered1.tmp.tsv")

    if cli_args.of_link is not None or cli_args.mc_link is not None:
        print("Calulating stats")
        cleaned_matched_link_list = stats_and_load_other_links(cli_args.out_dir, cli_args.of_link, cli_args.mc_link, cleaned_matched_link_list, dg_dict, rel_abbrev_group, pt_df, ec_df)

        outfile = open(cli_args.out_dir + os.sep + "patient_relations_w_infered_w_of_mc.tmp.tsv", 'wt')
        for match, relation in cleaned_matched_link_list.items():
            outfile.write(match[0] + "\t" + relation + "\t" + match[1] + "\n")
        outfile.close()

    print("Infering relations")
    if cli_args.of_link is None and cli_args.mc_link is None:
        matches_dict = infer_relations(cli_args.out_dir, "patient_relations_w_infered1.tmp.tsv","output_actual_and_inferred_relationships2.tmp.tsv")
    else:
        matches_dict = infer_relations(cli_args.out_dir, "patient_relations_w_infered_w_of_mc.tmp.tsv","output_actual_and_inferred_relationships2.tmp.tsv")

    cleaned_matched_link_list = clean_inferences(cli_args.out_dir, matches_dict, "final_patient_relations_w_infered.tsv")

    print("Writing Families")
    get_family_groups(cli_args.out_dir, "final_patient_relations_w_infered.tsv")


    return


if __name__ == '__main__':
    main()
    exit()
