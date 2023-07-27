function scatter_plot(res) {
    let items = res["items"];
    const final_result = items.map(function (el) {
        return el["final_result"];
    })
    const control = items.map(function (el) {
        return Math.floor((el["slalom"] + el["lane_change"]) / 2);
    });
    const students = items.map(function (el) {
        return `${el["first_name"]} ${el["last_name"]}`;
    });
    const penalties = items.map(function (el) {
        return el["penalties"];
    });
    const reverse = items.map(function (el) {
        return el["reverse"] * 1.5;
    });
    var textAnnotations = []

    for(var i = 0; i < students.length; i++){
        textAnnotations.push({
            x: control[i] - 1,
            y: final_result[i] + 1.5,
            xref: 'x',
            yref: 'y',
            text: `${students[i]}`,
            showarrow: false,
            font: {
              color: '#000000'
            },
            textangle: 15,
            align: 'center',
            // arrowhead: 2,
            // arrowsize: 1,
            // arrowwidth: 2,
            // arrowcolor: '#636363',
            // ax: 20,
            // ay: -30,
            bordercolor: '#c7c7c7',
            borderwidth: 2,
            borderpad: 4,
            bgcolor: '#FFFFB2',
            opacity: 0.8
        })
    }

    var language = window.localStorage.getItem("language")
    if(language == "es"){
        var gcs = "Mayor Control / Habilidad"
        var fd = "Conductor Más Rápido"
        var sdb = "Balance de Conductor<br> de Seguridad"
        var oc = "% de Control"
        var oe = "% del Ejercicio"
        var p_text = "Penalizaciones"
        var rev_text = "Reversa"

    }
    else{
        var gcs = "Greater Control/Skill"
        var fd = "Faster Driver"
        var sdb = "Security Driver<br> Balance"
        var oc = "% Of Control"
        var oe = "% of the exercise"
        var p_text = "Penalties"
        var rev_text = "Reverse"

    }

    let otherAnnotations = [
        {
            showarrow: false,
            text: gcs,
            x: 80,
            y: 74,
            font: {
                size: 18,
                color: 'grey',
            }
        },
        {
            showarrow: false,
            text: fd,
            align: "true",
            x: 35,
            y: 99,
            font: {
                size: 18,
                color: 'grey',
            }
        },
        {
            showarrow: false,
            text: sdb,
            align: "true",
            x: 80,
            y: 90,
            font: {
                size: 14,
                color: 'grey',
            }
        },
        {
            axref: 'x',
            ax: 34.25,

            aref: 'x',
            x: 87.5,

            ayref: 'y',
            ay: 73,

            aref: 'y',
            y: 73,
            line: {
                "dash": "dot"
            },
            arrowhead: 1.5,
            opacity: 0.6,
        },
        {
            axref: 'x',
            ax: 34.5,

            aref: 'x',
            x: 34.5,

            ayref: 'y',
            ay: 72.5,

            aref: 'y',
            y: 97.5,
            arrowhead: 1.5,
            opacity: 0.6,
        }
    ]

    var scl = [
        [0, 'rgb(51,24,74)'],
        [0.25, 'rgb(71,113,233)'],
        [0.5, 'rgb(32,234,172)'],
        [0.6, 'rgb(205,236,52)'],
        [0.7, 'rgb(244,102,23)'],
        [1, 'rgb(131,6,2)']
    ];
    var textInfo = []
    for(var i = 0; i< students.length; i++){
        textInfo.push(`<b>${students[i]}</b> <br>${p_text}: ${penalties[i]} <br>${rev_text}: ${reverse[i]}`)
    }
    var trace1 = {
        x: control,
        y: final_result,
        mode: 'markers',
        type: 'scatter',
        text: textInfo,
        textfont: {
            size: 14, 
        },
        showlegend: false,
        hovertemplate:
            `<b>%{text}</b>` + 
            '<br>Control expressed in %: %{x}' +
            `<br>Final Result for % of the exercise: %{y}<br>` +
            `<extra></extra>`,
        marker: {
            size: reverse,
            color: penalties,
            colorscale: scl,
            cmin: 0,
            colorbar: {
                title: p_text
            }
        }
    };
    var height = 650;
    var win_width = $(window).width();
    if(win_width >= 1400 && win_width < 1800)
        height = 500;
    if(win_width >= 1200 && win_width < 1400)
        height = 580;
    if(win_width >= 900 && win_width < 1200)
        height = 540;
    if(win_width >= 500 && win_width < 900)
        height = 480;
    if(win_width < 500)
        height = 300;

    var data = [trace1];
    var annotations = otherAnnotations.concat(textAnnotations)
    var layout = {
        autosize: true,
        height: height,
        xaxis: {
            range: [30, 90],
            automargin: true,
            title: {
                text: oc,
                standoff: 20
            },
            zeroline: false,
            showgrid: false,
        },
        font: {
            family: 'Poppins',
            size: 12.5,
            color: 'black'
        },
        yaxis: {
            range: [70, 100],
            automargin: true,
            title: {
                text: oe,
                standoff: 20
            },
            zeroline: false,
            showgrid: false,
        },
        shapes: [{
            type: 'rect',
            x0: 70,
            y0: 80,
            x1: 90,
            y1: 98,
            layer: "below",
            line: {
                color: 'rgba(222, 184, 184, 1)',
                width: 3,
                dash: "dot",
            },
            fillcolor: 'rgba(245, 245, 245, 0.4)',
            label: sdb,
        }],
        legend: {
            y: 0.5,
            yref: 'paper',
            font: {
                size: 20,
                color: 'grey',
            }
        },
        // title: 'Scatter Plot',
        annotations: annotations
    };

    let config = {
        responsive: true,
        editable: false,
        // staticPlot: true
    }
    Plotly.newPlot('control-performance-plot', data, layout, config);
}

