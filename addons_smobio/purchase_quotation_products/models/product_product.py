##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
# from odoo.osv.orm import setup_modifiers
from lxml import etree


class ProductProduct(models.Model):
    _inherit = "product.product"

    qty_purchase = fields.Float(
        string='Quantity',
        compute='_compute_qty_purchase',
        help="Technical field. Used to compute the quantity of products"
        " related to a purchase order using the context",
    )

    def _compute_qty_purchase(self):
        purchase_order_id = self._context.get('active_id', False)
        ProductUom = self.env['uom.uom']
        if not purchase_order_id:
            self.update({'qty_purchase': 0})
            return

        purchase_order_lines = self.env['purchase.order'].browse(
            purchase_order_id).order_line

        for rec in self:
            lines = purchase_order_lines.filtered(
                lambda x: x.product_id == rec)
            value = sum([ProductUom._compute_quantity(
                line.product_qty,
                line.product_uom,
                rec.uom_po_id) for line in lines])
            rec.qty_purchase = value

    def _set_qty_purchase(self, qty):
        self.ensure_one()
        purchase_order_id = self._context.get('active_id', False)
        if purchase_order_id:
            lines = self.env['purchase.order.line'].search([
                ('order_id', '=', purchase_order_id),
                ('product_id', '=', self.id)])
            if lines:
                (lines - lines[0]).unlink()
                lines[0].product_qty = qty
                lines[0]._onchange_quantity()
            else:
                self.env['purchase.order'].browse(
                    purchase_order_id).add_products(self, qty)

    def action_product_form(self):
        self.ensure_one()
        view_id = self.env['ir.model.data'].xmlid_to_res_id(
            'product.product_normal_form_view')
        return {
            'name': _('Product'),
            'view_type': 'form',
            "view_mode": 'form',
            'res_model': 'product.product',
            'type': 'ir.actions.act_window',
            # 'domain': [('id', 'in', self.apps_product_ids.ids)],
            'res_id': self.id,
            'view_id': view_id,
        }

    def action_product_add_one_for_purchase(self):
        sale_order_id = self._context.get('active_id', False)
        if not sale_order_id:
            return True
        for rec in self:
            # we find a sol and if the uom of the sol and the product are
            # different convert qty to sum an unit from sol uom to product uom
            line = self.env['sale.order.line'].search([
                ('order_id', '=', sale_order_id),
                ('product_id', '=', rec.id)], limit=1)
            qty = 1.0
            if line.product_uom != rec.uom_id:
                qty = line.product_uom._compute_quantity(
                    qty, rec.uom_id)
            rec.qty_purchase += qty

    # TODO we should make this module inherits from sale one, value on context
    # should be the same and then we should use same computed field
    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        """
        If we came from sale order, we send in context 'force_product_edit'
        and we change tree view to make editable and also field qty
        """
        res = super(ProductProduct, self).fields_view_get(
            view_id=view_id, view_type=view_type,
            toolbar=toolbar, submenu=submenu)
        purchase_quotation_products = self._context.get(
            'purchase_quotation_products')
        if purchase_quotation_products and view_type == 'tree':
            doc = etree.XML(res['arch'])

            # replace uom_id to uom_po_id field
            node = doc.xpath("//field[@name='uom_id']")[0]
            replacement_xml = """
                <field name="uom_po_id"/>
                """
            uom_po_id_node = etree.fromstring(replacement_xml)
            node.getparent().replace(node, uom_po_id_node)
            res['fields'].update(self.fields_get(['uom_po_id']))

            # make all fields not editable
            for node in doc.xpath("//field"):
                node.set('readonly', '1')
                # setup_modifiers(node, res['fields'], in_tree_view=True)

            # add qty field
            placeholder = doc.xpath("//field[1]")[0]
            placeholder.addprevious(
                etree.Element('field', {
                    'name': 'qty_purchase',
                    # we force editable no matter user rights
                    'readonly': '0',
                }))
            # add button add one
            placeholder.addprevious(
                etree.Element('button', {
                    'name': 'action_product_add_one_for_purchase',
                    'type': 'object',
                    'icon': 'fa-plus',
                    'string': _('Add one'),
                }))
            res['fields'].update(self.fields_get(['qty_purchase']))

            # add button tu open form
            placeholder = doc.xpath("//tree")[0]
            placeholder.append(
                etree.Element('button', {
                    'name': 'action_product_form',
                    'type': 'object',
                    'icon': 'fa-external-link',
                    'string': _('Open Product Form View'),
                }))

            # make tree view editable
            for node in doc.xpath("/tree"):
                node.set('edit', 'true')
                node.set('create', 'false')
                node.set('editable', 'top')
            res['arch'] = etree.tostring(doc)
        return res

    def write(self, vals):
        """
        Si en vals solo viene qty y purchase_quotation_products entonces es un
        dummy write y hacemos esto para que usuarios sin permiso de escribir
        en productos puedan modificar la cantidad
        """
        # usamos 'qty_purchase' in vals y no vals.get('qty_purchase') porque
        # se podria estar pasando qty_purchase = 0 y queremos que igal entre
        if self._context.get('purchase_quotation_products') and \
                len(vals) == 1 and 'qty_purchase' in vals:
            # en vez de hacerlo con sudo lo hacemos asi para que se guarde
            # bien el usuario creador y ademas porque SUPERADMIN podria no
            # tener el permiso de editar productos
            # self = self.sudo()
            qty = vals.get('qty_purchase')
            for rec in self:
                rec._set_qty_purchase(qty)
            return True
        return super(ProductProduct, self).write(vals)
