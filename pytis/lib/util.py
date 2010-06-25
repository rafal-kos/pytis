## -*- coding: utf-8 -*-

import warnings
from decorator import decorator

def deprecated(message):
    """Wrap a function with a warnings.warn and augmented docstring."""

    def wrapper(func, *args, **kwargs):
        warnings.warn(message, stacklevel=3)
        return func(*args, **kwargs)

    return decorator(wrapper)

def obj2dict(obj):
    """Convert object to dict"""
    return dict((key, value) for key, value in obj.__dict__.iteritems() 
                      if not callable(value) and not key.startswith('__'))