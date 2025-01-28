# -*- coding: utf-8 -*-
import typing
from odoo import fields, models, _, api


class SaleOrder(models.Model):
    """This model is used to add a new state to sales order."""
    _inherit = 'sale.order'

    state = fields.Selection(
        selection_add=[('approval', 'Approval'), ('sale', 'Sales Order')])

    def write(self, vals):
        """Override the write method to check the discount limit on update of the order."""
        res = super(SaleOrder, self).write(vals)
        # Automatically check discount limit and update the state
        if 'order_line' in vals or 'discount' in vals:
            for order in self:
                new_state = order.check_discount_limit()
                if order.state != new_state:
                    order.state = new_state
        return res

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

    def action_quotation_send(self):
        """ Opens a wizard to compose an email, with relevant mail template loaded by default """
        # Trigger the discount limit check before sending the quotation
        for order in self:
            new_state = order.check_discount_limit()
            if order.state != new_state:
                order.state = new_state
                order.message_post(
                    body=f"Order state updated to {new_state} based on discount check before sending quotation.")

        # Existing logic for sending the quotation email
        self.filtered(lambda so: so.state in ('draft', 'sent')).order_line._validate_analytic_distribution()
        lang = self.env.context.get('lang')

        ctx = {
            'default_model': 'sale.order',
            'default_res_ids': self.ids,
            'default_composition_mode': 'comment',
            'default_email_layout_xmlid': 'mail.mail_notification_layout_with_responsible_signature',
            'email_notification_allow_footer': True,
            'proforma': self.env.context.get('proforma', False),
        }

        if len(self) > 1:
            ctx['default_composition_mode'] = 'mass_mail'
        else:
            ctx.update({
                'force_email': True,
                'model_description': self.with_context(lang=lang).type_name,
            })
            if not self.env.context.get('hide_default_template'):
                mail_template = self._find_mail_template()
                if mail_template:
                    ctx.update({
                        'default_template_id': mail_template.id,
                        'mark_so_as_sent': True,
                    })
                if mail_template and mail_template.lang:
                    lang = mail_template._render_lang(self.ids)[self.id]
            else:
                for order in self:
                    order._portal_ensure_token()
        action = {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }
        if (
                self.env.context.get('check_document_layout')
                and not self.env.context.get('discard_logo_check')
                and self.env.is_admin()
                and not self.env.company.external_report_layout_id
        ):
            layout_action = self.env['ir.actions.report']._action_configure_external_report_layout(
                action,
            )
            # Need to remove this context for windows action
            action.pop('close_on_report_download', None)
            layout_action['context']['dialog_size'] = 'extra-large'
            return layout_action
        return action

