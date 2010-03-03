jQuery(document).ready(function() {
$('._polygon-field-js').each(function() {
    var fieldId = $(this).html();
    var geomPolygon;
    var geomPolygonColor = "#2b82bd";
    var wktGeometry = $('#'+ fieldId).val();
    var initialWKTGeometry = wktGeometry;
    var geomMap;
    var geomMarker;
    var geomMarkersPolygon = [];
    var geomRadius;
    var geomType;
    var geomReversePlacemark;
    var geomAccuracy;
    var geomDragIcon = new GIcon();
    geomDragIcon.image = "http://labs.google.com/ridefinder/images/mm_20_blue.png";
    geomDragIcon.shadow = "http://labs.google.com/ridefinder/images/mm_20_shadow.png";
    geomDragIcon.iconSize = new GSize(12, 20);
    geomDragIcon.shadowSize = new GSize(22, 20);
    geomDragIcon.iconAnchor = new GPoint(6, 20);

    var POINT = 'P';
    var CIRCLE = 'C';
    var POLYGON = 'L';
    var HANDWRITING = 'H';


    function getCircle(center, radius, nodes, liColor, liWidth, liOpa, fillColor, fillOpa){
        // Enhanced from http://esa.ilmari.googlepages.com/circle.htm
        var latConv = center.distanceFrom(new GLatLng(parseFloat(center.lat()) + 0.1, center.lng())) / 100;
        var lngConv = center.distanceFrom(new GLatLng(center.lat(), parseFloat(center.lng()) + 0.1)) / 100;
        var points = [];
        var step = parseInt(360 / nodes) || 10;
        for(var i=0; i<=360; i+=step) {
          var point = new GLatLng(parseFloat(center.lat()) + (radius / latConv * Math.cos(i * Math.PI / 180)),
                                  parseFloat(center.lng()) + (radius / lngConv * Math.sin(i * Math.PI / 180)));
          points.push(point);
        }
        fillColor = fillColor || liColor || geomPolygonColor;
        liWidth = liWidth || 2;
        var poly = new GPolygon(points, liColor, liWidth, liOpa, fillColor, fillOpa);
        return poly;
    }

    function getSquare(center, radius, liColor, liWidth, liOpa, fillColor, fillOpa) {
        return getCircle(center, radius, 4, liColor, liWidth, liOpa, fillColor, fillOpa)
    }

    function loadGeometryFromWKT(wkt) {
        polygon_re = /^POLYGON\s*\(\((([+-]?\d+(\.\d+)? [+-]?\d+(\.\d+)?,\s*)+([+-]?\d+(\.\d+)? [+-]?\d+(\.\d+)?){1})\)\)$/;
        polygon_match = wkt.match(polygon_re);
        point_re = /^POINT\s*\(([+-]?\d+(\.\d+)? [+-]?\d+(\.\d+)?){1}\)$/;
        point_match = wkt.match(point_re);
        if (polygon_match) {
            geomType = POLYGON;
            $('#'+ fieldId +'geom-type').val(POLYGON);
            var points = [];
            var wkt_points = polygon_match[1].split(", ");
            for(var i=0; i<wkt_points.length; i++) {
                var wkt_point = wkt_points[i].split(" ");
                var point = new GLatLng(wkt_point[0], wkt_point[1]);
                points.push(point);
            }
            geomPolygon = new GPolygon(points, geomPolygonColor, 2, undefined, geomPolygonColor, 0.2);
            var bounds = geomPolygon.getBounds();
            var center = bounds.getCenter();
            geomMap.setCenter(center);
            geomMarker.setPoint(center);
            geomMap.setZoom(geomMap.getBoundsZoomLevel(bounds));
            if (points.length == 37) {
                // Check whether polygon is a circle and set geomRadius
                var isCircle = true;
                var radius = center.distanceFrom(points[0]);
                var precission = Math.pow(10, 2);
                var truncatedRadius = Math.round(parseInt(radius * precission) / precission)
                for(var i=1; i<points.length-1; i++) {
                    var distance = center.distanceFrom(points[i]);
                    var truncatedDistance = Math.round(parseInt(distance * precission) / precission)
                    isCircle = isCircle && (truncatedRadius == truncatedDistance);
                    if (!isCircle) {
                        break;
                    }
                }
                if (isCircle) {
                    geomRadius = truncatedRadius;
                    geomType = CIRCLE;
                    $('#'+ fieldId +'geom-type').val(CIRCLE);
                }
            }
        } else if (point_match) {
            geomType = POINT;
            $('#'+ fieldId +'geom-type').val(POINT);
            var wkt_point = point_match[1].split(" ");
            var point = new GLatLng(wkt_point[0], wkt_point[1]);
            geomMarker.setPoint(point);
            geomPolygon = undefined;
            geomMap.setCenter(point);
        }
    }

    function initializeGeomMap(show) {
        if (GBrowserIsCompatible()) {
            $('#'+ fieldId).hide();
            $('#'+ fieldId +'geom-map').show();

            geocoder = new GClientGeocoder();
            geomMap = new GMap2(document.getElementById(fieldId +"geom-map"));
            geomMap.addControl(new GLargeMapControl3D());
            geomMap.addControl(new GMenuMapTypeControl());
            geomMap.addControl(new GScaleControl(250));
            geomMap.enableDragging();
            geomMap.disableScrollWheelZoom();
            //geomMap.setCenter(defaultPoint, defaultZoom);

            geomMarker = new GMarker(geomMap.getCenter(), {draggable: true})
            geomMarker.bindInfoWindow($('#'+ fieldId +'geom-info-window')[0]);
            geomOpenInfoWindow();

            GEvent.addListener(geomMarker, 'infowindowopen', geomOpenInfoWindow);
            GEvent.addListener(geomMarker, "drag", geomMarker.closeInfoWindow);
            GEvent.addListener(geomMarker, "dragend", dragEndGeomMarker);
            geomMap.addOverlay(geomMarker);

            GEvent.addListener(geomMap, 'singlerightclick', geomRightClickHandler);
            GEvent.addListener(geomMap, 'zoomend', setSliderZoom);

            geomType = $('#'+ fieldId +'geom-type').val() || POINT;
            $('#'+ fieldId +'geom-type').change(changeGeomType);
            var redraw = false;
            if (initialWKTGeometry) {
                resetGeometry();
                $('#'+ fieldId +'geom-reset').show();
                $('#'+ fieldId +'geom-reset').click(resetGeometry);
                redraw = (initialWKTGeometry == undefined);
            } else {
                changeGeomType(geomType, redraw);
                dragEndGeomMarker(redraw);
            }
        }
    }

    function resetGeometry() {
        geomMarker.closeInfoWindow();
        clearPolygon();
        $('#'+ fieldId).val(initialWKTGeometry);
        loadGeometryFromWKT(initialWKTGeometry);
        var redraw = false;
        redraw = (initialWKTGeometry == undefined);
        changeGeomType(geomType, redraw);
        dragEndGeomMarker(redraw);
        getGeomReverseLocation();
        return false;
    }

    function clearPolygon() {
        if (geomPolygon) {
            geomMap.removeOverlay(geomPolygon);
        }
        if (geomMarkersPolygon) {
            for(var i=0; i<geomMarkersPolygon.length; i++) {
                geomMap.removeOverlay(geomMarkersPolygon[i]);
            }
            geomMarkersPolygon = [];
        }
    }

    function dragEndGeomMarker(redraw) {
        geometryChange(geomRadius, redraw);
        getGeomReverseLocation();
        polygonFit(true);
    }

    function geomRightClickHandler(point, src, overlay) {
        moveGeomMarker(point);
        if (overlay) {
            polygonVertexRemove(overlay);
        }
    }

    function moveGeomMarker(point) {
        if (!geomMarker.draggingEnabled() && geomType != POLYGON) {
            geomMarker.closeInfoWindow();
            var moveGeomMarkerPoint = geomMap.fromContainerPixelToLatLng(point);
            geomMarker.setPoint(moveGeomMarkerPoint);
            getGeomReverseLocation(moveGeomMarkerPoint);
            geometryChange(geomRadius);
        }
    }

    function getGeomReverseLocation(point) {
        point = point || geomMarker.getPoint();
        geocoder.getLocations(point, getGeomReverseLocationHandler);
    }

    function getGeomReverseLocationHandler(response) {
        geomReversePlacemark = "";
        geomAccuracy = null;
        if (response && response.Status.code == 200) {
            geomReversePlacemark = response.Placemark[0];
            geomAccuracy = geomReversePlacemark.AddressDetails.Accuracy * 10;
            var updateAddressFieldId = $('#'+ fieldId +'geom-update-address').val();
            $('#'+ updateAddressFieldId).val(geomReversePlacemark.address);
        }
    }

    function geomOpenInfoWindow() {
        var defaultRadius = getDefaultRadius();
        radiusFactor = calcRadiusFactor(geomMap.getZoom());
        var sliderParams = {min: 0,
                            max: radiusFactor,
                            change: sliderChangeHandler,
                            start: Math.min(radiusFactor, geomRadius) || defaultRadius}
        $('#'+ fieldId +'geom-info-window .slider').slider("destroy");
        $('#'+ fieldId +'geom-info-window .slider').slider(sliderParams);
        if (geomAccuracy) {
            $('#'+ fieldId +'geom-point').html(geomReversePlacemark.address);
            $('#'+ fieldId +'geom-accuracy').html(geomAccuracy +"%");
        } else {
            $('#'+ fieldId +'geom-point').html('');
            $('#'+ fieldId +'geom-accuracy').html('');
        }
        if (geomPolygon) {
            $('#'+ fieldId +'geom-area').html(parseInt(geomPolygon.getArea()) +" m²");
            $('#'+ fieldId +'geom-vertexes').html(geomPolygon.getVertexCount() - 1);
        }
        if (geomType == HANDWRITING) {
            $('#'+ fieldId +'geom-type-polygon').show();
        }
    }

    function changeGeomType(type, notChangePolygon) {
        geomType = $(this).val() || type;
        $('#'+ fieldId +'geom-type-point').hide();
        $('#'+ fieldId +'geom-type-circle').hide();
        $('#'+ fieldId +'geom-type-polygon').hide();
        if (!notChangePolygon) {
            geometryChange(geomRadius, notChangePolygon);
        }
        switch(geomType) {
            case POINT:
                $('#'+ fieldId +'geom-type-point').show();
                polygonFit(true);
            break;
            case CIRCLE:
                $('#'+ fieldId +'geom-type-circle').show();
            break;
            case POLYGON:
            case HANDWRITING:
                $('#'+ fieldId +'geom-type-polygon').show();
            break;
        }
    }

    function calcRadiusFactor(value) {
        return parseInt((16000000 / Math.pow(2, parseInt(value) + 2)) * 10);
    }

    function getDefaultRadius() {
        return calcRadiusFactor(geomMap.getZoom()) * 0.5;
    }

    function setSliderZoom(oldLevel, newLevel) {
        geomMarker.closeInfoWindow();
    }

    function sliderChangeHandler(e, ui) {
        geometryChange(ui.value);
    }

    function polygonColorChange(rgb) {
        if (geomPolygon) {
            geomPolygon.color = rgb;
            geomPolygon.setStrokeStyle({color: rgb});
            geomPolygon.redraw(true);
        }
    }

    function polygonFit(notCalculateCenter) {
        if (!notCalculateCenter) {
            var center = geomPolygon.getBounds().getCenter();
            geomMarker.show();
            geomMarker.setPoint(center);
        }
        wktGeometry = calcWKTGeometryFromMap();
        $('#'+ fieldId).val(wktGeometry);
    }

    function calcWKTGeometryFromMap() {
        if (geomType == POINT) {
            var point = geomMarker.getPoint();
            return "POINT ("+ point.lat() +" "+ point.lng() +")";
        } else if (geomPolygon) {
            var wktPoints = [];
            var vertexCount = geomPolygon.getVertexCount();
            geomMarkersPolygon = geomMarkersPolygon || [];
            for(var i=0; i<vertexCount; i++) {
                var point  = geomPolygon.getVertex(i);
                var wktPoint = point.lat() +" "+ point.lng();
                wktPoints.push(wktPoint);
            }
            if (wktPoints) {
                return "POLYGON (("+ wktPoints.join(", ") +"))";
            }
        }
    }

    function polygonVertexDrag() {
        geomMarker.closeInfoWindow();
        geomMarker.hide();
        var poly = [];
        for(var i=0; i<geomMarkersPolygon.length; i++) {
            poly.push(geomMarkersPolygon[i].getPoint());
        }
        // HACK: Draw strokeColor on last line of polygon
        if ((geomMarkersPolygon.length > 0) &&
            (poly[poly.length] != geomMarkersPolygon[0].getPoint())) {
            poly.push(geomMarkersPolygon[0].getPoint());
        }
        if (geomPolygon) {
            geomMap.removeOverlay(geomPolygon);
        }
        geomPolygon = new GPolygon(poly, 'red', 3, 1, 'red', 0.2);
        geomMap.addOverlay(geomPolygon);
    }

    function polygonVertexDragEnd(point) {
        polygonColorChange(geomPolygonColor);
        polygonFit();
        geomMarker.show()
        polygonFit(true);
    }

    function polygonVertexRemove(marker) {
        var n = geomMarkersPolygon.indexOf(marker);
        if (n >= 0 && geomMarkersPolygon.length > 3) {
            geomMap.removeOverlay(geomMarkersPolygon[n]);
            geomPolygon.deleteVertex(n);
            geomPolygon.redraw(true);
            geomMarkersPolygon.splice(n, 1);
            polygonFit();
        }
    }

    function polygonVertexAdd() {
        var markerIndex = geomMarkersPolygon.indexOf(this);
        var markerIndexAfter;
        if (markerIndex == geomMarkersPolygon.length - 1) {
            markerIndexAfter = 0;
        } else {
            markerIndexAfter = markerIndex + 1;
        }
        var point1 = geomMarkersPolygon[markerIndex].getLatLng();
        var point2 = geomMarkersPolygon[markerIndexAfter].getLatLng();
        var halfwayPoint = new GLatLng((parseFloat(point1.lat()) + parseFloat(point2.lat())) / 2,
                                       (parseFloat(point1.lng()) + parseFloat(point2.lng())) / 2);
        geomPolygon.insertVertex(markerIndexAfter, halfwayPoint);
        redrawPolygon();
    }

    function redrawPolygon() {
        var vertexCount = geomPolygon.getVertexCount();
        geomMarkersPolygon = geomMarkersPolygon || [];
        // HACK: i<vertexCount-1 instead i<vertexCount in order to get the correct number markers
        for(var i=0; i<vertexCount-1; i++) {
            if (geomMarkersPolygon[i]) {
                geomMap.removeOverlay(geomMarkersPolygon[i])
            }
            geomMarkersPolygon[i] = addPolygonMarker(geomPolygon.getVertex(i));
        }
    }

    function addPolygonMarker(vertex) {
        var marker = new GMarker(vertex, {icon: geomDragIcon, draggable: true});
        geomMap.addOverlay(marker);
        marker.enableDragging();
        GEvent.addListener(marker, 'drag', polygonVertexDrag);
        GEvent.addListener(marker, 'dragend', polygonVertexDragEnd);
        GEvent.addListener(marker, 'click', polygonVertexAdd);
        return marker;
    }

    function geometryChange(radius, redraw) {
        if (redraw == undefined) {
            redraw = true;
        }
        var defaultRadius = getDefaultRadius();
        geomRadius = radius || defaultRadius;
        geomMarker.enableDragging();
        clearPolygon();
        if (geomType == CIRCLE) {
            if (geomRadius > 0) {
                var point = geomMarker.getPoint();
                if (redraw) {
                    geomPolygon = getCircle(point, geomRadius / 1000);
                }
                geomMap.addOverlay(geomPolygon);
                geomPolygon.redraw(true);
                polygonFit(true);
            }
            $('#'+ fieldId +'geom-radius').html(geomRadius +" m");
        } else if (geomType == POLYGON) {
            if (geomRadius > 0) {
                var point = geomMarker.getPoint();
                if (redraw) {
                    geomPolygon = getSquare(point, geomRadius / 1000);
                }
                geomMap.addOverlay(geomPolygon);
                redrawPolygon();
                polygonFit();
            }
        } else if (geomType == HANDWRITING) {
            // Using new Google Maps API (>v2.111)
            // http://gmaps-samples.googlecode.com/svn/trunk/poly/mymapstoolbar.html
            geomPolygon = new GPolygon([], geomPolygonColor, 2, undefined, geomPolygonColor, 0.2);
            geomMarker.closeInfoWindow();
            geomMarker.hide();
            geomMarker.disableDragging();
            geomMap.addOverlay(geomPolygon);
            geomPolygon.enableDrawing({onEvent: 'mouseover'});
            geomPolygon.disableEditing({onEvent: 'mouseout'});
            GEvent.addListener(geomPolygon, 'endline', showGeomMarker);
        }
    }

    function showGeomMarker() {
        polygonFit();
        geomMarker.show();
        polygonColorChange(geomPolygonColor);
    }

    initializeGeomMap();
});
});
