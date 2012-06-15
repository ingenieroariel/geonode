from geonode.csw.backends.base import BaseCSWBackend
from owslib.csw import CatalogueServiceWeb
from urlparse import urlparse


class CSWBackend(BaseCSWBackend):
    def __init__(self, *args, **kwargs):
        self.type = 'geonetwork'
        self.url = kwargs['URL']
        self.user = kwargs['USERNAME']
        self.password = kwargs['PASSWORD']
        skip_caps = True
        if 'SKIP_CAPS' in kwargs:
            skip_caps = kwargs['SKIP_CAPS']
        self._group_ids = {}
        self._operation_ids = {}
        self.connected = False

        CatalogueServiceWeb.__init__(self, url=self.url, skip_caps=skip_caps)

        upurl = urlparse(self.url)

        self.base = '%s://%s/' % (upurl.scheme, upurl.netloc)
