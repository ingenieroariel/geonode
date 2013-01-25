{% include 'geonode/ext_header.html' %}
{% include 'geonode/geo_header.html' %}
<style type="text/css">
#aboutbutton {
    display: none;
}
#paneltbar {
    margin-top: 90px;
}
button.logout {
    display: none;
}
button.login {
    display:none;
}
</style>
<script type="text/javascript" src="{{ STATIC_URL}}geonode/js/maps/GeoNode-GeoExplorer.js"></script>
<script type="text/javascript">
var app;
Ext.onReady(function() {
{% autoescape off %}
    var config = Ext.apply({
        authStatus: {% if user.is_authenticated %} 200{% else %} 401{% endif %},
        proxy: "/proxy/?url=",
        printService: "{{GEOSERVER_BASE_URL}}pdf/",
        /* The URL to a REST map configuration service.  This service 
         * provides listing and, with an authenticated user, saving of 
         * maps on the server for sharing and editing.
         */
        rest: "{% url maps_browse %}",
        ajaxLoginUrl: "{% url account_ajax_login %}",
        homeUrl: "{% url home %}",
        localGeoServerBaseUrl: "{{ GEOSERVER_BASE_URL }}",
        localCSWBaseUrl: "{{ CATALOGUE_BASE_URL }}",
        csrfToken: "{{ csrf_token }}",
        defaultSourceType: "gxp_wmscsource",
        sources: {
            local: {
                url: "{{ GEOSERVER_BASE_URL }}ows",
                title: "Local GeoServer",
                ptype: "gxp_wmscsource"
            },
            mapquest: {
                ptype: "gxp_mapquestsource"
            },
            osm: {
                ptype: "gxp_osmsource"
            },
            google: {
                ptype: "gxp_googlesource"
            },
            bing: {
                ptype: "gxp_bingsource"
            },
            mapbox: {
                ptype: "gxp_mapboxsource"
            },
            ol: {
                ptype: "gxp_olsource"
            }
        },
        map: {
            projection: "EPSG:102113",
            layers: [{
                source: "mapquest",
                title: "MapQuest OpenStreetMap",
                name: "osm",
                group: "background"
            }, {
                source: "ol",
                group: "background",
                fixed: true,
                type: "OpenLayers.Layer",
                args: [
                    "None", {visibility: false}
                ]
            }],
            center: [0, 0],
            zoom: 2
        } 
    });


    app = new GeoNode.Composer(config);
{% endautoescape %}
});
</script>
