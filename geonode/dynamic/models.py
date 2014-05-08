from geonode.dynamic.model_generator import ModelGenerator
from django.conf import settings

if 'datastore' in settings.DATABASES:
    gen = ModelGenerator('datastore', globals())
    gen.generate_models()
