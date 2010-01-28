var map;
var layer_mapnik;
var layer_tah;
var layer_markers;

function drawmap(map_id, lang_code, popuptext, lon, lat, zoom, marker_lon, marker_lat, marker_width, marker_height) {
	log("draw OpenStreetMap:");
	log("map_id:" + map_id);
	log("lang_code:" + lang_code);
	log("popuptext:" + popuptext);
	log("lon:" + lon + " lat:" + lat, " zoom:" + zoom);
	log("marker lon:" + marker_lon + " lat:" + marker_lat);
	log("marker size:" + marker_width + "x" + marker_height);
	
    OpenLayers.Lang.setCode(lang_code);
	
    map = new OpenLayers.Map(map_id, {
        projection: new OpenLayers.Projection("EPSG:900913"),
        displayProjection: new OpenLayers.Projection("EPSG:4326"),
        controls: [
            new OpenLayers.Control.MouseDefaults(),
            new OpenLayers.Control.LayerSwitcher(),
            new OpenLayers.Control.PanZoomBar()],
        maxExtent:
            new OpenLayers.Bounds(-20037508.34,-20037508.34,
                                    20037508.34, 20037508.34),
        numZoomLevels: 18,
        maxResolution: 156543,
        units: 'meters'
    });

    layer_mapnik = new OpenLayers.Layer.OSM.Mapnik("Mapnik");
    layer_markers = new OpenLayers.Layer.Markers("Address", { projection: new OpenLayers.Projection("EPSG:4326"),
    	                                          visibility: true, displayInLayerSwitcher: false });

    map.addLayers([layer_mapnik, layer_markers]);
    jumpTo(lon, lat, zoom);

    addMarker(layer_markers, marker_lon, marker_lat, popuptext, marker_width, marker_height);
}

function jumpTo(lon, lat, zoom) {
    var x = Lon2Merc(lon);
    var y = Lat2Merc(lat);
    map.setCenter(new OpenLayers.LonLat(x, y), zoom);
    return false;
}

function Lon2Merc(lon) { return 20037508.34 * lon / 180; }

function Lat2Merc(lat) {
    var PI = 3.14159265358979323846;
    lat = Math.log(Math.tan( (90 + lat) * PI / 360)) / (PI / 180);
    return 20037508.34 * lat / 180;
}

function addMarker(layer, lon, lat, popupContentHTML, marker_width, marker_height) {
    var ll = new OpenLayers.LonLat(Lon2Merc(lon), Lat2Merc(lat));
    var feature = new OpenLayers.Feature(layer, ll);
    feature.closeBox = true;
    feature.popupClass = OpenLayers.Class(OpenLayers.Popup.FramedCloud, {minSize: new OpenLayers.Size(marker_width, marker_height) } );
    feature.data.popupContentHTML = popupContentHTML;
    feature.data.overflow = "hidden";

    var marker = new OpenLayers.Marker(ll);
    marker.feature = feature;

    var markerClick = function(evt) {
        if (this.popup == null) {
            this.popup = this.createPopup(this.closeBox);
            map.addPopup(this.popup);
            this.popup.show();
        } else {
            this.popup.toggle();
        }
        OpenLayers.Event.stop(evt);
    };
    marker.events.register("mousedown", feature, markerClick);

    layer.addMarker(marker);
    map.addPopup(feature.createPopup(feature.closeBox));
}

