## -*- coding: utf-8 -*-
import logging

from pylons import request, response, session, tmpl_context as c, url

from pytis.lib.base import BaseController, render, render_macro
from pytis.model.order import Order, Delegation
import pytis.lib.helpers as h
import webhelpers.paginate as paginate
from pytis.model.form import DelegationForm
from pytis.lib.helpers import flash
from sqlalchemy import desc

log = logging.getLogger(__name__)

class DelegationsController(BaseController):

    @h.auth.authorize(h.auth.is_valid_user)
    def __before__(self):
        pass

    def list(self):
        records = Delegation.query.order_by(desc(Delegation.id))
        c.paginator = paginate.Page(
            records,
            page=int(request.params.get('page', 1)),
            items_per_page = 30,
        )
        return render('/delegations/list.xhtml')

    def edit(self, id):
        c.delegation = Delegation.query.get_or_abort(id)
        c.form = DelegationForm(request.POST, obj=c.delegation)
        
        if request.method == 'POST' and c.form.validate():
            c.form.populate_obj(c.delegation)
            c.delegation.save()
            
            flash(u'Delegacja pomyślnie zapisana')
            return self.redirect(url(controller='delegations', action='edit', id=id))            
        
        return render('/delegations/edit.xhtml')

    def print_delegation(self, id):
        c.delegation = Delegation.query.get_or_abort(id)
        return h.generate_pdf('/prints/delegation.xhtml', 'delegacja')
    
    def show_orders(self, id):
        c.orders = Order.query.filter(Order.delegation_id == id)
        
        return render_macro('/base/macros.xhtml', 'show_orders', delegation_id=id, orders=c.orders)
        
