/* eslint-env jquery, browser */

// Global namespace for the project
/* global RD:true */
window.RD = {};

/* global L */

RD.Api = {
  getMovements: function(page, type) {
    page = page || 0;
    options = {};
    if (type) { options.type = type; }
    return $.getJSON('/api/movements/' + page, options);
  },
  getMovementsGeo: function(geo, page) {
    page = page || 0;
    return $.getJSON('/api/movements_geo/' + geo + '/' + page);
  },
  getTrain: function(id) {
    return $.getJSON('/api/train/' + id);
  }
};

function getMovementsInView() {
  var viewBounds = RD.map.getBounds();
  var nw = viewBounds.getNorthWest();
  var sw = viewBounds.getSouthWest();
  var se = viewBounds.getSouthEast();
  var ne = viewBounds.getNorthEast();
  var viewBoundsParam = _.map([nw, sw, se, ne], function(pt) {
    return [pt.lng, pt.lat].join();
  }).join(':');
  return RD.Api.getMovementsGeo(viewBoundsParam);
}

function displayMovements(movements) {
  var markers = _.map(_.filter(movements, function(mvt) {
    return mvt.loc_geo;
  }), function(mvt) {
    var thePopup = L.popup().setContent('Train with ID ' + mvt.train_id + ': ' + mvt.variation_status + ' ' + mvt.event_type + ' at ' + mvt.loc_name);
    var theMarker = L.marker(L.latLng(mvt.loc_geo.coordinates[1], mvt.loc_geo.coordinates[0]));
    theMarker.bindPopup(thePopup);
    return theMarker;
  });
  if (RD.layerGroup) {
    RD.map.removeLayer(RD.layerGroup);
  }
  RD.layerGroup = L.layerGroup(markers);
  RD.map.addLayer(RD.layerGroup);
}

function updateView() {
  RD.layerGroup = null;
  setInterval(function() {
    getMovementsInView().done(displayMovements);
  }, 10000);
}

$(function main() {
  RD.map = L.map('map').setView([51.505, -0.09], 10);
  L.tileLayer('http://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, &copy; <a href="http://cartodb.com/attributions">CartoDB</a>'
  }).addTo(RD.map);

  updateView();
  RD.map.on('moveend', function() {
    getMovementsInView().done(displayMovements);
  })
});
