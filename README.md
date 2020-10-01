# RIFTEHR

Relationship Inference From The EHR (RIFTEHR) is an automated algorithm for identifying relatedness between patients in an institution's Electronic Health Records.

http://riftehr.tatonettilab.org

---
Remember to always respect patient privacy.

This is a pure python 3.x implemntiaton of https://github.com/tatonetti-lab/riftehr .  Original implemention can be found under the `modules` directory along with a README for how to run them.

Three input files are required.  A tab seperated paitent file, a tab seperated fil contaiining the emergency contact data for the paitents, and a tab seperated file containing the paitent demographic data.  A fourth optional file is tab serparated Mother/Child data that will be used as TP data for some statistical and will be integrated into

Paitent file format:

| MRN | FirstName | LastName | PhoneNumber | Zipcode |
| --- | --- | --- | --- | --- |
| 1 | Stephen | Taylor | 111-111-1111 | 22182 |

Paitent emergency contact format:

| MRN_1 | EC_FirstName | EC_LastName | EC_PhoneNumber | EC_Zipcode | EC_Relationship |
| --- | --- | --- | --- | --- | --- |
| 1 | Katherine | Taylor | 222-222-2222 | 22182 | SPO |

Paitent demographic format:

| MRN | BirthYear | Sex |
| --- | --- | --- |
| 1 | 1960 | M |

Toy example files can also be found in the `example_files` directory.




Run example files with `python run_RIFTEHR.py --run_example`

Input files must be tab seperated.  Run on paitent data with the command:

 `python run_RIFTEHR.py --pt_file my_paitent_file.tsv --ec_file my_emergency_contact_file.tsv --dg_file my_pt_demographic_file.tsv ----out_dir output_directory`

 Run `python run_RIFTEHR.py -h` to view all options