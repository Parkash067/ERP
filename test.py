import sys
def read_logs(file_path):
    # make sure using r'filepath' to mean its a string literal
    fl = open(file_path, 'r')
    end_lst = []
    fl_all = fl.read()
    lst_rec = fl_all.split('\n')
    for rec in lst_rec:
        end_lst.append(rec)
        rec_lst = rec.split(',')
        if len(rec_lst) > 1:
            dct = {}
            for ind, rec in enumerate(rec_lst):
                key_nm = ind
                dct[key_nm] = rec[1:-1]
                # change sorted as it doesnt work in our scenario
            sorted(dct.iterkeys())
            end_lst.append(dct)
    return end_lst

logs = read_logs('./tollfree.txt')
for i in range(1,5):
    print logs[i]
