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
  getTrain: function(id) {
    return $.getJSON('/api/train/' + id);
  }
};

$(function main() {
  RD.map = L.map('map').setView([51.505, -0.09], 13);
  L.tileLayer('http://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, &copy; <a href="http://cartodb.com/attributions">CartoDB</a>'
  }).addTo(RD.map);

  RD.Api.getMovements().done(function(movements) {
    console.log('got movements:', movements);
    _.each(movements, function(mvt) {
        console.log('adding mvt id', mvt.id);
        if (!mvt.loc_geo) { return; }
        var thePopup = L.popup().setContent('Train with ID ' + mvt.train_id + ': ' + mvt.variation_status + ' ' + mvt.event_type + ' at ' + mvt.loc_name);
        L.marker(L.latLng(mvt.loc_geo.coordinates[1], mvt.loc_geo.coordinates[0])).bindPopup(thePopup).addTo(RD.map);
      });
  });
});
