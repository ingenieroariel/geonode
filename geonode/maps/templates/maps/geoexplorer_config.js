{
  "defaultSourceType": "gxp_wmscsource",
  "about": {
    "abstract": "",
    "title": ""
  },
  "map": {
    "layers": [
      {
        "opacity": 1,
        "source": "0",
        "fixed": false,
        "visibility": true
      },
      {
        "opacity": 1,
        "group": "background",
        "args": [
          "No background"
        ],
        "visibility": false,
        "source": "1",
        "fixed": true,
        "type": "OpenLayers.Layer"
      },
      {
        "opacity": 1,
        "group": "background",
        "args": [
          "OpenStreetMap"
        ],
        "visibility": false,
        "source": "1",
        "fixed": true,
        "type": "OpenLayers.Layer.OSM"
      },
      {
        "opacity": 1,
        "group": "background",
        "name": "osm",
        "visibility": true,
        "source": "2",
        "fixed": false
      },
      {
        "opacity": 1,
        "group": "background",
        "name": "naip",
        "visibility": false,
        "source": "2",
        "fixed": false
      },
      {
        "opacity": 1,
        "group": "background",
        "name": "AerialWithLabels",
        "visibility": false,
        "source": "3",
        "fixed": true
      },
      {
        "opacity": 1,
        "source": "4",
        "fixed": false,
        "visibility": true
      },
      {
        "opacity": 1,
        "selected": true,
        "group": "background",
        "args": [
          "bluemarble",
          "http:\/\/maps.opengeo.org\/geowebcache\/service\/wms",
          {
            "layers": [
              "bluemarble"
            ],
            "tiled": true,
            "tilesOrigin": [
              -20037508.34,
              -20037508.34
            ],
            "format": "image\/png"
          },
          {
            "buffer": 0
          }
        ],
        "visibility": false,
        "source": "1",
        "fixed": true,
        "type": "OpenLayers.Layer.WMS"
      }
    ],
    "center": [
      0,
      0
    ],
    "units": "m",
    "maxResolution": 156543.03390625,
    "maxExtent": [
      -20037508.34,
      -20037508.34,
      20037508.34,
      20037508.34
    ],
    "zoom": 1,
    "projection": "EPSG:900913"
  },
  "id": null,
  "sources": {
    "1": {
      "ptype": "gxp_olsource"
    },
    "0": {
      "url": "http:\/\/localhost:8080\/geoserver\/wms",
      "restUrl": "\/gs\/rest",
      "ptype": "gxp_wmscsource"
    },
    "3": {
      "ptype": "gxp_bingsource"
    },
    "2": {
      "ptype": "gxp_mapquestsource"
    },
    "4": {
      "ptype": "gxp_mapboxsource"
    }
  }
}
