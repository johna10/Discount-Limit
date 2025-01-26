# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """The model is used to add a discount limit feature within the sales settings."""
    _inherit = 'res.config.settings'

    is_discount_limit = fields.Boolean(string='Discount limit',
         config_parameter='sale_discount_limit.is_discount_limit',
         help='Check this field for enabling discount limit')
    discount_limit = fields.Float(string='Limit amount',
         config_parameter='sale_discount_limit.discount_limit',
         help='The discount limit amount in percentage')

    # @api.model
    # def set_values(self):
    #     """Set discount limit value globally."""
    #     res = super(ResConfigSettings, self).set_values()
    #     self.env['ir.config_parameter'].sudo().set_param('sale_discount_limit.discount_limit', self.discount_limit)
    #     return res


