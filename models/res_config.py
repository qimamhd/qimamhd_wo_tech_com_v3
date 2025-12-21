from odoo import fields, models, _,api
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
 
    technician_commission_required = fields.Boolean(string="ادخال عمولات الفنيين اجباري")
 

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
   
        l_technician_commission_required = params.get_param('technician_commission_required',    default=False)


         
        res.update(technician_commission_required=l_technician_commission_required)

        return res

    def set_values(self):
          super(ResConfigSettings, self).set_values()
         
          self.env['ir.config_parameter'].sudo().set_param(
                  "technician_commission_required",
                    self.technician_commission_required)
