from modeltranslation.translator import translator, TranslationOptions
from geonode.core.layers.models import Layer

class LayerTranslationOptions(TranslationOptions):
    fields = ('title','abstract','purpose','name',)

translator.register(Layer, LayerTranslationOptions)