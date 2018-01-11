import sys
import datetime as dt
writer = sys.stdout.write
import os

def read_cdr_files(path):
    end_lst = []
    path_ = os.path.expanduser(path)
    try:
        # make sure using r'filepath' to mean its a string literal
        fl = open(path_, 'r')
        fl_all = fl.read()
        lst_rec = fl_all.split('\n')
        for rec in lst_rec:
            rec_lst = rec.split(',')
            if len(rec_lst) > 1:
                print rec_lst
                dct = {}
                for ind, rec in enumerate(rec_lst):
                    key_nm = 'item' + str(ind)
                    dct[key_nm] = rec[1:-1]
                end_lst.append(dct)
    except:
        print("File is not present in current directory")
    return end_lst
lst = read_cdr_files('./custom_contracts/tollfree.txt')



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



