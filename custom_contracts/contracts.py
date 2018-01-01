from openerp.osv import fields, osv
from openerp import api

class invoice_csnumber(osv.osv):
    _inherit = 'account.analytic.account'
    _columns = {
        'include_cdr_amount': fields.boolean('Calculate amount from CDR files', store=True),
    }
