
tp_pt_mom_child = set()
test_imput_mom_child = set()
test_imput_child_mom = set()
test_merged = set()
test_all = set()
all_pt = set()
all_child_mom = set()
no_phone_num_pt = set()
no_ec_phone_num = set()
ec_tp_no_phone = set()
ec_tp_no_name = set()
mom_child_no_phone = set()
mom_child_no_phone = set()

infile = open('PT_FILE', 'rt')
for line in infile:
    if line.strip() == "":
        continue
    fields = line.strip().split("\t")
    all_pt.add(fields[0].strip())
    if len(fields) < 4:
        print(line)
        no_phone_num_pt.add(fields[0])
        continue
    if fields[3].strip() == "":
        no_phone_num_pt.add(fields[0])
infile.close()

infile = open('PT_MOM_CHILD', 'rt')
outfile = open('PT_MOM_CHILD_TP', 'wt')

for line in infile:
    if "mrn" in line or line.strip() == "":
        outfile.write(line)
        continue
    fields = line.strip().split("\t")
    if fields[0].strip() in all_pt and fields[1].strip() in all_pt:
        all_child_mom.add(fields[0].strip())
        all_child_mom.add(fields[1].strip())
        tp_pt_mom_child.add(tuple([fields[0].strip(), fields[1].strip()]))
        if fields[0].strip() in no_phone_num_pt:
            mom_child_no_phone.add(fields[0])
        if fields[1].strip() in no_phone_num_pt:
            mom_child_no_phone.add(fields[1])
    outfile.write(line)
outfile.close()
infile.close()

count = 0

infile = open('PT_FILE', 'rt')
outfile = open('PT_FILE_TP', 'wt')
for line in infile:
    if "mrn" in line or line.strip() == "":
        outfile.write(line)
        continue
    fields = line.strip().split("\t")
    if fields[0].strip() in all_child_mom:
        if len(fields) < 4:
            count += 1
            continue
        if fields[3].strip() == "":
            count += 1

        outfile.write(line)
infile.close()
outfile.close()
print("TP Mom/Child Links no contact phone:\t"+str(count))

print("TP Mom/Child Links:\t"+str(len(tp_pt_mom_child)))
print("TP Mom/Child Links missing phone contact Info:\t"+str(len(mom_child_no_phone)))

infile = open('EC_FILE', 'rt', encoding='utf-8', errors='ignore')
outfile = open('EC_FILE_TP', 'wt', encoding='utf-8', errors='ignore')
for line in infile:
    if "mrn" in line or line.strip() == "":
        outfile.write(line)
        continue
    fields = line.strip().split("\t")
    if fields[3].strip() == "" or fields[1].strip() == "" or fields[2].strip() == "":
        no_ec_phone_num.add(fields[0].strip())
    if fields[0].strip() in all_child_mom:
        outfile.write(line)
        if fields[3].strip() == "":
            ec_tp_no_phone.add(fields[0].strip())
            if fields[1].strip() == "" or fields[2].strip() == "":
                ec_tp_no_name.add(fields[0].strip())
infile.close()
outfile.close()

print("All EC, missing contact info:\t"+str(len(no_ec_phone_num)))
print("TP Mom/Child missing phone EC info:\t"+str(len(ec_tp_no_phone)))
print("TP Mom/Child missing name EC info:\t"+str(len(ec_tp_no_name)))

infile = open('Parent.tsv', 'rt')

for line in infile:
    if "mrn" in line or line.strip() == "":
        continue
    fields = line.strip().split("\t")
    test_imput_mom_child.add(tuple([fields[0].strip(), fields[2].strip()]))
    test_merged.add(tuple([fields[0].strip(), fields[2].strip()]))
    test_merged.add(tuple([fields[2].strip(), fields[0].strip()]))
infile.close()

infile = open('Child.tsv', 'rt')

for line in infile:
    if "mrn" in line or line.strip() == "":
        continue
    fields = line.strip().split("\t")
    test_imput_child_mom.add(tuple([fields[0], fields[2]]))
    test_merged.add(tuple([fields[0].strip(), fields[2].strip()]))
    test_merged.add(tuple([fields[2].strip(), fields[0].strip()]))
infile.close()

infile = open('df_cumc_patient.tmp.tsv', 'rt')

for line in infile:
    if "mrn" in line or line.strip() == "":
        continue
    fields = line.strip().split("\t")
    test_all.add(tuple([fields[0].strip(), fields[2].strip()]))
    test_all.add(tuple([fields[2].strip(), fields[0].strip()]))
infile.close()

tp_mom_child = tp_pt_mom_child.intersection(test_imput_mom_child)
tp_child_mom = tp_pt_mom_child.intersection(test_imput_child_mom)
tp_merged = tp_pt_mom_child.intersection(test_merged)
tp_all = tp_pt_mom_child.intersection(test_all)


print(len(tp_pt_mom_child))
print(len(test_imput_mom_child))
print(len(test_imput_child_mom))
print(len(test_merged))
print(len(test_all))

print(len(tp_mom_child))
print(len(tp_child_mom))
print(len(tp_merged))
print(len(tp_merged))
print(len(tp_all))
