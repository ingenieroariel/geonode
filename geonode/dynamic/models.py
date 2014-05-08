from geonode.dynamic.model_generator import ModelGenerator
from django.conf import settings

if 'datastore' not in settings.DATABASES:
    msg = 'Please configure the "datastore" database before enabling dynamic models'
    raise Exception(msg)

gen = ModelGenerator('datastore', globals())
gen.generate_models()

local_vars = locals()
dynamic_models = [local_vars[model_name] for model_name in gen.known_models]
