"""
Tools for managing a CatalogWebService (CSW)
"""

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module

DEFAULT_CSW_ALIAS = 'default'

if DEFAULT_CSW_ALIAS not in settings.CSW:
    raise ImproperlyConfigured("You must define a '%s' CSW" % DEFAULT_CSW_ALIAS)


def get_catalogue(backend=None, fail_silently=False, **kwds):
    """Load a catalogue backend and return an instance of it.
       If backend is None (default) settings.CSW is used.

       Both fail_silently and other keyword arguments are used in the
       constructor of the backend.
    """
    path = backend or settings.CSW[DEFAULT_CSW_ALIAS]
    try:
        mod_name, klass_name = path.rsplit('.', 1)
        mod = import_module(mod_name)
    except ImportError as e:
        raise ImproperlyConfigured(('Error importing catalogue backend module %s: "%s"'
                                    % (mod_name, e)))
    try:
        klass = getattr(mod, klass_name)
    except AttributeError:
        raise ImproperlyConfigured(('Module "%s" does not define a '
                                    '"%s" class' % (mod_name, klass_name)))
    return klass(fail_silently=fail_silently, **kwds)