function final_excercise_table_populate(res){
    var container = $('#control-performance-table .pagination')
    var total_length = res.items.length;
    if(total_length == 0)   return false;
    var page_size = 6;
    var html = get_final_excercise_table_data(res.items.slice(0, page_size))

    $("#control-performance-table .table").html(html);
    set_language_strings()

    container.pagination({
        dataSource: res.items,
        showPageNumbers: false,
        showNavigator: true,
        showFirstOnEllipsisShow: false,
        className: 'paginationjs-theme-grey paginationjs',
        pageSize: page_size,
        pageRange: 1,
        callback: function (data, pagination) {
            let start = (pagination.pageNumber - 1) * page_size;
            let end = (pagination.pageNumber) * page_size;
            if (total_length < end) end = total_length
            var html = get_final_excercise_table_data(res.items.slice(start, end))
            $("#control-performance-table .table").html(html);
            set_language_strings()
        }
    })

}

function get_final_excercise_table_data(items){
    var rows = "";
    for(var i = 0; i < items.length; i++){
        rows += `<tr>
            <td class="col-auto">
                ${items[i].first_name} ${items[i].last_name}
            </td>
            <td class="col-auto text-center">
                ${items[i].final_result}
            </td>
            <td class="col-auto text-center">
                ${parseInt((items[i].slalom + items[i].lane_change) / 2)}
            </td>
            <td class="col-auto text-center col-sm-2 col-xs-2 col-md-2 col-xl-2 col-xxl-2">
                ${items[i].reverse}
            </td>
            <td class="col-auto text-center col-sm-2 col-xs-2 col-md-2 col-xl-2 col-xxl-2">
                ${items[i].penalties}
            </td>
        </tr>`
    }

    return (`<table class="table table-responsive">
            <thead>
                <tr>
                <th class="col-sm-5 col-xs-5 col-md-5 col-xl-5 col-xxl-5">
                <span class="language-en">FULL NAME</span>
                <span class="language-es">NOMBRE COMPLETO</span>
                </th>
                <th class="col-sm-2 col-xs-2 col-md-2 col-xl-2 col-xxl-2 text-center">
                <span class="language-en">FINAL RESULT (%)</span>
                <span class="language-es">RESULTADO FINAL (%)</span>
                </th>
                <th class="col-sm-1 col-xs-1 col-md-1 col-xl-1 col-xxl-1 text-center">
                <span class="language-en">CONTROL(%)</span>
                <span class="language-es">CONTROL(%)</span>
                </th>
                <th class="col-sm-2 col-xs-2 col-md-2 col-xl-2 col-xxl-2 text-center">
                <span class="language-en">REVERSE(%)</span>
                <span class="language-es">REVERSA (%)</span>
                </th>
                <th class="col-sm-2 col-xs-2 col-md-2 col-xl-2 col-xxl-2 text-center">
                <span class="language-en">PENALTIES</span>
                <span class="language-es">PENALIZACIONES</span>
                </th>
                </tr>
            </thead>
            <tbody>
                ${rows}
            </tbody>
        </table>`)
}

function perf_scatter_plt_on_success(scatter_perf_data, orignal = true) {
    if(orignal)
        window.localStorage.setItem(`scatter-perf-${$("#page-header").attr("data-id")}`, JSON.stringify(scatter_perf_data))
    scatter_plot(scatter_perf_data);
    final_excercise_table_populate(scatter_perf_data);
    set_language_strings();
}

function perf_scatter_plt_on_error(response) {
    console.log(response, "err")
}

$("#final-exercise-activity-tab").click(function(){
    setTimeout(
        function() {
            const scatter_perf_data = JSON.parse(window.localStorage.getItem(`scatter-perf-${$("#page-header").attr("data-id")}`));
            if(scatter_perf_data){
                scatter_plot(scatter_perf_data);
                final_excercise_table_populate(scatter_perf_data);
            }
            set_language_strings();

        }, 250);
})

