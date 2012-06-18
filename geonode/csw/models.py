from django.db import models
from geonode.csw import CSW
from geonode.layers.models import Layer


#FIXME(Ariel): Should the metadata links live here as a Django model or in the layer object?

def delete_from_catalogue(instance, sender, **kwargs): 
    """
    Removes the layer from GeoServer and Catalogue
    """
    with CSW() as csw_cat:
       csw_cat.delete_layer(instance)


def save_to_catalogue(instance, sender, **kwargs):
    # If this object was saved via fixtures,
    # do not do post processing.
    if kwargs.get('raw', False):
        return

    with CSW() as csw_cat:
        record = csw_cat.get_by_uuid(instance.uuid)
        if record is None:
            md_link = csw_cat.create_from_layer(instance)
            instance.metadata_links = [("text/xml", "TC211", md_link)]
        else:
             csw_cat.update_layer(instance)


def populate_from_catalogue(instance, sender, **kwargs):
    """Fills in information in the instance fields only available
       after instance is in catalogue.
    """
    #FIXME(Ariel): This is legible but has too many levels of nesting.
    with CSW() as csw_cat:
        meta = csw_cat.metadata_record(instance)
        if meta is not None:
            kw_list = reduce(
                    lambda x, y: x + y["keywords"],
                    meta.identification.keywords,
                    [])
            kw_list = [l for l in kw_list if l is not None]
            instance.keywords.add(*kw_list)
            if hasattr(meta.distribution, 'online'):
                onlineresources = [r for r in meta.distribution.online if r.protocol == "WWW:LINK-1.0-http--link"]
                if len(onlineresources) == 1:
                    res = onlineresources[0]
                    instance.distribution_url = res.url
                    instance.distribution_description = res.description



models.signals.pre_delete.connect(delete_from_catalogue, sender=Layer)
models.signals.post_save.connect(save_to_catalogue, sender=Layer)
models.signals.pre_save.connect(populate_from_catalogue, sender=Layer)
