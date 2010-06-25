from pytis.model import User, meta
from sqlalchemy import *                # can I limit what I get?
from logging import basicConfig, DEBUG, INFO, debug, info, warning, error, critical
from authkit.permissions import Permission
from authkit.permissions import NotAuthenticatedError, NotAuthorizedError

import logging
log = logging.getLogger(__name__)

basicConfig(level=DEBUG, format="%(levelname)s:%(module)s: %(message)s") # default WARNING

session = meta.Session
session.clear()            # remove stale info

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

def _getuser(environ):
    """Get the user from the environ, puke if none.
    """
    from pylons import session as s
    if 'user' not in s:
        raise NotAuthenticatedError('Not Authenticated')
    elif not 'login' in s['user']:
        raise NotAuthorizedError('Not Authorized')    
    
    user = session.query(User).filter_by(login=s['user']['login']).one()
    debug("getuser user=%s" % user)
    if not user:
        warning("No user found with username=%s" % s['user']['login'])
        raise NotAuthorizedError("No user found with username=%s" % s['user']['login'])
    return user

class RoleIn(Permission):
    """Does the user have a role in the supplied list of roles (logical OR).
    A user can have more than one role.
    """
    def __init__(self, roles):
        self.roles = _downlist(roles)
        
    def check(self, app, environ, start_response):
        user = _getuser(environ)
        for role in user.roles:
            if role.name in self.roles:
                return app(environ, start_response)
        warning("User roles=%s not in required=%s" % (user.roles, self.roles))
        raise NotAuthorizedError("User roles=%s not in required=%s" % (user.roles, self.roles))
    
    
class GroupIn(Permission):
    """Is the users's group in the supplied list of groups (logical OR).
    A user can have only one group.
    """
    def __init__(self, groups):
        self.groups = _downlist(groups)
        
    def check(self, app, environ, start_response):
        user = _getuser(environ)        
        if user.group.name in self.groups:
            return app(environ, start_response)
        warning("User group=%s not in required=%s" % (user.group, self.groups))          
        raise NotAuthorizedError("User group=%s not in required=%s" % (user.group, self.groups))
