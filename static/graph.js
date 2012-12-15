function plot_chart(areaname, graphtitle, ylegend, dataseries) {
    var chart = new Highcharts.Chart({
        chart: {
            renderTo: areaname,
            type: 'area'
        },
        title: {
            text: graphtitle
        },
        xAxis: {
            type: 'datetime'
        },
        yAxis: {
            title: {
                text: ylegend
            }
        },
        plotOptions: {
            area: {
                marker: {
                    enabled: false,
                    symbol: 'circle',
                    radius: 2,
                    states: {
                        hover: {
                            enabled: true
                        }
                    }
                }
            }
        },
        series: dataseries,
    });
};

function plot_monthly_chart(areaname, graphtitle, xlabels, dataseries,
show_labels) {
    var chart = new Highcharts.Chart({
        chart: {
            renderTo: areaname,
            type: 'line'
        },
        title: {
            text: graphtitle
        },
        xAxis: {
            categories: xlabels,
            labels : {
                enabled : show_labels
            }
        },
        plotOptions: {
            line: {
                    dataLabels: {
                        enabled: false
                    },
                    enableMouseTracking: true,
                    marker: {
                        enabled: false,
                        symbol: 'circle',
                        radius: 2,
                        states: {
                            hover: {
                                enabled: true
                            }
                        }
                    }
                }
        },
        series: dataseries
    });
};


// run the currently selected effect
function runToggle(id) {
    // run the effect
    $(id).toggle("blind", "", 500);
};
