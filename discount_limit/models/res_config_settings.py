# -*- coding: utf-8 -*-
from email.policy import default

from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    """The model is used to add a discount limit feature within the sales settings."""
    _inherit = 'res.config.settings'

    is_discount_limit = fields.Boolean(string='Discount limit',
                                        config_parameter='sale_discount_limit.is_discount_limit',
                                        help='Check this field for enabling discount limit')
    discount_type = fields.Selection([('fixed','Fixed'), ('percentage','Percentage')], default='fixed')
    discount_fixed_limit = fields.Float(string='Limit amount',
                                        config_parameter='sale_discount_limit.discount_fixed_limit',
                                        help='The discount limit in amount')
    discount_percentage_limit = fields.Float(string='Limit Percentage %',
                                        config_parameter='sale_discount_limit.discount_percentage_limit',
                                        help='The discount limit in percentage')


    @api.onchange('discount_type')
    def _onchange_discount_type(self):
        if self.discount_type == 'fixed':
            self.discount_percentage_limit = 0
        else:
            self.discount_fixed_limit = 0


