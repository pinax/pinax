$(function() {
    var ymap = document.getElementById('ymap');
    if(ymap) {
        var map = new YMap(ymap);
        // Add map type control  
        map.addTypeControl();  
        // Add map zoom (long) control  
        map.addZoomLong();  
        // Add the Pan Control  
        map.addPanControl();
        for(var i = 0; i < _geo.length; ++i) {
            var g = _geo[i];
            var yPoint = new YGeoPoint(g[0], g[1]);
            // Display the map centered on a geocoded location
            map.drawZoomAndCenter(yPoint, 12);
            // Create a new marker for an address
            var myMarker = new YMarker(yPoint);
            // Create some content to go inside the SmartWindow
            var myMarkerContent = g[2];
            // When the marker is clicked, show the SmartWindow
            YEvent.Capture(myMarker, EventsList.MouseClick, function() {
                myMarker.openSmartWindow(myMarkerContent); 
            });
            // Put the marker on the map
            map.addOverlay(myMarker);
            var pageLink = document.getElementById('loc_' + i);
            if(pageLink) {
                pageLink.onclick = function() {
                    var geoIndex = parseInt(this.id.replace('loc_', ''), 10);
                    var g = _geo[geoIndex];
                    var yPoint = new YGeoPoint(g[0], g[1]);
                    map.drawZoomAndCenter(yPoint, 12);
                };
            }
        }
    }
});