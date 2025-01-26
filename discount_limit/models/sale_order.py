# -*- coding: utf-8 -*-
import typing
from odoo import fields, models, api


class SaleOrder(models.Model):
    """This model is used to add a new state to sales order."""
    _inherit = 'sale.order'

    state = fields.Selection(
        selection_add=[('approval', 'Approval'), ('sent', 'Quotation Sent')])

    # @api.model
    # def create(self, vals):
    #     """Check the discount limit on creation of order."""
    #     record = super(SaleOrder, self).create(vals)
    #     record._check_discount_limit()
    #     return record

    def write(self, vals):
        """Check the discount limit on update of order."""
        vals['state'] = self._check_discount_limit()
        return super(SaleOrder, self).write(vals)

    @api.onchange('order_line')
    def _onchange_order_line(self):
        """Change the state of the order based on limit."""
        state = self._check_discount_limit()
        print("sattae", state)

    def _check_discount_limit(self):
        """Check the discount amount exceeds the discount limit."""
        limit = self.env['ir.config_parameter'].sudo().get_param('sale_discount_limit.discount_limit')
        limit_value = float(limit)
        # for order in self:
        actual_products_amount = 0
        orders_items = self.order_line
        untaxed_amount = self.amount_untaxed
        for item in orders_items:
            actual_products_amount = actual_products_amount + item.price_unit * item.product_uom_qty
        if untaxed_amount < actual_products_amount - limit_value:
            return 'approval'
        else:
            return 'draft'

    def action_approval(self):
        """After approval state change to sent."""
        print("hi")
        # for order in self:
        # self.with_context(_check_discount_called=True).write({'state': 'sent'})
