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
        'account_no': fields.char('Account No.', store=True)
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


class cdr(osv.osv):
    _name = 'cdr.logs'
    _columns = {
        'customer_id': fields.integer('Customer ID', store=True),
        'customer_name': fields.char('Customer Name', store=True),
        'hash_key': fields.char('Hash Key', store=True),
        'region': fields.char('Region', store=True),
        'incoming_call_receiver': fields.char('Number Dialed', store=True),
        'dialer': fields.char('Dialer', store=True),
        'time_stamp': fields.datetime('Time_Stamp', store=True),
        'total_call_time_from_dialing': fields.integer('Call Duration', store=True),
        'calling_talk_time': fields.integer('Talk Time', store=True),
        'charging_rate': fields.float('Charging Rate', store=True),
        'call_type': fields.selection([('Mobile', 'Mobile'),
                                       ('Local', 'Local'),
                                       ('National', 'National'),
                                       ('International', 'International')],string='Call Type', store=True),
        'type': fields.selection([('tf', 'Toll Free'), ('normal', 'Normal')],string='Type', store=True)
    }


class call_packages(osv.osv):
    _name = 'call.rates'
    _rec_name = 'partner_id'
    _columns = {
        'partner_id': fields.many2one('res.partner', store=True, string='Customer', required=True),
        'hash_key': fields.related('partner_id', 'hash_key', type='char', store=True, string='Hash Key', readonly=True),
        'tf_package_one': fields.float('0.02C', store=True),
        'tf_package_two': fields.float('0.04C', store=True),
        'tf_package_three': fields.float('0.12C', store=True),
        'tf_package_four': fields.float('0.16C', store=True),
        'tf_package_five': fields.float('0.25C', store=True),
        'local_rates': fields.float('Local Call Rate Normal Billing', store=True),
        'national_rates': fields.float('National Call Rate Normal Billing', store=True),
        'mobile_rates': fields.float('Mobile Call Rate Normal Billing', store=True),
        'special_number': fields.float('Special Number Call Rate Normal Billing', store=True),
        'international_rates_id': fields.one2many('international.rates','call_rates_id','International Rates', store=True)
    }

    _sql_constraints = [
        ('partner_id', 'unique(partner_id)', 'Rates have been already defined of this customer!')
    ]


class international_rates(osv.osv):
    _name = 'international.rates'
    _rec_name = 'country_id'

    _columns = {
        'call_rates_id': fields.many2one('call.rates', store=True),
        'country_id': fields.many2one('res.country','Country', store=True, required=True),
        'name': fields.related('country_id', 'name', type='char', store=True, string='Name', readonly=True),
        'rates': fields.float('Rates', store=True)
    }

