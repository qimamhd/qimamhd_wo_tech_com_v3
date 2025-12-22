# -*- coding: utf-8 -*-
import re
from odoo import api, models, fields, exceptions,_
from odoo.exceptions import ValidationError
from datetime import datetime

class xx_car_services_lines(models.Model):
    _inherit = 'wo.services.header.lines'

    enter_technical_commission_manual = fields.Boolean(default=lambda self: self._default_enter_technical_commission_manual(),
                                              compute="_get_enter_technical_commission_manual")

    # @api.depends('company_id')
    def _get_enter_technical_commission_manual(self):

       
        for rec in self:
            rec.enter_technical_commission_manual = self.user_has_groups('qimamhd_wo_tech_com_v3.group_allow_add_technical_commission')

    def _default_enter_technical_commission_manual(self):

       
        return  self.user_has_groups('qimamhd_wo_tech_com_v3.group_allow_add_technical_commission')
  
    # *******************************************************************************************************

class xx_car_installation_order_packages_lines(models.Model):
    _inherit = 'wo.insl.order.packages.lines'

    car_part_commission = fields.Float(string="عمولة الجزء")

 
class xx_car_installation_order_mst(models.Model):
    _inherit = 'wo.installation.order.mst'
    
    
    technical_commission_rqeuired = fields.Boolean(default=lambda self: self._default_technical_commission_rqeuired(),
                                              compute="_get_technical_commission_rqeuired")

    # @api.depends('company_id')
    def _get_technical_commission_rqeuired(self):

        params = self.env['ir.config_parameter'].sudo()
        l_technical_commission_rqeuired = params.get_param('technician_commission_required',
                                                      default=False)
        for rec in self:
            rec.technical_commission_rqeuired = l_technical_commission_rqeuired

    def _default_technical_commission_rqeuired(self):

        params = self.env['ir.config_parameter'].sudo()
        l_technical_commission_rqeuired = params.get_param('technician_commission_required',
                                                      default=False)
        return l_technical_commission_rqeuired
  
    # *******************************************************************************************************

    enter_technical_commission_manual = fields.Boolean(default=lambda self: self._default_enter_technical_commission_manual(),
                                              compute="_get_enter_technical_commission_manual")

    # @api.depends('company_id')
    def _get_enter_technical_commission_manual(self):

       
        for rec in self:
            rec.enter_technical_commission_manual = self.user_has_groups('qimamhd_wo_tech_com_v3.group_allow_add_technical_commission')

    def _default_enter_technical_commission_manual(self):

       
        return  self.user_has_groups('qimamhd_wo_tech_com_v3.group_allow_add_technical_commission')
  
    # *******************************************************************************************************

    def check_technical_commission(self):
        for rec in self:
            if rec.technical_commission_rqeuired:
                for line in rec.lines_services:
                    if not line.car_part_id.car_category_part_flag:
                        if not line.car_part_commission:
                             raise ValidationError( "يجب تحديد عمولة الفني على منطقة الخدمة (%s)" % line.car_part_id.name)
                   
                    elif line.car_part_id.car_category_part_flag:
                        for record_s in line.service_header_id: 
                            for line_s in record_s.service_header_line_ids:
                                if line_s.cart_part_selected and not line_s.car_part_commission:
                                    raise ValidationError( "يجب تحديد عمولة الفني في تفاصيل منطقة الخدمة (%s)" % line.car_part_id.name)

                for line in rec.lines_packages:
                    if not line.car_part_id.car_category_part_flag:
                        if not line.car_part_commission:
                             raise ValidationError( "يجب تحديد عمولة الفني على منطقة الخدمة في الباقة (%s)" % line.car_part_id.name)
                   
                    elif line.car_part_id.car_category_part_flag:
                        for record_s in line.package_header_id: 
                            for line_s in record_s.service_header_line_ids:
                                if line_s.cart_part_selected and not line_s.car_part_commission:
                                    raise ValidationError( "يجب تحديد عمولة الفني في تفاصيل منطقة الخدمة في الباقة (%s)" % line.car_part_id.name)

    def calc_manulal_technician_commission(self):
        for rec in self:
            for wo_line in rec.lines_services:
                if wo_line.car_part_id.car_category_part_flag:
                    for records in wo_line.service_header_id:
                        for line in records.service_header_line_ids:
                            for line_technician in line.technical_name:
                                if line.cart_part_selected:
                                    if len(line.technical_name):
                                        part_commission = line.car_part_commission
                                            
                                        if part_commission:
                                            invoice_date = ''
                                            state = ''
                                            if rec.technical_commission_calc_flag == 'invoice_posted':
                                                invoice_date = rec.create_invoice_id.invoice_date if rec.create_invoice_id.state == 'posted' else False
                                                state = 'posted' if rec.create_invoice_id.state == 'posted' else 'draft'
                                            else:
                                                if rec.state == 'complete_work':
                                                    invoice_date = rec.compelete_done_date if rec.compelete_done_date else rec.order_date
                                                    state = 'posted'
                                                else:
                                                    invoice_date = False
                                                    state = 'draft'

                                            l_tech_comm = part_commission / len(line.technical_name)
                                            commission_report = self.env['wo.installation.technician.com.line'].create({
                                                'invoice_date': invoice_date,
                                                'state':  state,
                                                'header_id': rec.id,
                                                'sale_order_id': rec.sale_order_id.id if rec.sale_order_id else False,
                                                'invoice_id': rec.create_invoice_id.id if rec.create_invoice_id else False,
                                                'technical_id': line_technician.id,
                                                'service_type': line.cart_part_id.name,
                                                'service_type_id': records.service_type.id,
                                                'sale_source': 'service',
                                                'branch_id': rec.branch_id.id,

                                                'com_cal_type':  'part_com',
                                                'cart_part_id': line.cart_part_id.id,
                                                'car_part_id': records.car_part_id.id,
                                                'film_category_id': line.film_category_id.id,
                                                'film_product_id': line.car_film_product_id.id if line.car_film_product_id else False ,
                                                    
                                                'technical_count': len(line.technical_name),
                                                'commission_amount': part_commission,
                                                'technical_commission': l_tech_comm ,
                                                'car_size_id': rec.car_size_id.id,
                                            })
                            
                                 
                else:
                    for line_technician in wo_line.technical_name:
                        if len(wo_line.technical_name):
                           
                            part_commission =  wo_line.car_part_commission
                             
                            if part_commission:
                                invoice_date = ''
                                state = ''
                                if rec.technical_commission_calc_flag == 'invoice_posted':
                                    invoice_date = rec.create_invoice_id.invoice_date if rec.create_invoice_id.state == 'posted' else False
                                    state = 'posted' if rec.create_invoice_id.state == 'posted' else 'draft'
                                else:
                                    if rec.state == 'complete_work':
                                        invoice_date = rec.compelete_done_date if rec.compelete_done_date else rec.order_date
                                        state = 'posted'
                                    else:
                                        invoice_date = False
                                        state = 'draft'

                                l_tech_comm = part_commission / len(wo_line.technical_name)
                                commission_report = self.env['wo.installation.technician.com.line'].create({
                                    'invoice_date': invoice_date,
                                    'state':  state,
                                    'header_id': rec.id,
                                    'sale_order_id': rec.sale_order_id.id if rec.sale_order_id else False,
                                    'invoice_id': rec.create_invoice_id.id if rec.create_invoice_id else False,
                                    'technical_id': line_technician.id,
                                    'service_type': wo_line.car_part_id.name,
                                    'service_type_id': wo_line.service_type.id,
                                    'sale_source': 'service',
                                    'branch_id': rec.branch_id.id,

                                    'com_cal_type':  'part_com',
                                    'cart_part_id': wo_line.car_part_id.id,
                                    'car_part_id': wo_line.car_part_id.id,
                                    'film_category_id': wo_line.film_category_id.id,
                                    'film_product_id': wo_line.car_film_product_id.id if wo_line.car_film_product_id else False ,
                                    'technical_count': len(wo_line.technical_name),
                                    'commission_amount': part_commission,
                                    'technical_commission': l_tech_comm ,
                                    'car_size_id': rec.car_size_id.id,
                                })
            
            for wo_line in rec.lines_packages:
                if wo_line.car_part_id.car_category_part_flag:
                    for records in wo_line.package_header_id:
                        for line in records.service_header_line_ids:
                            for line_technician in line.technical_name:
                                if line.cart_part_selected:
                                    if len(line.technical_name):
                                        part_commission = line.car_part_commission
                                        if part_commission:
                                            invoice_date = ''
                                            state = ''
                                            if rec.technical_commission_calc_flag == 'invoice_posted':
                                                invoice_date = rec.create_invoice_id.invoice_date if rec.create_invoice_id.state == 'posted' else False
                                                state = 'posted' if rec.create_invoice_id.state == 'posted' else 'draft'
                                            else:
                                                if rec.state == 'complete_work':
                                                    invoice_date = rec.compelete_done_date if rec.compelete_done_date else rec.order_date
                                                    state = 'posted'
                                                else:
                                                    invoice_date = False
                                                    state = 'draft'

                                            l_tech_comm = part_commission / len(line.technical_name)
                                            commission_report = self.env['wo.installation.technician.com.line'].create({
                                                'invoice_date': invoice_date,
                                                'state':  state,
                                                'header_id': rec.id,
                                                'sale_order_id': rec.sale_order_id.id if rec.sale_order_id else False,
                                                'invoice_id': rec.create_invoice_id.id if rec.create_invoice_id else False,
                                                'technical_id': line_technician.id,
                                                'service_type': line.cart_part_id.name,
                                                'service_type_id': records.service_type.id,
                                                'sale_source': 'service',
                                                'branch_id': rec.branch_id.id,

                                                'com_cal_type':  'part_com',
                                                'cart_part_id': line.cart_part_id.id,
                                                'car_part_id': records.car_part_id.id,
                                                'film_category_id': line.film_category_id.id,
                                                'film_product_id': line.car_film_product_id.id if line.car_film_product_id else False ,
                                                    
                                                'technical_count': len(line.technical_name),
                                                'commission_amount': part_commission,
                                                'technical_commission': l_tech_comm ,
                                                'car_size_id': rec.car_size_id.id,
                                            })

                             
                          
                else:
                    for line_technician in wo_line.technical_name:
                        if len(wo_line.technical_name):

                            part_commission = wo_line.car_part_commission
                             
                            if part_commission:
                                invoice_date = ''
                                state = ''
                                if rec.technical_commission_calc_flag == 'invoice_posted':
                                    invoice_date = rec.create_invoice_id.invoice_date if rec.create_invoice_id.state == 'posted' else False
                                    state = 'posted' if rec.create_invoice_id.state == 'posted' else 'draft'
                                else:
                                    if rec.state == 'complete_work':
                                        invoice_date = rec.compelete_done_date if rec.compelete_done_date else rec.order_date
                                        state = 'posted'
                                    else:
                                        invoice_date = False
                                        state = 'draft'

                                l_tech_comm = part_commission / len(wo_line.technical_name)
                                commission_report = self.env['wo.installation.technician.com.line'].create({
                                    'invoice_date': invoice_date,
                                    'state':  state,
                                    'header_id': rec.id,
                                    'sale_order_id': rec.sale_order_id.id if rec.sale_order_id else False,
                                    'invoice_id': rec.create_invoice_id.id if rec.create_invoice_id else False,
                                    'technical_id': line_technician.id,
                                    'service_type': wo_line.car_part_id.name,
                                    'service_type_id': wo_line.service_type.id,
                                    'sale_source': 'service',
                                    'branch_id': rec.branch_id.id,

                                    'com_cal_type':  'part_com',
                                    'cart_part_id': wo_line.car_part_id.id,
                                    'car_part_id': wo_line.car_part_id.id,
                                    'film_category_id': wo_line.film_category_id.id,
                                    'film_product_id': False ,
                                    'technical_count': len(wo_line.technical_name),
                                    'commission_amount': part_commission,
                                    'technical_commission': l_tech_comm ,
                                    'car_size_id': rec.car_size_id.id,
                                })

  
