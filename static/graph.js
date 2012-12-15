function plot_chart(areaname, xlabels, dataseries, prev_xlabels) {
    var chart = nv.models
        .stackedAreaChart()
        .tooltipContent(function(key, x, y, e, graph) {
            return '<h5>' + key + ': ' + y + ' </h5>' +'<p>' + xlabels[e.pointIndex] + '</p>' ;
        })
        .showLegend(true)
        .showControls(false);

    chart.x(function(d, i) { return i });
    chart.xAxis
        .tickFormat(function(d) { return xlabels[d] });


    d3.select('#' + areaname + ' svg')
      .datum(dataseries)
      .transition().duration(500)
      .call(chart);

    nv.utils.windowResize(chart.update);

    return chart;
};



function plot_monthly_chart(areaname, xlabels, dataseries) {
    var chart = nv.models.lineChart()
    .tooltipContent(function(key, x, y, e, graph) {
        return '<h5>' + key + ': ' + y + ' </h5>' +'<p>' + xlabels[e.pointIndex] + '</p>' ;
    });

    chart.x(function(d, i) { return i });
    chart.xAxis
        .tickFormat(function(d) { return xlabels[d] });


    d3.select('#' + areaname + ' svg')
      .datum(dataseries)
      .transition().duration(500)
      .call(chart);

    nv.utils.windowResize(chart.update);

    return chart;
};


// run the currently selected effect
function runToggle(id) {
    // run the effect
    $(id).toggle("blind", "", 500);
};
