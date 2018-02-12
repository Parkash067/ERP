from dateutil.relativedelta import relativedelta

import logging
from openerp.osv import osv, fields
import openerp.tools
from openerp.tools.translate import _
from datetime import date, timedelta,datetime
import time
from dateutil.relativedelta import *

from openerp.addons.decimal_precision import decimal_precision as dp


class custom_hr(osv.osv):
    _inherit = 'hr.employee'
    _columns = {
        'ird_number': fields.char('IRD Number', store=True)
    }

    def cal_commission(self, res, commision_type, cr, uid, context=None):
        sale_won = self.pool.get('sale.won')
        lead_to_opportunity = self.pool.get('lead.to.opportunity')
        total_opportunities = len(res)
        if commision_type == 'lead_to_opportunity_date':
            if total_opportunities > 15:
                if (total_opportunities%15) >= 1:
                    for i in reversed(range(total_opportunities%15)):
                        lead_to_opportunity.create(cr,uid,{'sales_person': res[i]['user_id'],
                                                           'date_of_sale': res[i]['lead_to_opportunity_date'],
                                                           'commission_amount': 50}, context=None)
                elif (total_opportunities%15) == 0 and (total_opportunities/15) >1:
                    for i in reversed(range(total_opportunities / 15)):
                        lead_to_opportunity.create(cr, uid, {'sales_person': res[i]['user_id'],
                                                             'date_of_sale': res[i]['lead_to_opportunity_date'],
                                                             'commission_amount': 50}, context=None)
        elif commision_type == 'sale_confirm_date':
            if total_opportunities > 5:
                if (total_opportunities%5) >= 1:
                    for i in reversed(range(total_opportunities%5)):
                        sale_won.create(cr,uid,{'sales_person': res[i]['user_id'],
                                                           'date_of_sale': res[i]['sale_confirm_date'],
                                                           'commission_amount': 100}, context=None)
                elif (total_opportunities%5) == 0 and (total_opportunities/5) >1:
                    for i in reversed(range(total_opportunities / 5)):
                        sale_won.create(cr, uid, {'sales_person': res[i]['user_id'],
                                                             'date_of_sale': res[i]['sale_confirm_date'],
                                                             'commission_amount': 100}, context=None)
        return True

    def cal_employee_commissions(self, cr, uid, context=None):
        start_date = fields.datetime.now()
        end_date = datetime.strptime(str(start_date).split(' ')[0],'%Y-%m-%d')-timedelta(days=7)
        print start_date
        print end_date
        cr.execute("Select id from res_users")
        results = cr.dictfetchall()
        commission_types = ['lead_to_opportunity_date','sale_confirm_date']
        for commission_type in commission_types:
            for result in results:
                cr.execute("Select user_id,lead_to_opportunity_date,sale_confirm_date from crm_lead where "+commission_type+" between'"+str(end_date).split(' ')[0]+"'"+"and'"+str(start_date).split(' ')[0]+"'"+"and user_id ='"+str(result['id'])+"'")
                res=cr.dictfetchall()
                self.cal_commission(res,commission_type,cr,uid,context=None)
        print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Job Done >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
        return True


class custom_sales_won_commision(osv.osv):
    _name = 'sale.won'
    _columns = {
        'sales_person': fields.many2one('res.users', 'Sales Person', store=True),
        'date_of_sale': fields.date('Date', store=True),
        'commission_amount': fields.float('Amount', store=True)
    }


class custom_lead_to_opportunity_commision(osv.osv):
    _name = 'lead.to.opportunity'
    _columns = {
        'sales_person': fields.many2one('res.users', 'Sales Person', store=True),
        'date_of_sale': fields.date('Date', store=True),
        'commission_amount': fields.float('Amount', store=True)
    }


