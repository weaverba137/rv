$(function () {
//
//
//
function replot() {
    var plot_area = $('#plot_area');
    var SNR_area = $('#SNR_area')
    var plot_options = {
        "grid": {
            "hoverable": true,
            "clickable": true
        },
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
    var a1 = Math.sqrt(fit1_param[1]*fit1_param[1] + fit1_param[2]*fit1_param[2]);
    var a2 = Math.sqrt(fit2_param[1]*fit2_param[1] + fit2_param[2]*fit2_param[2]);
    var phi1 = 180.0*Math.atan2(fit1_param[2],fit1_param[1])/Math.PI;
    var phi2 = 180.0*Math.atan2(fit2_param[2],fit2_param[1])/Math.PI;
    var T1 = 2.0*Math.PI/fit1_param[3];
    var T2 = 2.0*Math.PI/fit2_param[3];
    $("#fit1v").html(fit1_param[0].toFixed(2));
    $("#fit1A").html(a1.toFixed(2));
    $("#fit1B").html(phi1.toFixed(2));
    $("#fit1T").html(T1.toFixed(2));
    $("#fit2v").html("("+fit2_param[0].toFixed(2)+")");
    $("#fit2A").html("("+a2.toFixed(2)+")");
    $("#fit2B").html("("+phi2.toFixed(2)+")");
    $("#fit2T").html("("+T2.toFixed(2)+")");
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
                // "radius": 0,
                "errorbars": "y",
                "yerr": {
                    "show": true,
                    "upperCap": "-",
                    "lowerCap": "-",
                    "radius": 2
                },
            },
            "lines": {"show": false}
        },
        {
            "data": data.fit1,
            "color": "red",
            "points": {"show": false},
            "lines": {"show": true},
            "shadowSize": 0
        },
        {
            "data": data.fit2,
            "color": "red",
            "points": {"show": false},
            "lines": {"show": false},
            "dashes": {"show": true},
            "shadowSize": 0
        },
        {
            "data": [[data.mjd[0], data.vhelio_avg], [data.mjd[data.mjd.length-1], data.vhelio_avg]],
            "color": "blue",
            "points": {"show": false},
            "lines": {"show": true},
            "shadowSize": 0
        },
        {
            "data": [[data.mjd[0], data.vhelio_avg-data.vscatter], [data.mjd[data.mjd.length-1], data.vhelio_avg-data.vscatter]],
            "color": "blue",
            "points": {"show": false},
            "lines": {"show": false},
            "dashes": {"show": true},
            "shadowSize": 0
        },
        {
            "data": [[data.mjd[0], data.vhelio_avg+data.vscatter], [data.mjd[data.mjd.length-1], data.vhelio_avg+data.vscatter]],
            "color": "blue",
            "points": {"show": false},
            "lines": {"show": false},
            "dashes": {"show": true},
            "shadowSize": 0
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
    fit1_param = data.fit1_param;
    fit2_param = data.fit2_param;
    visits = data.visits;
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
//
//
function showTooltip(item) {
    // var contents, id, tooltip_css;
    // id = this.getID(item.seriesIndex, item.dataIndex);
    // contents = "" + (this.getName(id)) + " (" + (this.formatPosition(id)) + ")";
    var contents = "Time: " + item.datapoint[0].toFixed(2) + " d<br/>RV: " +
        item.datapoint[1].toFixed(2) + " &pm; " +
        item.datapoint[2].toFixed(2) + " km/s<br/>Visit: " +
        visits[item.dataIndex];
    var tooltip_css = {
        position: 'absolute',
        display: 'none',
        top: item.pageY + 5,
        left: item.pageX + 5,
        border: '1px solid gray',
        padding: '2px',
        "background-color": 'silver',
        opacity: 0.8
    };
    $("<div id=\"hovertip\"/>").html(contents).css(tooltip_css).appendTo('body').fadeIn(200);
}
//
//
//
function handle_hover(event, pos, item) {
    if (item) {
        if (item.seriesIndex == 0) {
            if (previousPoint != item.dataIndex) {
                $('#hovertip').remove();
                showTooltip(item);
                previousPoint = item.dataIndex;
            }
        }
    } else {
        $('#hovertip').remove();
        previousPoint = null;
    }
}
//
//
//
function handle_click(event, pos, item) {
    if (item) {
        if (item.seriesIndex == 0) {
            var visitId = visits[item.dataIndex];
            var m = visitId.match(/apogee\.([^.]+)\.([^.]+)\.([^.]+)\.([^.]+)\.([^.]+)\.([^.]+)/);
            if (m !== null) {
                var url = "http://data.sdss3.org/irSpectrumDetail?plateid=" +
                    m[4] + "&mjd=" + m[5] + "&fiber=" + m[6];
                // alert(url);
                window.open(url);
            }
        }
    }
}
//
// "Global" variables.
//
var rv = [];
var snr = [];
var visits = [];
var xlim = null;
var ylim = null;
var mjd_zero = 0;
var Q = 0;
var fit1_param = [];
var fit2_param = [];
var previousPoint = null;
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
$("#plot_area").bind("plothover", handle_hover);
$("#plot_area").bind("plotclick", handle_click);
$("#unzoom").click(function (event) { event.preventDefault(); replot(); });
});
