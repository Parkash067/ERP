#The file name of this file must match the filename name which we import in __init__.py file
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import api
from itertools import groupby
from datetime import date, timedelta,datetime
import re


class sales(osv.osv):
    _inherit = "res.partner"
    _columns = {
        'last_name': fields.char('Last Name', store=True, required=True),
        'hash_key': fields.char('Hash Key', store=True),
        'office': fields.char('Office#1', store=True),
        'office_one': fields.char('Office#2', store=True),
        'mobile_one': fields.char('Mobile#2', store=True),
        'phone_one': fields.char('Phone#2', store=True),
    }


class sales_order(osv.osv):
    _inherit = "sale.order"
    _columns = {

    }


class crm_lead(osv.osv):
    _inherit = 'crm.lead'
    _columns = {

    }

    def case_mark_won(self, cr, uid, ids, context=None):
        """ Mark the case as won: state=done and probability=100
        """
        stages_leads = {}
        for lead in self.browse(cr, uid, ids, context=context):
            if lead.partner_id.hash_key:
                stage_id = self.stage_find(cr, uid, [lead], lead.section_id.id or False, [('probability', '=', 100.0), ('on_change', '=', True)], context=context)
                if stage_id:
                    if stages_leads.get(stage_id):
                        stages_leads[stage_id].append(lead.id)
                    else:
                        stages_leads[stage_id] = [lead.id]
                else:
                    raise osv.except_osv(_('Warning!'),
                        _('To relieve your sales pipe and group all Won opportunities, configure one of your sales stage as follow:\n'
                            'probability = 100 % and select "Change Probability Automatically".\n'
                            'Create a specific stage or edit an existing one by editing columns of your opportunity pipe.'))
            else:
                raise osv.except_osv(_('Warning!'),_("Before mark won please enter 'Hash Key' of customer"))
        for stage_id, lead_ids in stages_leads.items():
            self.write(cr, uid, lead_ids, {'stage_id': stage_id}, context=context)
        return True
