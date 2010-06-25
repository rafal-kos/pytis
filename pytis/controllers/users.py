## -*- coding: utf-8 -*-

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from pytis.lib.base import BaseController, render
from pytis.lib.helpers import flash
from pytis.model import meta
from pytis.model.user import User, LoginOrEmailExistsException, \
    UserDoesntExistsException
import logging
import pytis.lib.helpers as h
import webhelpers.paginate as paginate
from pytis.model.form import UserEditForm, UserRegisterForm, ChangePasswordForm

log = logging.getLogger(__name__)
 
class UsersController(BaseController):
    
    #@h.cache(600)
    @h.auth.authorize(h.auth.GroupIn('Administratorzy'))
    def list(self):
        records = User.query
        c.paginator = paginate.Page(
            records,
            page=int(request.GET.pop('page', 1)),
            items_per_page = int(request.GET.pop('page_size', 30)),
            **dict(request.GET)
        )
        return render('/users/list.xhtml')     
        
    @h.auth.authorize(h.auth.GroupIn('Administratorzy'))
    def register(self):
        c.form = UserRegisterForm(request.POST)
        
        if request.method == 'POST' and c.form.validate():
            user = User()
            c.form.populate_obj(user, exclude=['id'])
                        
            try:
                user.save()
            except LoginOrEmailExistsException:        
                flash(u'Twój email lub login istnieje już w bazie danych. Użyj innego.')                            
            else:
                flash(u'Użytkownik został pomyślnie dodany do bazy danych.')
                return redirect(url(controller='users', action='list'))                          
        
        return render('/users/register.xhtml')                  
    
    #@h.cache(600)
    @h.auth.authorize(h.auth.GroupIn('Administratorzy'))    
    def edit(self, id):                      
        c.user = User.query.get(id)        
        c.form = UserEditForm(request.POST, obj=c.user, groups = c.user.groups)
        
        if request.method == 'POST' and c.form.validate():
            user = User.query.get_or_abort(id)
            c.form.populate_obj(user, exclude=['id'])
            user.save()
            
            flash(u'Użytkownik pomyślnie edytowany.')
            return redirect(url(controller='users', action='list'))
                
        return render('/users/edit.xhtml')
        
    @h.auth.authorize(h.auth.GroupIn('Administratorzy'))
    def delete(self, id):               
        user = User.query.get_or_abort(id)        
        meta.Session.delete(user)
        meta.Session.commit()
        
        flash(u'Użytkownik pomyślnie usunięty.')
        return redirect(url(controller='users', action='list'))
            
    def login(self):                
        return render('users/login.xhtml')        
        
    def authenticate(self):
        user = User()
        user.login = request.POST['login']
        user.password = request.POST['password']
        
        try:
            user.exists()
        except UserDoesntExistsException:
            flash(u'Niepoprawne dane autoryzacyjne. Sprawdź swój login i hasło.', 'error')
            return redirect(url(controller='users', action='login'))
        
        user = User.query.filter(User.login == request.POST['login']).first()
        flash(u'Witamy w systemie')            
        try:
            session['user'] = {
                'id': user.id,
                'login': user.login
            }
            
            groups = []
            for group in user.groups:
                groups.append(str(group.name).lower())                    
            session['user'].update({'groups': groups})                
        except KeyError:
            pass
        else:
            session.save()
            return redirect(url('/'))                    

    @h.auth.authorize(h.auth.is_valid_user)
    def password_change(self):
        c.form = ChangePasswordForm(request.POST)
        
        if request.method == 'POST' and c.form.validate():
            user = User.query.get(h.auth.user_id())
            user.password = c.form.password.data
            user.save()
            
            flash(u'Hasło zostało zmienione.')
            return self.redirect(url(controller='users', action='list'))
            
        return render('/users/password_change.xhtml')
    
    @h.auth.authorize(h.auth.is_valid_user)
    def logout(self):
        try:
            del(session['user'])
        except KeyError:
            pass
        else:
            session.save()

        return redirect(url(controller='users', action='login'))        