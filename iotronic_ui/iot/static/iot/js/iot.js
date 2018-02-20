/* Additional JavaScript for iot. */

//alert('MELO');

//var image_url = 'https://ing-res-17.me.trigrid.it/iotronic/';
var images_url = 'http://'+location.host+'/dashboard/static/iot/images/';

var markers = [];
markers = L.markerClusterGroup({
	spiderfyOnMaxZoom: false,
	disableClusteringAtZoom: 17
});


var marker_red = L.icon({
	iconUrl: images_url+'marker-icon-red.png',
	iconAnchor:[12.5, 41],
	shadowUrl: images_url+'marker-shadow.png'
});


var marker_green = L.icon({
	iconUrl: images_url+'marker-icon-green.png',
	iconAnchor:[12.5, 41],
	shadowUrl: images_url+'marker-shadow.png'
});


var marker_blue = L.icon({
	iconUrl: images_url+'marker-icon.png',
	iconAnchor:[12.5, 41],
	shadowUrl: images_url+'marker-shadow.png'
});


var labels = [];
var latitude = [];
var longitude = [];
var altitude = [];
var statuses = [];
var last_update = [];


function render_map(map_id, coordinates){
	var osmUrl='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
	var osm = new L.TileLayer(osmUrl, {});
	
	var lat = 38.20523;
	var lon = 15.55972;
	if(coordinates["coordinates"].length ==1){
		lat = coordinates["coordinates"][0].lat;
		lon = coordinates["coordinates"][0].lon;
	}
	var map = L.map(map_id, {scrollWheelZoom:false, worldCopyJump: true}).setView([lat, lon], 12);
	map.addLayer(osm);
	
	//Copyright
	L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
		attribution: '&copy; <a href="https://osm.org/copyright">OpenStreetMap</a> - by <b>MDSLab</b>'
	}).addTo(map);

	//var marker = L.marker([lat, lon]);
	//marker.setIcon(marker_red);
	coord = coordinates["coordinates"];
	for(var i=0;i<coord.length;i++){

		labels.push(coord[i].label);
		latitude.push(parseFloat(coord[i].lat));
		longitude.push(parseFloat(coord[i].lon));
		altitude.push(parseFloat(coord[i].alt));
		statuses.push(coord[i].status);
		last_update.push(coord[i].updated);


		var marker = L.marker([coord[i].lat, coord[i].lon]);
		marker.setIcon(choose_marker(coord[i].status));

		marker.on('click', function(e){
		
			var latlng = JSON.stringify(e.latlng);
			var obj = $.parseJSON('[' + latlng + ']');
			var lat = JSON.stringify(obj[0].lat);
			var lon = JSON.stringify(obj[0].lng);
		
			sel = 0;
			for(j=0; j<labels.length; j++){
				if(latitude[j]==lat && longitude[j]==lon){
					sel = j;
					break;
				}
			}
		
			var img = '<img src="'+images_url+'blue-circle.png" width=10 height=10>';
			if(statuses[sel] == "online")
				img = '<img src="'+images_url+'green-circle.png" width=10 height=10>';
			if(statuses[sel] == "offline")
				img = '<img src="'+images_url+'red-circle.png" width=10 height=10>';

			var open_popup = '<div>';

			var default_popup = '<center>'+img +' <b>'+labels[sel]+'</b></center><br />' +
				'<center><b>'+last_update[sel]+'</b></center><br />'+
				'Latitude: <b>'+latitude[sel]+ '</b><br />' +
				'Longitude: <b>'+longitude[sel]+'</b><br />' +
				'Altitude: <b>'+altitude[sel]+'</b><br /><br />';

			global_popup = open_popup + default_popup +"</div>";
			var popup = L.popup().setLatLng(e.latlng).setContent(global_popup).openOn(map);
		});
		markers.addLayer(marker);
	}
	map.addLayer(markers);
	//return map;
}



function choose_marker(status){
	if(status=="online") return marker_green;
	else if(status =="offline") return marker_red;
	else return marker_blue;
}
