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
