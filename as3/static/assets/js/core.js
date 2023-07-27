function plot_heat_map(top_performer, result_data, id_) {
    let data_arr = []
    const company_name = $("#page-header").attr("cname");
    data_arr.push([])
    data_arr.push([])
    for (var i = 0; i < 3; i++) {
        let inner_dat = []
        for (var j = 100; j >= 30; j--) {
            inner_dat.push(j)
        }
        data_arr.push(inner_dat)
    }

    var xlabels = []

    for (var i = 30; i <= 100; i++) {
        // if(i%10 == 0)
        xlabels.push(`${i}`)
        // else
        //     xlabels.push(``)
    }

    let language = window.localStorage.getItem("language")
    if (!language) {
        language = "en"
        window.localStorage.setItem(key = "language", value = language);
    }
    if (language === "en") {
        var lsav = "Low-Stress Average"
        var hsav = "High-Stress Average"
        var yts = "Your Top Student"
        var glsav = "Global Low-Stress Average"
        var ghsav = "Global High-Stress Average"
        var pp = "Performance"
        var fe = "% of Final Exercise"
    } else if (language === "es") {
        var lsav = "Promedio Estrés Bajo"
        var hsav = "Promedio Estrés Alto"
        var yts = "Su Mejor Conductor"
        var glsav = "Promedio Global Estrés Bajo"
        var ghsav = "Promedio Global Estrés Alto"
        var pp = "Desempeño"
        var fe = "% del Ejercicio Final"
    }

    var data = [{
        z: data_arr,
        colorscale: 'Portland',
        type: 'heatmap',
        x: xlabels,
        showscale: false,
    }];
    var layout = {
        hovermode: false,
        title: '',
        font: {
            family: 'Poppins',
            // size: 12.5,
            color: 'black'
        },
        xaxis: {
            ticks: '',
            title: `${pp} (${fe})`,
            // side: 'top'
            showgrid: false,
            zeroline: false,
            showline: false,
            autotick: true,
            range: [30, 100]
        },
        yaxis: {
            showgrid: false,
            zeroline: false,
            showline: false,
            // ticks: '',
            showticklabels: false,
            ticks: '',
            ticksuffix: ' ',
        },
        height: 250,
        shapes: [{
                type: 'circle',
                xref: 'x',
                yref: 'y',
                x0: Math.floor(result_data.global.hs) - 0.25,
                y0: 2,
                x1: Math.floor(result_data.global.hs) + 0.25,
                y1: 4,
                fillcolor: 'red',
                line: {
                    color: 'red'
                }
            },
            {
                type: 'circle',
                xref: 'x',
                yref: 'y',
                x0: Math.floor(result_data.global.ls) - 0.25,
                y0: 2,
                x1: Math.floor(result_data.global.ls) + 0.25,
                y1: 4,
                fillcolor: 'green',
                line: {
                    color: 'green'
                }
            },
            {
                type: 'line',
                x0: Math.floor(result_data.qs.ls),
                y0: 1.5,
                x1: Math.floor(result_data.qs.ls),
                y1: 4.5,
                line: {
                    color: 'darkblue',
                    width: 4,
                    dash: 'dashdot'
                }
            },
            {
                type: 'line',
                x0: Math.floor(result_data.qs.hs),
                x1: Math.floor(result_data.qs.hs),
                y0: 1.5,
                y1: 4.5,
                line: {
                    color: 'red',
                    width: 4,
                    dash: 'dashdot'
                }
            },

        ],
        annotations: [{
                axref: 'x',
                ayref: 'y',
                x: Math.floor(result_data.qs.ls) + 0, // 1.5
                y: 4.5, // 5.3
                ax: Math.floor(result_data.qs.ls),
                ay: 5.9,
                textangle: 0, // -7
                text: `<i><b>${lsav}</b></i>`,
                showarrow: true,
                arrowcolor: "blue",
                font: {
                    color: "blue",
                    size: 11
                },
                textposition: 'bottom',
            },
            {
                axref: 'x',
                ayref: 'y',
                x: Math.floor(result_data.qs.hs) + 0, // 1.5
                y: 4.5, // 5.3
                ax: Math.floor(result_data.qs.hs),
                ay: 7,
                textangle: 0, // -7
                text: `<i><b>${hsav}</b></i>`,
                showarrow: true,
                arrowcolor: "red",
                font: {
                    color: "red",
                    size: 11
                },
                textposition: 'bottom',
            },

            {
                axref: 'x',
                ayref: 'y',
                x: Math.floor(result_data.global.ls),
                y: 1.5,
                ax: Math.floor(result_data.global.ls),
                ay: 0.1,
                text: `<i><b>${glsav}</b></i>`,
                showarrow: true,
                arrowcolor: "green",
                font: {
                    color: "black",
                    size: 11
                },
                textposition: 'bottom',
            },
            {
                axref: 'x',
                ayref: 'y',
                x: Math.floor(result_data.global.hs),
                y: 1.5,
                ax: Math.floor(result_data.global.hs),
                ay: -0.5,
                text: `<i><b>${ghsav}</b></i>`,
                showarrow: true,
                arrowcolor: "red",
                font: {
                    color: "black",
                    size: 11
                },
                textposition: 'bottom',
            },
            {
                ayref: 'y',
                axref: 'x',
                ax: Math.floor(result_data.qs.max),
                x: Math.floor(result_data.qs.max),
                y: 4.5,
                ay: 8, //5.55,
                textangle: 0,
                text: `<i><b>${yts}:<br>${top_performer}</b></i>`,
                showarrow: true,
                arrowcolor: "rgb(131,6,2)",
                font: {
                    color: "rgb(131,6,2)",
                    size: 11
                },
                marker: {
                    color: "red"
                }
            },
        ],

        margin: {
            l: 8,
            r: 20,
            b: 40,
            t: 0,
        }
    };
    let config = {
        responsive: true,
        editable: false,
        staticPlot: true
    }
    Plotly.newPlot(id_, data, layout, config);
}


