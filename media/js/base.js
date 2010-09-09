google.load('jquery', '1.4.2');
google.load('jqueryui', '1.8.1');
google.load('maps', '2.x', {"other_params": "sensor=true"});

function loadLibraries() {
    var libs = [
        "/media/js/markerclusterer.js",
        "/media/js/TimeControl.js",
    ];
    var libsLength = libs.length;
    for (i=0; i<libsLength; i++) {
        var lib = libs[i];
        var counter = libsLength;
        $.getScript(lib, function(code) {
            counter--;
            if (counter == 0) {
                initialize();
            }
        });
    }
}

function initialize() {
    if (!google.maps.BrowserIsCompatible()) {
        $("#map").html("Browser isn't compatible");
        return;
    }
    var markers = [];
    var polygons = [];
    var markerClusterer = null;
    var dateSelectedRange = null;
    var artworkPlaceFilter = "artwork_current_place";
    var map = new google.maps.Map(document.getElementById('map'));
    var timeControlOptions = {
        css: 'slider',
        id: 'sliderTimeControl',
        start: new Date(1600, 1, 1),
        end: new Date(1800, 1, 1),
        selected: [new Date(1675, 1, 1), new Date(1725, 1, 1)],
        format: "yy",
        // There's really any other options for zoom yet.
        // zoom: TimeControl.YEAR,
        onStart: onTimeChange,
        onTimeChange: onTimeChange
    };
    var timeControl = new TimeControl(timeControlOptions);
    function ExhibitControl() {};
    ExhibitControl.prototype = new google.maps.Control();
    ExhibitControl.prototype.initialize = function(map) {
        var container = document.createElement("div");
        var exhibitDiv = $("<DIV>");
        exhibitDiv.html("Exhibit");
        exhibitDiv.attr("href", "javascript:void(0);");
        exhibitDiv.addClass("exhibitMapControl");
        $(container).append(exhibitDiv);
        exhibitDiv.click(function() {
            location.href = "/exhibit/artworks/?"+ dateSelectedRange;
            return false;
        });
        map.getContainer().appendChild(container);
        return container;
    }
    ExhibitControl.prototype.getDefaultPosition = function() {
      return new google.maps.ControlPosition(google.maps.ANCHOR_TOP_RIGHT, new google.maps.Size(214, 7));
    }
    function FilterControl() {};
    FilterControl.prototype = new google.maps.Control();
    FilterControl.prototype.initialize = function(map) {
        var container = document.createElement("div");
        var filterDiv = $("<DIV>");
        var filterLabel = $("<LABEL>");
        var filterSelect = $("<SELECT>");
        var filterOptionsValues = ["artwork_current_place",
                                   "artwork_original_place"];
        var filterOptionsTexts = ["current location",
                                  "original location"];
        filterSelect.attr("id", "filterSelect");
        filterSelect.attr("name", "filterSelect");
        filterLabel.attr("for", "filterSelect");
        filterLabel.html("Artworks by");
        for(i=0; i<2; i++) {
            var filterOption = $("<OPTION>")
            filterOption.html(filterOptionsTexts[i]);
            filterOption.attr("value", filterOptionsValues[i]);
            filterSelect.append(filterOption);
        }
        filterDiv.append(filterLabel);
        filterDiv.append(filterSelect);
        filterSelect.change(function() {
            artworkPlaceFilter = $(this).val();
            onTimeChange(timeControl.selected, timeControl.range);
        });
        filterDiv.attr("href", "javascript:void(0);");
        filterDiv.addClass("filterMapControl");
        $(container).append(filterDiv);
        map.getContainer().appendChild(container);
        return container;
    }
    FilterControl.prototype.getDefaultPosition = function() {
      return new google.maps.ControlPosition(google.maps.ANCHOR_TOP_RIGHT, new google.maps.Size(305, 7));
    }
    map.addControl(timeControl);
    map.addControl(new ExhibitControl());
    map.addControl(new FilterControl());
    map.addControl(new google.maps.LargeMapControl3D());
    map.addMapType(google.maps.PHYSICAL_MAP);
    var hierarchyControl = new google.maps.HierarchicalMapTypeControl();
    hierarchyControl.addRelationship(google.maps.SATELLITE_MAP, google.maps.HYBRID_MAP, null, false);
    map.addControl(hierarchyControl);
    map.setMapType(google.maps.PHYSICAL_MAP);
    // Centered at client location with zoom level 4
    var center;
    if (google.loader.ClientLocation) {
        center = new google.maps.LatLng(google.loader.ClientLocation.latitude,
                                        google.loader.ClientLocation.longitude);
    } else {
        center = new google.maps.LatLng(40.66397287638688, -3.71337890625);
    }
    map.setCenter(center, 4);
    map.enableDragging();
    map.enableScrollWheelZoom();
    $(window).unload(function() {GUnload();});

    function onTimeChange(selected, range) {
        if (range) {
            var yearStart = selected[0].getUTCFullYear();
            var yearEnd = selected[1].getUTCFullYear();
            var url = "/artworks/range/"+ yearStart +"/to/"+ yearEnd +"/";
            var bounds = map.getBounds();
            var southWest = bounds.getSouthWest();
            var northEast = bounds.getNorthEast();
            var data = {
                south_west_longitude: southWest.lng(),
                south_west_latitude: southWest.lat(),
                north_east_longitude: northEast.lng(),
                north_east_latitude: northEast.lat(),
                filter: artworkPlaceFilter
            }
            $("#progress").show();
            // $("#progress").progressbar("destroy");
            $("#progress").progressbar({ value: 0 });
            $.getJSON(url, data, drawClusters);
            dateSelectedRange = "from="+ yearStart +"&to="+ yearEnd;
        }
    }

    function drawClusters(data) {
            $("#progress").progressbar('value', 1);
            var parentMap = map;
            var factor = (100-2) / data.length;
            for(i=0; i<data.length; i++) {
                var item = data[i];
                if (parseInt(i*factor) != parseInt((i-1)*factor)) {
                    $("#progress").progressbar('value', parseInt(i*factor));
                }
                if (item.coordinates) {
                    var geometry = getGeometryFromWKT(item.coordinates, item.place);
                    if (geometry instanceof google.maps.Marker) {
                        geometry.identifier = item.identifier;
                        google.maps.Event.addListener(geometry, "click", function(e) {
                            var url = "/artworks/"+ this.identifier +"/";
                            var parentMarker = this;
                            $.getJSON(url, {}, function(data) {
                                parentMarker.openInfoWindowHtml(data.title +"<br/>("+ data.place +")");
                            });
                        });
                        markers.push(geometry);
                    } else {
                        polygons.push(geometry);
                    }
                }
            }
            if (markerClusterer != null) {
                markerClusterer.clearMarkers();
            }
            markerClusterer = new MarkerClusterer(map, markers);
            $("#progress").hide();
    }

    markerIcon = new google.maps.Icon();
    markerIcon.image = '/media/img/markers/image.png';
    markerIcon.shadow = '/media/img/markers/shadow.png';
    markerIcon.iconSize = new google.maps.Size(28,38);
    markerIcon.shadowSize = new google.maps.Size(47,38);
    markerIcon.iconAnchor = new google.maps.Point(14,38);
    markerIcon.infoWindowAnchor = new google.maps.Point(14,0);
    markerIcon.printImage = '/media/img/markers/printImage.gif';
    markerIcon.mozPrintImage = '/media/img/markers/mozPrintImage.gif';
    markerIcon.printShadow = '/media/img/markers/printShadow.gif';
    markerIcon.transparent = '/media/img/markers/transparent.png';
    markerIcon.imageMap = [19,0,21,1,22,2,23,3,24,4,25,5,26,6,26,7,27,8,27,9,27,10,27,11,27,12,27,13,27,14,27,15,27,16,27,17,27,18,27,19,27,20,26,21,25,22,25,23,24,24,23,25,21,26,20,27,19,28,18,29,17,30,17,31,16,32,16,33,16,34,16,35,15,36,15,37,9,37,8,36,8,35,7,34,6,33,5,32,5,31,5,30,5,29,5,28,5,27,6,26,5,25,4,24,3,23,2,22,1,21,1,20,0,19,0,18,0,17,0,16,0,15,0,14,0,13,0,12,0,11,0,10,0,9,0,8,1,7,1,6,2,5,3,4,4,3,5,2,6,1,8,0];

    function getGeometryFromWKT(wkt, title) {
        polygonRegExp = /^POLYGON\s*\(\((([+-]?\d+(\.\d+)? [+-]?\d+(\.\d+)?,\s*)+([+-]?\d+(\.\d+)? [+-]?\d+(\.\d+)?){1})\)\)$/;
        polygonMatch = wkt.match(polygonRegExp);
        pointRegExp = /^POINT\s*\(([+-]?\d+(\.\d+)? [+-]?\d+(\.\d+)?){1}\)$/;
        pointMatch = wkt.match(pointRegExp);
        if (polygonMatch) {
            var points = [];
            var wktPoints = polygonMatch[1].split(", ");
            for(var i=0; i<wktPoints.length; i++) {
                var wktPoint = wktPoints[i].split(" ");
                var point = new google.maps.LatLng(wktPoint[1], wktPoint[0]);
                points.push(point);
            }
            var polygon = new google.maps.Polygon(points, "#6688CC", 2, undefined, "#6688CC", 0.2);
            return polygon;
        } else if (pointMatch) {
            var wktPoint = pointMatch[1].split(" ");
            var point = new google.maps.LatLng(wktPoint[1], wktPoint[0]);
            var markerOptions = {
                icon: markerIcon,
                title: title
            }
            var marker = new google.maps.Marker(point, markerOptions);
            return marker;
        }
    }

}
google.setOnLoadCallback(loadLibraries);
