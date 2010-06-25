from unittest import TestCase

class WSGIAppSecurityTestCase(TestCase):
    def __init__(self, *args, **kw):
        TestCase.__init__(self, *args, **kw)
        try:
            app = self.app
        except AttributeError:
            name= '.'.join([self.__class__.__module__,  self.__class__.__name__])
            raise AttributeError("You need to place the wsgi app to test at ""%s's 'app' attribute" % name)
        if not isinstance(app, TestApp):
            self.app = TestApp(app)
        else:
            self.app = app

    def get(self, url, remote_user=None, **kw):
        extra_env = kw.setdefault('extra_environ', {})
        if remote_user:
            extra_env['REMOTE_USER'] = remote_user
    
        return self.app.get(url, **kw)

    def post(self, url, remote_user=None, **kw):
        extra_env = kw.setdefault('extra_environ', {})
        if remote_user:
            extra_env['REMOTE_USER'] = remote_user

        return self.app.post(url, **kw)

    def failUnlessForbidden(self, url, remote_user, method="GET",
                            msg="Status code is not 403", **kw):
        meth = getattr(self, method.lower())
        kw['status'] = 403
        try:
            meth(url, remote_user, **kw)
        except AppError:
            self.fail(msg)

    def failUnlessUnauthorized(self, url, method="GET",
                             msg="Status code is not 401", **kw):
        meth = getattr(self, method.lower())
        kw['status'] = 401
        try:
            meth(url, **kw)
        except AppError:
            self.fail(msg)

    def failUnlessAllowed(self, url, remote_user=None, method="GET", msg="Status code is not 200 or redirection", **kw):
        meth = getattr(self, method.lower())
        try:
            meth(url, remote_user, **kw)
        except AppError:
            self.fail(msg)         