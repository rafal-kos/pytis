## -*- coding: utf-8 -*-

import sqlalchemy as sa
from sqlalchemy import orm

from pylons import request
from pytis.model import meta
from pytis.lib import util
from pylons.controllers.util import abort
from pytis.lib.utils.datastructures import SortedDict
from pytis.lib import helpers as h
from pytis.model.meta import AbstractBase

BLANK_CHOICE_DASH = [("", "---------")]
   
class ActionObject(AbstractBase):    
    
    def response_action(self, request, queryset):
        data = request.POST.copy()
        data.pop('index', None)

        action = data.pop('action')
        if action:
            func, name, description = self.get_actions(request)[action]
            
            selected = request.POST.getall(h.ACTION_CHECKBOX_NAME)
            if not selected:
                return None
            
            response = func(self, request, queryset.filter(self.__class__.id.in_(selected)).all())
        
            return response
    
    def get_action(self, action):
        if callable(action):
            func = action
            action = action.__name__
        elif hasattr(self.__class__, action):
            func = getattr(self.__class__, action)
        else:
            return None

        if hasattr(func, 'short_description'):
            description = func.short_description
        else:
            description = capfirst(action.replace('_', ' '))

        return func, action, description
        

    def get_actions(self, request):
        if self.actions is None:
            return []

        actions = []

        class_actions = getattr(self, 'actions', [])
        actions.extend([self.get_action(action) for action in class_actions])

        actions.sort(lambda a,b: cmp(a[2].lower(), b[2].lower()))
        actions = SortedDict([
            (name, (func, name, desc))
            for func, name, desc in actions
        ])

        return actions

    def get_action_choices(self, request, default_choices=BLANK_CHOICE_DASH):
        """
        Return a list of choices for use in a form object.  Each choice is a
        tuple (name, description).
        """
        choices = [] + default_choices
        for func, name, description in self.get_actions(request).itervalues():
            choice = (name, description)
            choices.append(choice)
        return choices   