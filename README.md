# RIFTEHR

Relationship Inference From The EHR (RIFTEHR) is an automated algorithm for identifying relatedness between patients in an institution's Electronic Health Records based off of  Emergency Contact information.

Remember to always respect patient privacy.

---

This is a first pass of a pure python 3.x implemntiaton of https://github.com/tatonetti-lab/riftehr originally developed by http://riftehr.tatonettilab.org.  Original implemention can also be found in this repo under the `modules` directory along with a README for how to run them.  Please submit any bugs found/fixed to this repo.  Questions/Comments/Issues concerning this implemention should be sent to Thomas Person, any Questions/Comments about the RIFTEHR algorithm itself should be directed to the Tatonetti lab.  Should you use this implementation in your research please cite: `Polubriaginof FCG, Vanguri R, Quinnies K, et al. Disease Heritability Inferred from Familial Relationships Reported in Medical Records. Cell. 2018;173(7):1692-1704.e11. doi:10.1016/j.cell.2018.04.032; PMID: 29779949`


---

## Input files:
Three tab seperated input files are required, two optional my also be used .  A tab seperated patient file(`pt_file.tsv`), a tab seperated emergency contact file (`ec_file.tsv`) for those patients, and a tab seperated file containing the patient demographic data(`pt_demog.tsv`).  A fourth optional file is tab serparated Mother/Child data (`mc_file.tsv`) that will be used as True Positive data for some statistical analysis of imputed relationships and will also be integrated into the familys.  A final fith option file (`of_file.tsv`) is a tab serperated file of other family linkages that may be captured in an EHR system.  Toy example files can also be found in the `example_files` directory. Relationship abbreviation information, relationship groups, and their oposites can be found in the `reference_files` directory.


### Patient file:

| MRN | FirstName | LastName | PhoneNumber | Zipcode |
| --- | --- | --- | --- | --- |
| 1 | Stephen | Taylor | 111-111-1111 | 22182 |

Should only be one record per MRN, any duplicates will be dropped.



### Patient emergency contact:

| MRN_1 | EC_FirstName | EC_LastName | EC_PhoneNumber | EC_Zipcode | EC_Relationship |
| --- | --- | --- | --- | --- | --- |
| 1 | Katherine | Taylor | 222-222-2222 | 22182 | SPO |

MRN_1 in the emergency contact file should corrispond to the MRN in the Patient file as the Emergency Contact information for that patient.  A single MRN can have multiple Emergency Contacts.  Any EC relationship types not found in the `reference_files` will be dropped.



### Patient demographic:

| MRN | BirthYear | Sex |
| --- | --- | --- |
| 1 | 1960 | M |

The MRN in the Patient demographic file should corrispond to the MRN in the Patient file.  Should only be one record per MRN, any duplicates will be dropped.



### Mother Child Linkage:

| MRN_Mother | MRN_Child |
| --- | --- |
| 22 | 21 |

The Mother Child Linkage is established in the delivery room and is the most accurate relationship link in an EHR system.  RIFTEHR uses this as True Positives to determine accuracy  matching of Emergency Contact Data, and integrate this information into the families that are output.



### Other Family Linkages:

| MRN_2 | MRN_3 | Relationship |
| --- | --- |  --- |
| 21 | 25 | Father |

Other self reported family relations are often captured in an EHR.  These links will also be integrated into the families generated from the Emergency Contact Information.


---
## Running RIFTEHR

Run example files with `python run_RIFTEHR.py --run_example`

Input files must be tab seperated.  Run on patient data with the command:

 `python run_RIFTEHR.py --pt_file my_patient_file.tsv --ec_file my_emergency_contact_file.tsv --dg_file my_pt_demographic_file.tsv --mc_link mc_file.tsv --out_dir output_directory`

 Run `python run_RIFTEHR.py -h` to view all options