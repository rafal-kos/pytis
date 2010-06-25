## -*- coding: utf-8 -*-

from pylons import session
from authkit.authorize.pylons_adaptors import authorize
from authkit.authorize.pylons_adaptors import authorized
from authkit.permissions import RequestPermission, NotAuthenticatedError, NotAuthorizedError

def _downlist(thing):
    """Turn a string or tuple into a list and downcase it.
    """
    if isinstance(thing, tuple):
        thing = list(thing)
    elif isinstance(thing, str):
        thing = [thing]
    if not isinstance(thing, list):
        raise PermissionSetupError("Argument must be list, tuple or string, not: %s" % thing)
    return [t.lower() for t in thing]

class AuthenticatedUser(RequestPermission):
    def __init__(self, accept_empty=False):
        self.accept_empty = accept_empty
        
    def check(self, app, environ, start_response):
        if 'user' not in session:
            raise NotAuthenticatedError('Not Authenticated')
        elif self.accept_empty == False and not 'id' in session['user']:
            raise NotAuthorizedError('Not Authorized')
        
        return app(environ, start_response)
    
class GroupIn(RequestPermission):
    """Checks that user belongs to group
    """
    def __init__(self, groups):
        self.groups = _downlist(groups)
        
    def check(self, app, environ, start_response):        
        if 'user' not in session:
            raise NotAuthenticatedError('Not Authenticated')
        elif not 'groups' in session['user']:
            raise NotAuthorizedError('Not Authorized')
        
        for group in self.groups:
            if group in session['user']['groups']:
                return app(environ, start_response)
            
        raise NotAuthorizedError(
                u"Użytkownik nie jest członkiem żadnej z grup: %r"%self.groups
            )
               
is_valid_user = AuthenticatedUser()
is_admin = GroupIn('Administratorzy')
is_speditor = GroupIn('Spedytorzy')

def user_id():
    return session['user']['id']

def user_login():
    return session['user']['login']