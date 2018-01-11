from _ssl import txt2obj

from dateutil.relativedelta import relativedelta
import datetime
import logging
import time
import os
from openerp.osv import osv, fields
import openerp.tools
from openerp.tools.translate import _

from openerp.addons.decimal_precision import decimal_precision as dp

_logger = logging.getLogger(__name__)


class custom_contract(osv.osv):
    _inherit = 'account.analytic.account'
    _columns = {
        'include_cdr_amount': fields.boolean('Calculate amount from CDR files', store=True),
    }

    def cron_save_cdr_logs(self, cr, uid, context=None):

        logs = self.read_cdr_files(cr,uid)
        for log in logs:
            partner = self.pool.get('res.partner').browse(cr, uid, log['item16'])#replace this with sql query
            print partner.name#initialize partner model
        return True

    # Get Wizard Record
    def read_cdr_files(self, cr, uid, context=None,):
        end_lst = []
        # return_list = []
        # change the below cod3e or comment it
        path = os.path.expanduser('E:/My Projects/odoo-8.0/ERP/custom_contracts/tollfree.txt')
        # get pATH OF THR FOLDER WHERE FILES ARE STORED
        list_of_files = os.listdir(path)
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
                if len(end_lst) > 0:
                    file_to_dic[index] = end_lst
                    end_lst = []
                    index = index + 1
            # return return_list
            return file_to_dic
        except:
            print("File is not present in current directory")



    # This is the function which is reponsible to create invoice lines from cron job we must modified these lines
    def _prepare_invoice_line(self, cr, uid, line, fiscal_position, context=None):
        fpos_obj = self.pool.get('account.fiscal.position')
        res = line.product_id
        account_id = res.property_account_income.id
        if not account_id:
            account_id = res.categ_id.property_account_income_categ.id
        account_id = fpos_obj.map_account(cr, uid, fiscal_position, account_id)

        taxes = res.taxes_id or False
        tax_id = fpos_obj.map_tax(cr, uid, fiscal_position, taxes, context=context)
        values = {
            'name': line.name,
            'account_id': account_id,
            'account_analytic_id': line.analytic_account_id.id,
            'price_unit': line.price_unit or 0.0,
            'quantity': line.quantity,
            'uos_id': line.uom_id.id or False,
            'product_id': line.product_id.id or False,
            'invoice_line_tax_id': [(6, 0, tax_id)],
        }
        return values

    def _prepare_invoice_lines(self, cr, uid, contract, fiscal_position_id, context=None):
        fpos_obj = self.pool.get('account.fiscal.position')
        fiscal_position = None
        if fiscal_position_id:
            fiscal_position = fpos_obj.browse(cr, uid,  fiscal_position_id, context=context)
        invoice_lines = []
        for line in contract.recurring_invoice_line_ids:
            values = self._prepare_invoice_line(cr, uid, line, fiscal_position, context=context)
            invoice_lines.append((0, 0, values))
        return invoice_lines

    def _prepare_invoice(self, cr, uid, contract, context=None):
        invoice = self._prepare_invoice_data(cr, uid, contract, context=context)
        invoice['invoice_line'] = self._prepare_invoice_lines(cr, uid, contract, invoice['fiscal_position'], context=context)
        return invoice

    def _recurring_create_invoice(self, cr, uid, ids, automatic=False, context=None):
        context = context or {}
        invoice_ids = []
        current_date = time.strftime('%Y-%m-%d')
        if ids:
            contract_ids = ids
        else:
            contract_ids = self.search(cr, uid, [('recurring_next_date', '<=', current_date), ('state', '=', 'open'),
                                                 ('recurring_invoices', '=', True), ('type', '=', 'contract')])
        if contract_ids:
            cr.execute(
                'SELECT company_id, array_agg(id) as ids FROM account_analytic_account WHERE id IN %s GROUP BY company_id',
                (tuple(contract_ids),))
            for company_id, ids in cr.fetchall():
                context_contract = dict(context, company_id=company_id, force_company=company_id)
                for contract in self.browse(cr, uid, ids, context=context_contract):
                    try:
                        invoice_values = self._prepare_invoice(cr, uid, contract, context=context_contract)
                        invoice_ids.append(
                            self.pool['account.invoice'].create(cr, uid, invoice_values, context=context))
                        next_date = datetime.datetime.strptime(contract.recurring_next_date or current_date, "%Y-%m-%d")
                        interval = contract.recurring_interval
                        if contract.recurring_rule_type == 'daily':
                            new_date = next_date + relativedelta(days=+interval)
                        elif contract.recurring_rule_type == 'weekly':
                            new_date = next_date + relativedelta(weeks=+interval)
                        elif contract.recurring_rule_type == 'monthly':
                            new_date = next_date + relativedelta(months=+interval)
                        else:
                            new_date = next_date + relativedelta(years=+interval)
                        self.write(cr, uid, [contract.id], {'recurring_next_date': new_date.strftime('%Y-%m-%d')},
                                   context=context)
                        if automatic:
                            cr.commit()
                    except Exception:
                        if automatic:
                            cr.rollback()
                            _logger.exception('Fail to create recurring invoice for contract %s', contract.code)
                        else:
                            raise
        return invoice_ids
