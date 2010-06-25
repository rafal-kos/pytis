from pylons import session
from authkit.permissions import RequestPermission, NotAuthenticatedError, NotAuthorizedError

class AuthenticatedUser(RequestPermission):
    def __init__(self, accept_empty=False):
        self.accept_empty = accept_empty
        
    def check(self, app, environ, start_response):
        if 'user' not in session:
            raise NotAuthenticatedError('Not Authenticated')
        elif self.accept_empty==False and not 'id' in session['user']:
            raise NotAuthorizedError('Not Authorized')
        
        return app(environ, start_response)