$(function () {
//
//
//
function replot() {
    var plot_area = $('#plot_area');
    var SNR_area = $('#SNR_area')
    var plot_options = {
        "legend": {
            "show": false
        },
        "selection": {
            "mode": "xy"
        },
        "axisLabels": {
            "show": true
        },
        "xaxis": xlim,
        "yaxis": ylim,
        "xaxes": [{
            "axisLabel": "MJD &ndash; " + mjd_zero
        }],
        "yaxes": [{
            "axisLabel": "Heliocentric Velocity [km/s]"
        }],
        "pan": {
            "interactive": true
        },
        "zoom": {
            "interactive": true
        }
    };
    var SNR_options = {
        "legend": {
            "show": false
        },
        "selection": {
            "mode": "xy"
        },
        "axisLabels": {
            "show": true
        },
        "xaxis": xlim,
        "xaxes": [{
            "axisLabel": "MJD &ndash; " + mjd_zero
        }],
        "yaxes": [{
            "axisLabel": "Signal/Noise"
        }]
    };
    var plot = $.plot(plot_area, rv, plot_options);
    var plot2 = $.plot(SNR_area, snr, SNR_options);
    $("#calc").html("");
}
//
//
//
function onDataReceived(data) {
    rv = [
        {
            "data": [],
            "color": "black",
            "points": {
                "show": true,
                "radius": 0,
                "errorbars": "y",
                "yerr": {
                    "show": true,
                    "upperCap": "-",
                    "lowerCap": "-",
                    "radius": 2
                }
            },
            "lines": {"show": false}
        },
        {
            "data": data.fit1,
            "color": "red",
            "points": {"show": false},
            "lines": {"show": true}
        },
        {
            "data": data.fit2,
            "color": "red",
            "points": {"show": false},
            "lines": {"show": false},
            "dashes": {"show": true}
        },
        {
            "data": [[data.mjd[0], data.vhelio_avg], [data.mjd[data.mjd.length-1], data.vhelio_avg]],
            "color": "blue",
            "points": {"show": false},
            "lines": {"show": true}
        },
        {
            "data": [[data.mjd[0], data.vhelio_avg-data.vscatter], [data.mjd[data.mjd.length-1], data.vhelio_avg-data.vscatter]],
            "color": "blue",
            "points": {"show": false},
            "lines": {"show": false},
            "dashes": {"show": true}
        },
        {
            "data": [[data.mjd[0], data.vhelio_avg+data.vscatter], [data.mjd[data.mjd.length-1], data.vhelio_avg+data.vscatter]],
            "color": "blue",
            "points": {"show": false},
            "lines": {"show": false},
            "dashes": {"show": true}
        }
    ];
    snr = [
        {
            "data": [],
            "color": "black",
            "points": {"show": true},
            "lines": {"show": false}
        }
    ];
    xlim = {"min":99999, "max":-99999, "panRange":[0,0], "zoomRange":[0.1,10]};
    ylim = {"min":99999, "max":-99999, "panRange":[0,0], "zoomRange":[0.1,10]};
    for (var i=0; i<data.mjd.length; i++) {
        if (data.mjd[i] < xlim.min) xlim.min = data.mjd[i];
        if (data.mjd[i] > xlim.max) xlim.max = data.mjd[i];
        var m = data.vhelio[i]-data.vrelerr[i];
        if (m < ylim.min) ylim.min = m;
        m = data.vhelio[i]+data.vrelerr[i];
        if (m > ylim.max) ylim.max = m;
        rv[0].data.push([data.mjd[i],data.vhelio[i],data.vrelerr[i]]);
        snr[0].data.push([data.mjd[i],data.snr[i]])
    }
    xlim.min = xlim.min - 5;
    xlim.max = xlim.max + 5;
    xlim.panRange[0] = xlim.min - 5;
    xlim.panRange[1] = xlim.max + 5;
    ylim.min = ylim.min - 0.5;
    ylim.max = ylim.max + 0.5;
    ylim.panRange[0] = ylim.min - 1.0;
    ylim.panRange[1] = ylim.max + 1.0;
    mjd_zero = data.mjd_zero;
}
//
//
//
function load_data() {
    $("#calc").html("Calculating...");
    var title = $("h1:first").text();
    var m = title.match(/(\d+)\.(2M\d+[+-]\d+)/i);
    if (m !== null) {
        Q = $("#Q").val();
        var url = "/" + m[1] + "/" + m[2] + "/" + Q;
        $.getJSON(url,{},onDataReceived).error(function(){alert("JSON error!");}).complete(replot);
    }
}
//
// "Global" variables.
//
var rv = [];
var snr = [];
var xlim = null;
var ylim = null;
var mjd_zero = 0;
var Q = 0;
if (rv.length == 0) {
    load_data();
}
//
// Run load_data when Q changes.
//
$("#Q").change(load_data);
//
// Add zoom out event.
//
$("#unzoom").click(function (event) { event.preventDefault(); replot(); });
});
