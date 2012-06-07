"""
Tools for managing a CatalogWebService (CSW)
"""
import os
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module

DEFAULT_CSW_ALIAS = 'default'

# GeoNode uses this if the CSW setting is empty (None).
if not hasattr(settings, 'CSW'):
    settings.CSW = { DEFAULT_CSW_ALIAS: 'geonode.csw.backends.dummy'}

# If settings.CSW is defined, we expect it to be properly named
if DEFAULT_CSW_ALIAS not in settings.CSW:
    raise ImproperlyConfigured("You must define a '%s' CSW" % DEFAULT_CSW_ALIAS)


def load_backend(backend_name):
    # Look for a fully qualified CSW backend name
    try:
        return import_module('.base', backend_name)
    except ImportError as e_user:
        # The CSW backend wasn't found. Display a helpful error message
        # listing all possible (built-in) CSW backends.
        backend_dir = os.path.join(os.path.dirname(__file__), 'backends')
        try:
            available_backends = [f for f in os.listdir(backend_dir)
                    if os.path.isdir(os.path.join(backend_dir, f))
                    and not f.startswith('.')]
        except EnvironmentError:
            available_backends = []

        if backend_name not in available_backends:
            backend_reprs = map(repr, sorted(available_backends))
            error_msg = ("%r isn't an available catalogue backend.\n"
                         "Try using geonode.csw.backends.XXX, where XXX "
                         "is one of:\n    %s\nError was: %s" %
                         (backend_name, ", ".join(backend_reprs), e_user))
            raise ImproperlyConfigured(error_msg)
        else:
            # If there's some other error, this must be an error in GeoNode
            raise

def get_catalogue(backend=None):
    """Returns a catalogue object.
    """
    the_backend = backend or settings.CSW
    default_backend = the_backend[DEFAULT_CSW_ALIAS]
    backend_name = default_backend['ENGINE']
    return load_backend(backend_name)

get_catalogue()
