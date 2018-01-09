from dateutil.relativedelta import relativedelta
import datetime
import logging
import time

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

    def get_customer_details(self, cr, uid, ids, hash_key,context=None):
        res_partner = self.pool.get('res.partner')


    # Get Wizard Record
    def read_logs(self,file_path):
        #make sure using r'filepath' to mean its a string literal
        fl = open(file_path,'r')
        end_lst = []
        fl_all = fl.read()
        lst_rec = fl_all.split('\n')
        for rec in lst_rec:
            rec_lst = rec.split(',')
            print rec_lst
            if len(rec_lst) > 1:
                dct = {}
                for ind, rec in enumerate(rec_lst):
                    key_nm = 'item ' + str(ind)
                    dct[key_nm] = rec[1:-1]

                    # change sorted as it doesnt work in our scenario
                    # sorted(dct,dct.keys())
                end_lst.append(dct)
        return end_lst

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
        print ">>>>>>>>>>>>>>>>>>>>>>>>.invoice lines>>>>>>>>>>>>>"
        print invoice_lines
        return invoice_lines

    def _prepare_invoice(self, cr, uid, contract, context=None):
        invoice = self._prepare_invoice_data(cr, uid, contract, context=context)
        invoice['invoice_line'] = self._prepare_invoice_lines(cr, uid, contract, invoice['fiscal_position'], context=context)
        return invoice

    def _recurring_create_invoice(self, cr, uid, ids, automatic=False, context=None):
        crd_rec = self.read_logs('./tollfree.txt')
        print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>Invoices creation>>>>>>>>>>>>>>>>>>>>"
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
