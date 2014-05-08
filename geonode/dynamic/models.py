from geonode.dynamic.model_generator import ModelGenerator
from django.conf import settings

if 'datastore' not in settings.DATABASES:
    msg = 'Please configure the "datastore" database before enabling dynamic models'
    raise Exception(msg)

gen = ModelGenerator('datastore', globals())
gen.generate_models()

local_vars = locals()
dynamic_models = [local_vars[model_name] for model_name in gen.known_models]

class DynamicManager(models.Manager):
    def get_queryset(self):
        return super(DatastoreManager, self).get_queryset().using('datastore')


def get_model(table_name, db_key='datastore', namespace=globals()):
    model_str = gen.generate_model(table_name)
    exec model_str in namespace
    model_name = table_name.replace('_', ' ').title().replace(' ','')
    return model_name
