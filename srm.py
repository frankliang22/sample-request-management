from openerp.osv import fields,osv
from datetime import datetime,date,timedelta
from time import gmtime, strftime, strptime
import time 
class main(osv.Model):
    _name = "srm.main"
  
    
    
    def set_open(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'open'}, context=context)

    def set_close(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'close'}, context=context)
    
    def _calc_duration (self, cr, uid, ids, field_names, arg, context=None):
        result = {}
        for i in self.browse(cr, uid, ids, context=context):
            start = datetime.strptime(i.sr_date, '%Y-%m-%d')
            end = str(i.exact) 
            if i.exact:
                end = datetime.strptime(i.exact, '%Y-%m-%d')
                DD = timedelta(days=1)
                duration = end-start+DD
                difference = str(duration)
                difference = difference.replace(":","")
                difference = difference.replace(",","")
                difference = difference.rstrip("0")
            else:
                duration = ''
                difference = str(duration)
        result [i.id] = str(difference)
        return result
    

    def _three_days_later(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for i in self.browse(cr, uid, ids, context=context):
            before = datetime.strptime(i.sr_date, '%Y-%m-%d')
            DD = timedelta(days=3)
            later = before + DD
            later_str = str(later)
            later_str = later_str.replace(":","")
            later_str = later_str.replace(",","")
            later_str = later_str.rstrip("0")
            res [i.id] = str(later_str)
        return res
    def _calculate_total(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for i in self.browse(cr,uid,ids,context=context):
            res[i.id] = i.qty*i.unitprice
        return res
    def _total_usd(self,cr,uid,ids,field_name,arg,context=None):
        res = {}
        for i in self.browse(cr,uid,ids,context=context):
            res[i.id] = i.freight + i.amount
        return res
    def _get_default_project_id(self, cr, uid, ctx={}):
        proj = ctx.get('default_project_id', False)
        if type(proj) is int:
            return [proj]
        return proj
    _defaults = {
        
        'state': 'open',
        
    }
   

    _columns = {
        # char field
        'name' :  fields.char(string="SR", size=256, required=True),      
        'sr_cost' : fields.char(string="RD cost center", size=256, required=True),
        'sr_sap' : fields.char(string="SAP#", size=256,),
        'sr_marketing' : fields.char(string="Marketing# or Description", size=256, required=True),
        'tracking': fields.char(string='Tracking number',size=256,required=False),
        'pic1' : fields.char(string='PM',size=256,required=False),
        'pic2' : fields.char(string='Engineer',size=256,required=False),
        'shipping' : fields.char(string='Shipping Account',size=256),
        'dn' : fields.char(string='DN#',size=256),
        'qecomment' : fields.char(string='QE Comments',size=256),
        'customerfeedback' : fields.char(string='Customer Feedback',size=256),
        'delaycomment' : fields.char(string='Comment for delay',size=256),
        'remark' : fields.char(string='Remark',size=256),
        'pic' : fields.char(string='Sales',size=256,required=True),
        'lte' : fields.char(string='LTE',size=256),
        
        # many2one field
        'project_id' : fields.many2one('project.project','Project'),
        'sr_customer' : fields.many2one('res.partner','Customer',required=True),
        
        # float fields
        'freight': fields.float(string="Freight Cost(USD)",digits=(16,2),required=False),
        'samplecost': fields.float(string="Sample cost",digits=(16,2),required=False),
        'unitprice': fields.float('Unit Price(USD)', digits=(16,2), required=False),

        
        # selection fields
        'samplesfee' : fields.selection([('Yes','Y'),('No','N')], 'Samples Fee(Y/N)', select=True),
        'srm' : fields.selection([('ENG','ENG'),('MP','MP')],'ENG or MP'),
        'stock' : fields.selection([('Yes','Y'),('No','N')], 'Use Stock if availiable(Y/N)',select=True),
        'state' : fields.selection([('open','Open'),('close','Close')],'State(Open/Closed)'),
        'freight1' : fields.selection([('Yes','Y'),('No','N')],'Freight(Y/N)'),
        'delay' : fields.selection([('New model delay','New model delay'),('Material delay','Material delay'),('Testing delay','Testing delay'),('Standard driver without safety stock','Standard driver without safety stock'),('Cancel(customer/sales request)','Cancel(customer/sales request)'),('Standard sample testing NG','Standard sample testing NG'),('Ship with other models together (save courier cost)','Ship with other models together (save courier cost)'),('Wait for customer direction',' Wait for customer direction'),('On schedule','On schedule')],"Delay Reason"),
        'status' : fields.selection([('close','close'),('open','open')],'Status'),
        'sample_type' : fields.selection([('transducer','Transducer'),('system','System'),('pbca','PBCA'),('other','Other')],'Sample type',required=True),
        # date fields
        'sr_date': fields.date('SR Date',required=True),
        'estimate' : fields.date('Estimate Sample ETD Date'),
        'samplestart' : fields.date("Sample Build Start Date"),
        'samplefinish' : fields.date("Sample Build Finish Date"),
        'exact' : fields.date('Exact Sample ETD Date'),
        'ready' : fields.date('Material Ready Date'),
        'teststart' : fields.date('Test Start Date'),
        'testfinish' : fields.date('Test Finish Date'),
        'packaging' : fields.date('Packaging Compelete(date)'),
        'inspection' : fields.date('Inspection Date'),
        'submission' : fields.date('Sample Submission Sheet Send to Customer(Date)'),
        'target' : fields.date('Target ETD Date'),
        'material1' : fields.date('Material Short List Release Date'),
        'material2' : fields.date('Material Request Release to Sourcing/Pur Date'),
        'drawing' : fields.date('Drawing Release Date'),

        # function fields
        'duration': fields.function(_calc_duration, store=True,string="Duration", type="char"),
        'amount' : fields.function(_calculate_total,string='Amount(USD)',type='float'),
        'feedback' : fields.function(_three_days_later, string='Feedback ETD Date to Customer',type="char"),
        'total' : fields.function(_total_usd,string='Total(USD)',type='float'),
       
        # text fields
        'sr_status' : fields.text('Status'),
        'comment' : fields.text('Comment(delay reason)'),
        'sample_requirements' : fields.text('Sample requirements'),
        # integer fields
        'qty' : fields.integer('Qty(pc)',required=True),
    }

   
