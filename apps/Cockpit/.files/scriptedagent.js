/* global _ */
/*
 * Complex scripted dashboard
 * This script generates a dashboard object that Grafana can load. It also takes a number of user
 * supplied URL parameters (in the ARGS variable)
 *
 * Return a dashboard object, or a function
 *
 * For async scripts, return a function, this function must take a single callback function as argument,
 * call this callback function with the dashboard object (look at scripted_async.js for an example)
 */

'use strict';

// accessible variables in this scope
var window, document, ARGS, $, jQuery, moment, kbn;

// Setup some variables
var dashboard;

// All url parameters are available via the ARGS object
var ARGS;

// Intialize a skeleton with nothing but a rows array and service object
dashboard = {
  rows : [],
  refresh: '5s',
};

// Set a title
dashboard.title = 'Scripted dash';

// Set default time
// time can be overriden in the url using from/to parameters, but this is
// handled automatically in grafana core during dashboard initialization
dashboard.time = {
  from: "now-6h",
  to: "now"
};

var series = [];

if(!_.isUndefined(ARGS.series)) {
  series = ARGS.series.split(',');
}


dashboard.rows.push({
    panels: [
{
  "aliasColors": {},
  "bars": false,
  "datasource": 'influxdb_main',
  "editable": true,
  "error": false,
  "fill": 1,
  "grid": {
    "leftLogBase": 1,
    "leftMax": null,
    "leftMin": null,
    "rightLogBase": 1,
    "rightMax": null,
    "rightMin": null,
    "threshold1": null,
    "threshold1Color": "rgba(216, 200, 27, 0.27)",
    "threshold2": null,
    "threshold2Color": "rgba(234, 112, 112, 0.22)"
  },
  "hideTimeOverride": false,
  "id": 1,
  "isNew": true,
  "legend": {
    "avg": false,
    "current": false,
    "max": false,
    "min": false,
    "show": true,
    "total": false,
    "values": false
  },
  "lines": true,
  "linewidth": 2,
  "links": [],
  "nullPointMode": "connected",
  "percentage": false,
  "pointradius": 5,
  "points": false,
  "renderer": "flot",
  "seriesOverrides": [],
  "span": 12,
  "stack": false,
  "steppedLine": false,
  "targets": series.map(function(x){return {
      "dsType": "influxdb",
      "groupBy": [
        {
          "params": [
            "auto"
          ],
          "type": "time"
        },
        {
          "params": [
            "null"
          ],
          "type": "fill"
        }
      ],
      "hide": false,
      "measurement": x,
      "query": 'SELECT "value" FROM "'+x+'"',
      "rawQuery": true,
      "refId": "A",
      "resultFormat": "time_series",
      "select": [
        [
          {
            "params": [
              "value"
            ],
            "type": "field"
          },
          {
            "params": [],
            "type": "mean"
          }
        ]
      ],
      "tags": []
    }
  }),
  "timeFrom": null,
  "timeShift": null,
  "title": "Panel Title",
  "tooltip": {
    "shared": true,
    "value_type": "cumulative"
  },
  "type": "graph",
  "x-axis": true,
  "y-axis": true,
  "y_formats": [
    "short",
    "short"
  ]
}
    ]
});


return dashboard;
