from dateutil.relativedelta import relativedelta
import datetime
import logging
import time
import os
from openerp.osv import osv, fields
import openerp.tools
from openerp.tools.translate import _
from config import file_location

from openerp.addons.decimal_precision import decimal_precision as dp

_logger = logging.getLogger(__name__)


class custom_contract(osv.osv):
    _inherit = 'account.analytic.account'
    _columns = {
        'include_cdr_amount': fields.boolean('Calculate amount from CDR files', store=True),
    }

    def cron_save_cdr_logs(self, cr, uid, context=None):
        cdr_log = self.pool.get('cdr.logs')
        logs = self.read_cdr_files(cr,uid)
        for log in logs:
            if len(log) == 16:
                hash_key = log[14].replace('"', '')
                cr.execute("select id,name from res_partner where hash_key='" + hash_key.strip() + "'")
                partner = cr.dictfetchall()
                if len(partner) > 0:
                    res = {
                        'customer_id': partner[0]['id'],
                        'customer_name': partner[0]['name'],
                        'hash_key': hash_key.strip(),
                        'region': log[9].replace('"', '').strip(),
                        'incoming_call_receiver': log[2].replace('"', '').strip(),
                        'dialer': log[3].replace('"', '').strip(),
                        'time_stamp': log[5].replace('"', '').strip() + " " + log[6].replace('"', '').strip(),
                        'total_call_time_from_dialing': log[7].replace('"', '').strip(),
                        'calling_talk_time': log[8].replace('"', '').strip(),
                        'charging_rate': log[11].replace('"', '').strip(),
                        'call_type': log[10].replace('"', '').strip(),
                        'type': 'normal'
                    }
                    cdr_log.create(cr, uid, res, context=context)
            elif len(log) == 18:
                hash_key = log[16].replace('"','')
                cr.execute("select id,name from res_partner where hash_key='"+hash_key.strip()+"'")
                partner = cr.dictfetchall()
                if len(partner)>0:
                    res = {
                        'customer_id': partner[0]['id'],
                        'customer_name': partner[0]['name'] ,
                        'hash_key': hash_key.strip() ,
                        'region': log[11].replace('"','').strip(),
                        'incoming_call_receiver':log[2].replace('"','').strip() ,
                        'dialer': log[3].replace('"','').strip() ,
                        'time_stamp': log[7].replace('"','').strip() + " " + log[8].replace('"','').strip(),
                        'total_call_time_from_dialing': log[9].replace('"','').strip(),
                        'calling_talk_time': log[10].replace('"','').strip(),
                        'charging_rate': log[13].replace('"','').strip(),
                        'type': 'tf'
                    }
                    cdr_log.create(cr, uid, res, context=context)
        return True

    # Get Wizard Record
    def read_cdr_files(self, cr, uid, context=None):
        end_lst = []
        for loc in file_location:
            path = os.path.expanduser(loc)
            try:
                #make sure using r'filepath' to mean its a string literal
                fl = open(path,'r')
                fl_all = fl.read()
                lst_rec = fl_all.split('\n')
                for rec in lst_rec:
                    rec_lst = rec.split(',')
                    if len(rec_lst) > 1:
                        end_lst.append(rec_lst)
            except:
                print("File is not present in current directory")
        return end_lst


    def cal_invoice_amount(self, cr, uid, partner_id, context=None):
        total = 0.0
        cr.execute("Select * from call_rates where partner_id='"+str(partner_id.id)+"'")
        call_rates = cr.dictfetchall()
        free_mintues = call_rates[0]['free_mins']
        counter = 0.0
        cr.execute("SELECT * FROM public.cdr_logs where charging_rate>0 and customer_id='" + str(partner_id.id) + "'"+"order by charging_rate asc")
        call_history = cr.dictfetchall()
        for log in call_history:
            if counter > free_mintues:
                talk_time = log['calling_talk_time']/60
                if log['charging_rate']== 0.02 and log['type']=='tf':
                    total = total+ talk_time*call_rates[0]['tf_package_one']
                elif log['charging_rate']== 0.04 and log['type']=='tf':
                    total = total+ talk_time*call_rates[0]['tf_package_two']
                elif log['charging_rate']== 0.12 and log['type']=='tf':
                    total = total+ talk_time*call_rates[0]['tf_package_three']
                elif log['charging_rate']== 0.16 and log['type']=='tf':
                    total = total+ talk_time*call_rates[0]['tf_package_four']
                elif log['charging_rate']== 0.25 and log['type']=='tf':
                    total = total+ talk_time*call_rates[0]['tf_package_five']
                elif log['call_type']=='National' and log['type']=='normal':
                    total = total + talk_time * call_rates[0]['national_rates']
                elif log['call_type']=='Mobile' and log['type']=='normal':
                    total = total + talk_time * call_rates[0]['mobile_rates']
                elif log['call_type']=='Local' and log['type']=='normal':
                    total = total + talk_time * call_rates[0]['local_rates']
                elif log['call_type']=='Special' and log['type']=='normal':
                    total = total + talk_time * call_rates[0]['local_rates']
            else:
                counter = counter + (log['calling_talk_time']/60)
        return total

    # This is the function which is reponsible to create invoice lines from cron job we must modified these lines
    def _prepare_invoice_line(self, cr, uid, line,contract, fiscal_position, context=None):
        amount = self.cal_invoice_amount(cr, uid, contract.partner_id, context=context)
        fpos_obj = self.pool.get('account.fiscal.position')
        res = line.product_id
        account_id = res.property_account_income.id
        if not account_id:
            account_id = res.categ_id.property_account_income_categ.id
        account_id = fpos_obj.map_account(cr, uid, fiscal_position, account_id)

        taxes = res.taxes_id or False
        tax_id = fpos_obj.map_tax(cr, uid, fiscal_position, taxes, context=context)
        if contract.include_cdr_amount:
            values = {
                'name': line.name,
                'account_id': account_id,
                'account_analytic_id': line.analytic_account_id.id,
                'price_unit': amount or 0.0,
                'quantity': line.quantity,
                'uos_id': line.uom_id.id or False,
                'product_id': line.product_id.id or False,
                'invoice_line_tax_id': [(6, 0, tax_id)],
            }
        else:
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

    def _prepare_invoice_lines(self, cr, uid, contract,fiscal_position_id, context=None):
        fpos_obj = self.pool.get('account.fiscal.position')
        fiscal_position = None
        if fiscal_position_id:
            fiscal_position = fpos_obj.browse(cr, uid,  fiscal_position_id, context=context)
        invoice_lines = []
        for line in contract.recurring_invoice_line_ids:
            values = self._prepare_invoice_line(cr, uid, line,contract,fiscal_position, context=context)
            invoice_lines.append((0, 0, values))
        return invoice_lines

    def _prepare_invoice(self, cr, uid, contract, context=None):
        invoice = self._prepare_invoice_data(cr, uid, contract, context=context)
        invoice['invoice_line'] = self._prepare_invoice_lines(cr, uid, contract,invoice['fiscal_position'], context=context)
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
                        if contract.include_cdr_amount:
                            invoice_values = self._prepare_invoice(cr, uid, contract,context=context_contract)
                            invoice_values['invoice_type'] = 'CDR'
                        else:
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
