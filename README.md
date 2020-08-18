# RIFTEHR

Relationship Inference From The EHR (RIFTEHR) is an automated algorithm for identifying relatedness between patients in an institution's Electronic Health Records.

http://riftehr.tatonettilab.org

---
Remember to always respect patient privacy.

Run in mysql: SET sql_mode=(SELECT REPLACE(@@sql_mode,'ONLY_FULL_GROUP_BY',''));

1.Create datafiles Step1_MatchECtoDemog/ec_file.txt and Step1_MatchECtoDemog/pt_file.txt

2. Run Step1_MatchECtoDemog/split_names_combine.py
  python path/split_names_combine.py path/ec_file.txt  path/pt_file.txt

3. Create tables and upload results from previous step to db


CREATE TABLE clinical_relationships_v3.x_ec_processed (MRN_1 VARCHAR(20),
EC_FirstName VARCHAR(20),EC_LastName VARCHAR(20),
    EC_PhoneNumber VARCHAR(12), EC_Zipcode VARCHAR(20),
    EC_Relationship VARCHAR(20));

CREATE TABLE clinical_relationships_v3.x_pt_processed (MRN VARCHAR(20),
FirstName VARCHAR(20),LastName VARCHAR(20),
    PhoneNumber VARCHAR(12), Zipcode VARCHAR(20));


4. Run find_matches.sql script

5. Create demographics table and add demo records

CREATE TABLE clinical_relationships_v3.pt_demog (mrn VARCHAR(20),  year VARCHAR(4),
    sex VARCHAR(1));

6. Run Step2_Relationship_Inference/1_exclude_EC_w_most_matches.sql

7. Run Step2_Relationship_Inference/2_clean_up_BEFORE_inferring_relationships.sql

8. Output table, patient_relations_w_opposites_clean, as patient_relations_w_opposites_clean.csv

9.  Run Step2_Relationship_Inference/3_Infer_Relationships.jl
Note: Run in same folder where patient_relations_w_opposites_clean.csv is saved

10.  Upload results from Julia script to mysql database

CREATE TABLE actual_and_inf_rel_part1 (mrn VARCHAR(20),
relationship VARCHAR(40),relation_mrn VARCHAR(20),
    infer INT(1));

11. Step2_Relationship_Inference/4_clean_up_after_inferences_part1.sql

12. Output patient_relations_w_opposites_part2 table as file as patient_relations_w_opposites_part2.csv"

13. Step2_Relationship_Inference/5_Infer_Relationships_part2.jl

14. Load results into mysql database

CREATE TABLE actual_and_inf_rel_part2 (mrn VARCHAR(20),
relationship VARCHAR(40),relation_mrn VARCHAR(20),
    infer INT(1));

15. Run Step2_Relationship_Inference/6_clean_up_after_inferences_part2.sql

16. Run Step3_AssignFamilyIDs/create_table_to_generate_family_id.sql

17.  Output all_relationships_to_generate_family_id table  as all_relationships file WITH A HEADER ROW

18.  Run /Step3_AssignFamilyIDs/All_relationships_family_ID.py
python all_relationships.csv all_family_IDS.csv

19.  Load all_family_IDS.csv into mysql table family_IDs (MRN,)

CREATE TABLE family_IDs (family_id VARCHAR(20),
individual_id VARCHAR(20));
