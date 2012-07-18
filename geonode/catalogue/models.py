from django.db import models
from geonode.catalogue import get_catalogue
from geonode.layers.models import Layer

def delete_layer(instance, sender, **kwargs): 
    """
    Removes the layer from Catalogue
    """
    catalogue = get_catalogue()
    catalogue.remove_record(instance.uuid)


def post_save_layer(instance, sender, **kwargs):
    # If this object was saved via fixtures,
    # do not do post processing.
    if kwargs.get('raw', False):
        return

    catalogue = get_catalogue()
    catalogue.create_record(instance)

models.signals.pre_delete.connect(delete_layer, sender=Layer)
models.signals.post_save.connect(post_save_layer, sender=Layer)
