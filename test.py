import sys
import os
import datetime as dt
def read_logs(file_path):
    # make sure using r'filepath' to mean its a string literal
    if 'toll_free' in file_path:
        ctype = 'Toll Free'
    else:
        ctype='Normal'
    fl = open(file_path, 'r')
    end_lst = []
    fl_all = fl.read()
    lst_rec = fl_all.split('\n')
    for rec in lst_rec:
        end_lst.append(rec)
        rec_lst = rec.split(',')
        if len(rec_lst) > 10:
            dct = {}
            for ind, rec in enumerate(rec_lst):
                key_nm = ind
                dct[key_nm] = rec[1:-1]
                dct['type'] = ctype
                # change added by adding another item to dictionary
                # change sorted as it doesnt work in our scenario
            sorted(dct.iterkeys())
            end_lst.append(dct)
    print end_lst[0]
    return end_lst
# read_logs('./custom_contracts/tollfree.txt')
def list_all_text_files():
    path = r'C:\Users\kickahs\Desktop\erp'
    all_files = os.listdir(path)
    txt_files= filter(lambda file:file[-4:] == '.txt',all_files)
    return txt_files
# this function saves logs in cdr logs table
# def save_logs(logs_dict):
#     for logs in logs_dict:
#         rec_id = self.env['res.partner'].search([('hash_kay','=',logs[14])])
#         usr_name= self.env['res.partner'].browse([rec_id.id]).name
#         tm_stamp=logs[7] + ' ' +logs[8]
#         dt_tm_stamp=dt.datetime.strptime(tm_stamp,"%Y-%m-%d %H:%M:%S")
#         vals={
#             'customer_id': rec_id.id,
#             'customer_name': usr_name,
#             'hash_key': logs[14],
#             # 'country': ,no idea about this
#             'Incoming_call_receiver': logs[2],
#             'dialer': logs[3],
#             'time_stamp': dt_tm_stamp, # for this import date time and dt.datetime.strp method
#             'total_call_time_from_dialing': logs[9],
#             'calling_talk_time': logs[10],
#             'Mobile_phone_county': logs[11],
#             'charging_rate': logs[12],
#             'actual_amount_charged': logs[13],
#             'hash_code': logs[14],
#             'type': logs['type']}
#
#         # i think it is dot make sure
#         rec_logs_id = self.env['cdr_logs'].search([('hash_kay','=',vals['hash_code'])])
#         rec_redundant=self.env['cdr_logs'].browse(rec_logs_id.id)
#
#         if not rec_redundant:
#             new_ids_created = self.env['cdr_logs'].create(vals)
#             self.env.cr.commit()
#         else:
#             print "data already exist"
#

def selected_files(lst):
    end_lst = []
    # return_list = []
    # change the below cod3e or comment it
    # path = os.path.expanduser('E:/My Projects/odoo-8.0/ERP/custom_contracts/tollfree.txt')
    # get pATH OF THR FOLDER WHERE FILES ARE STORED
    list_of_files = os.listdir(lst)
    txt_files = filter(lambda file: file[-4:] == '.txt', list_of_files)

    # list_of_usable_file = []
    try:
        file_to_dic = {}
        index = 0
        for single_text_file_path in txt_files:
            single_text_file_path = r'C:\Users\kickahs\Desktop\erp' + '\\' + single_text_file_path
            # make sure using r'filepath' to mean its a string literal
            fl = open(single_text_file_path, 'r')
            fl_all = fl.read()
            lst_rec = fl_all.split('\n')
            for rec in lst_rec:
                rec_lst = rec.split(',')
                if len(rec_lst) > 10:
                    dct = {}
                    for ind, rec in enumerate(rec_lst):
                        key_nm = 'item' + str(ind)
                        dct[key_nm] = rec[1:-1]
                    end_lst.append(dct)
                    # list_of_usable_file.append(single_text_file_path)
                    # update path to original
                    single_text_file_path = r'C:\Users\kickahs\Desktop\erp'
                else:
                    # update path to original
                    # single_text_file_path = r'C:\Users\kickahs\Desktop\erp'
                    break

            # if len(end_lst)>0:
            #     return_list.append(end_lst)
            if len(end_lst)>0:
                file_to_dic[index] = end_lst
                end_lst =  []
                index = index + 1
        # return return_list
        return file_to_dic
    except:
        print("File is not present in current directory")



# print list_all_text_files()
for rec,value in selected_files(r'C:\Users\kickahs\Desktop\erp').items():
    print value