function plot_performers_chart(performer, plot_id, type_) {
    const xaxis = performer.map(function (el) {
        let name = `${el["first_name"]} ${el["last_name"]}`
        return name;
    })
    const final_result = performer.map(function (el) {
        return el["final_result"];
    });

    var language = window.localStorage.getItem("language")
    if(language == "es"){
        var perfss = "Desempeño"
        if(type_ === "Low") type_ = "Bajo"
        else    type_ = "Alto"
        var cos = "Control Sobre Slalom"
        var cob = "Control Sobre Barricada"
    }
    else{
        var perfss = "Performers"
        var cos = "Control over Slalom"
        var cob = "Control over Barricade"
    }

    let trace1 = {
        x: xaxis,
        y: performer.map(function (el) {
            return 0;
        }),
        marker: {
            color: "rgb(139,0,0)"
        },
        name: `${type_} ${perfss}`,
        type: "bar",
    }

    let trace2 = {
        x: xaxis,
        y: performer.map(function (el) {
            return el["slalom"];
        }),
        marker: {
            color: "rgb(65,105,225)"
        },
        name: cos,
    }

    let trace3 = {
        x: xaxis,
        y: performer.map(function (el) {
            return el["lane_change"];
        }),
        marker: {
            color: "rgb(0,191,191)"
        },
        name: cob,
    }

    let trace4 = {
        x: xaxis,
        y: performer.map(function (el) {
            return 80;
        }),
        text: final_result.map(String),
        textposition: 'auto',
        line: {
            dash: 'dot',
            width: 4
        },
        marker: {
            color: "rgb(200,120,103)"
        },
        yref: "paper",
        type: "line",
        color: "#C87867",
        mode: 'lines',
        showlegend: false,
    }
    var layout = {
        yaxis: {
            range: [10, 110],
        },
        legend: {
            x: 1,
            xanchor: 'right',
            y: 1,
            orientation: "h"
        },
        font: {
            family: 'Poppins',
            size: 12.5,
            color: 'black'
        },
        margin: {
            l: 25,
            r: 75,
            b: 130,
            t: 0
        }
    }
    let config = {
        responsive: true,
        editable: false,
        staticPlot: true
    }
    Plotly.newPlot(plot_id, [trace1, trace2, trace3, trace4], layout, config);
    randomize_performers_chart(plot_id, xaxis, final_result)
}

function randomize_performers_chart(plot_id, x_axis, final_result) {
    Plotly.animate(plot_id, {
        data: [{
            x: x_axis,
            y: final_result,
        }],
        traces: [0],
        layout: {}
    }, {
        transition: {
            duration: 1000,
            easing: 'cubic-in-out'
        },
        frame: {
            duration: 500
        }
    })
}



function performer_averages_on_success(res, orignal = true) {
    if (orignal) window.localStorage.setItem(`averages-response-${$("#page-header").attr("data-id")}`, JSON.stringify(res));
    plot_heat_map(res.qs.top_student, res, 'heatmap-plot');
    $("#card_total_students_count").html(res.qs.total_students)
    $("#card_total_pass_count").html(res.qs.pass_count)
    $("#card_total_courses_count").html(res.qs.total_courses)
    // $("#card_total_courses_count").html(res.qs.total_courses)
}

function student_performers_on_success(res, orignal = true) {
    let students = res.items
    students.sort((a, b)=>{return b.final_result-a.final_result})
    if (orignal) window.localStorage.setItem(`students-api-response-${$("#page-header").attr("data-id")}`, JSON.stringify({items: students}));
    populate_students_table(res);
    populate_performers_activity(res);
    perf_scatter_plt_on_success(res);
}

$("#download_global_report_btn").click(function (e) {
    e.preventDefault(); // stops the default action
    const url = $(this).attr("data-url").replace(/ /g,'');
    let is_filter_apply = $("#filter-report-checkbox-id").is(':checked')
    var filters_tosent = window.localStorage.getItem(`as3-filters-${$("#page-header").attr("data-id")}`)
    //$("#loader").show(); // shows the loading screen
    if (!filters_tosent || !is_filter_apply){
        filters_tosent = {
            "groups": '',
            "teams": '',
            "locations": '',
            "programs": '',
            "start_date": '', // start.unix(),
            "end_date": '', // end.unix(),
        }
    }else{
        filters_tosent = JSON.parse(filters_tosent)
    }
    filters_tosent.language = window.localStorage.getItem(`language`).toUpperCase()
    console.log(url, filters_tosent)
    global_company_report_download(url, filters_tosent)
});
