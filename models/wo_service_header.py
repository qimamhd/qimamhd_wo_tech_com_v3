# -*- coding: utf-8 -*-
from odoo import api, models, fields, exceptions,_
from odoo.exceptions import ValidationError

class xx_car_wo(models.Model):
    _inherit = 'wo.installation.order.mst'

    edit_saleman_priv = fields.Boolean(compute="_get_edit_saleman_priv",default=False)

    @api.depends('user_id')
    def _get_edit_saleman_priv(self):
        for rec in self:
            rec.edit_saleman_priv= False
            if not rec.allow_mgr_cal_commission_priv:
                if rec.sale_order_id or rec.is_user_technical  or rec.state in ('confirm','execute_started','execute_completed','complete_work','sale_order'):
                    rec.edit_saleman_priv = False

                else:
                    rec.edit_saleman_priv = True

            if rec.allow_mgr_cal_commission_priv:
             
                    rec.edit_saleman_priv = True
    
    # @api.onchange('sale_man_id')
    # def _update_saleman(self):
    #     for rec in self:
    #         if rec.sale_order_id:
    #             rec.sale_order_id.write({'sale_man_id':rec.sale_man_id.id})
    #         if rec.create_invoice_id:
    #             rec.create_invoice_id.write({'sale_man_id':rec.sale_man_id.id})

    @api.constrains('sale_man_id')
    def _update_in_save_saleman(self):
        for rec in self:
            if rec.sale_order_id:
                rec.sale_order_id.write({'sales_man_id':rec.sale_man_id.id})
            if rec.sale_order_id.invoice_ids:
                for inv in rec.sale_order_id.invoice_ids:
                    inv.write({'sales_man_id':rec.sale_man_id.id})

              


class xx_car_wo_services_line(models.Model):
    _inherit = 'wo.insl.order.services.lines2'

    edit_technial_priv = fields.Boolean(compute="_get_edit_technial_priv",default=False)
    
    
    @api.depends('header_id')
    def _get_edit_technial_priv(self):
        for rec in self:
            if not rec.header_id.allow_mgr_cal_commission_priv:
                if rec.header_id.sale_order_id or not rec.car_part_flag or not rec.header_id.is_sale_man_technical or rec.header_id.state in ('cancel_order','execute_completed','complete_work'):
                    rec.edit_technial_priv = False
                else:

                    rec.edit_technial_priv = True

            if rec.header_id.allow_mgr_cal_commission_priv:
                if  rec.car_part_flag :
                    rec.edit_technial_priv = True
                else:
                    rec.edit_technial_priv = False
            
   

class xx_car_wo_packages_lines(models.Model):
    _inherit = 'wo.insl.order.packages.lines'


    edit_technial_priv = fields.Boolean(compute="_get_edit_technial_priv",default=False)

    @api.depends('header_id')
    def _get_edit_technial_priv(self):
        for rec in self:
            if not rec.header_id.allow_mgr_cal_commission_priv:
                if rec.header_id.sale_order_id or not rec.car_part_flag or not rec.header_id.is_sale_man_technical or rec.header_id.state in ('cancel_order','execute_completed','complete_work'):
                    rec.edit_technial_priv = False
                else:

                    rec.edit_technial_priv = True

            if rec.header_id.allow_mgr_cal_commission_priv:
                if  rec.car_part_flag:
                    rec.edit_technial_priv = True
                else:
                    rec.edit_technial_priv = False

            


class xx_car_wo_service_header(models.Model):
    _inherit = 'wo.services.header'

  # ====================================================================
    allow_mgr_cal_commission_priv = fields.Boolean(default=lambda self: self._default_allow_mgr_cal_commission_priv(),
                                                compute="_get_allow_mgr_cal_commission_priv")


    def _get_allow_mgr_cal_commission_priv(self):
        for rec in self:
            rec.allow_mgr_cal_commission_priv = self.user_has_groups(
                'qimamhd_wo_v3.group_allow_cal_technical_commission')

    def _default_allow_mgr_cal_commission_priv(self):

        return self.user_has_groups('qimamhd_wo_v3.group_allow_cal_technical_commission')


class xx_car_wo_service_header_line(models.Model):
    _inherit = 'wo.services.header.lines'

    edit_technial_priv = fields.Boolean(compute="_get_edit_technial_priv",default=False)

    @api.depends('header_id')
    def _get_edit_technial_priv(self):
        for rec in self:
            if not rec.header_id.allow_mgr_cal_commission_priv:
                if not rec.cart_part_selected or  rec.header_id.sale_order_id   or rec.header_id.state in ('cancel_order','execute_completed','complete_work'):
                    rec.edit_technial_priv = False
                else:

                    rec.edit_technial_priv = True

            if rec.header_id.allow_mgr_cal_commission_priv:
                if rec.cart_part_selected:
                    rec.edit_technial_priv = True
                else:
                    rec.edit_technial_priv = False
              

            