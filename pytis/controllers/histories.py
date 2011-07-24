## -*- coding: utf-8 -*-

from pylons import request, response, session, tmpl_context as c, url
from pytis.lib.base import BaseController, render
from pytis.lib.helpers import flash
from pytis.model import meta
from pytis.model.history import History
import pytis.lib.helpers as h


class HistoriesController(BaseController):

    @h.auth.authorize(h.auth.is_valid_user)
    def __before__(self):
        pass

    def view(self, id):
        object = request.GET.get('object', '')
        c.history = History.query.filter(History.object_id == id).filter(History.table == object).\
                    order_by(History.created_at.desc()).all()

        return render('/histories/view.phtml')