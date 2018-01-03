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
