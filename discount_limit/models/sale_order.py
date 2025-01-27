# -*- coding: utf-8 -*-
import typing
from odoo import fields, models, _


class SaleOrder(models.Model):
    """This model is used to add a new state to sales order."""
    _inherit = 'sale.order'

    state = fields.Selection(
        selection_add=[('approval', 'Approval'), ('sale', 'Sales Order')])

    # def write(self, vals):
    #     """Check the discount limit on update of order."""
    #
    #     super(SaleOrder, self).write(vals)
    #     vals['state'] = self.check_discount_limit()
    #     print('NEW')
    #     print('vals', vals)
    #     return super(SaleOrder, self).write(vals)


    def check_discount_limit(self):
        """Check the discount amount exceeds the discount limit."""
        print('step 1')
        limit_amount = self.env['ir.config_parameter'].sudo().get_param('sale_discount_limit.discount_fixed_limit')
        limit_percent = self.env['ir.config_parameter'].sudo().get_param('sale_discount_limit.discount_percentage_limit')
        limit_fixed = float(limit_amount)
        limit_percentage = float(limit_percent)
        print('Limit Amount', limit_fixed)
        print('Limit Percentage', limit_percentage)
        print(' ')

        actual_products_amount = 0
        orders_items = self.order_line
        untaxed_amount = self.amount_untaxed
        print('untaxed_amount', untaxed_amount)
        print(self.state)

        for item in orders_items:
            print(item.discount)
            actual_products_amount = actual_products_amount + item.price_unit * item.product_uom_qty
        print('Actual Product Price :', actual_products_amount)
        #If discount limit is a Fixed amount
        if limit_fixed != 0:
            if untaxed_amount < actual_products_amount - limit_fixed:
                print('Limit')
                return 'approval'
            else:
                print('No Limit')
                return 'draft'
        #If discount limit is a percentage
        else:
            if untaxed_amount < actual_products_amount - (actual_products_amount * (limit_percentage/100)):
                print('Limit from percentage')
                return 'approval'
            else:
                print('No Limit from percentage')
                return 'draft'

    def _confirmation_error_message(self):
        """ Return whether order can be confirmed or not if not then return error message. """
        self.ensure_one()
        if self.state not in {'draft', 'sent', 'approval'}:
            return _("Some orders are not in a state requiring confirmation.")
        if any(
            not line.display_type
            and not line.is_downpayment
            and not line.product_id
            for line in self.order_line
        ):
            return _("A line on these orders missing a product, you cannot confirm it.")

        return False

    def action_approval(self):
        """After approval state change to Sales order."""
        self.action_confirm()
