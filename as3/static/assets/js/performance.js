var perf_list_url = $("#activity-section").attr("perf-list-url")

function plot_activities_charts(data, plot_id, title) {
    var participant_max_len = 0;
    x1 = data.pvehicles.map(function (el) {
        if(el.participant.length > participant_max_len)
            participant_max_len = el.participant.length
        return el.participant;
    })
    y1 = data.pvehicles.map(function (el) {
        return el.value;
    })
    x2 = data.tries.map(function (el) {
        return el.participant;
    })
    y2 = data.tries.map(function (el) {
        return el.value;
    })
    const y2_sum = y2.reduce((a, b) => a + b, 0);
    const y2_avg = (y2_sum / y2.length) || 0;
    const y1_sum = y1.reduce((a, b) => a + b, 0);
    const y1_avg = (y1_sum / y1.length) || 0;

    let language = window.localStorage.getItem("language")
    if(language == "es"){
        var ov = "% del Vehículo"
        var not = "Número de Intentos"
    }
    else{
        var ov = "% of the Vehicle"
        var not = "Number of Tries"
    }

    let trace1 = {
        x: x1,
        y: y1,
        text: y1.map(function (el) {
            return `<b>${el}</b>`;
        }),
        hovertemplate: '(%{x}, %{y})<extra></extra>',
        marker: {
            color: "red",
            size: 8,
        },
        textfont: {
            size: 12,
            color: "red",
        },
        textposition: 'auto',
        textcolor: "red",
        type: "scatter",
        mode: 'markers+text+lines',
        textposition: 'top center',
        showlegend: false,
    }

    let trace2 = {
        x: x2,
        y: y2,
        hovertemplate: '(%{x}, %{y})',
        text: y2.map(function (el) {
            return `<b>${el}</b>`;
        }),
        marker: {
            color: "grey",
            size: 8,
            symbol: 'square',
        },
        yaxis: 'y2',
        textfont: {
            size: 12,
        },
        textcolor: "grey",
        showlegend: false,
        type: "scatter",
        mode: 'markers+text',
        textposition: 'bottom center',
    }
    let trace3 = {
        x: x2,
        y: y2.map(function (el) {
            return y2_avg;
        }),
        hovertemplate: 'Average: %{y}',
        text: ["Average"],
        textposition: 'bottom right',
        yaxis: 'y2',
        textfont: {
            size: 12,
            color: "#CCCCCC",
        },
        line: {
            dash: 'dot',
            width: 3
        },
        marker: {
            color: "#CCCCCC",
            size: 4,
        },
        yref: "paper",
        type: "line",
        color: "#CCCCCC",
        mode: 'lines+text',
        showlegend: false,
    }
    let trace4 = {
        x: x1,
        y: y1.map(function (el) {
            return y1_avg;
        }),
        yaxis: 'y1',
        text: ["Average"],
        textposition: 'bottom right',
        hovertemplate: 'Average: %{y}',
        textfont: {
            size: 12,
            color: "#FECCCD"
        },
        line: {
            dash: 'dot',
            width: 3
        },
        marker: {
            size: 4,
            color: "#FECCCD",
        },
        yref: "paper",
        type: "line",
        color: "#FECCCD",
        mode: 'lines+text',
        showlegend: false,
    }
    let trace5 = {
        x: x1,
        y: y1.map(function (el) {
            return 80;
        }),
        yaxis: 'y1',
        text: ["Minimum %"],
        hovertemplate: 'Average: 80',
        textfont: {
            size: 13,
            color: "#C87867"
        },
        marker: {
            color: "#C87867",
            size: 4,
        },
        textposition: 'bottom right',
        line: {
            dash: 'dot',
            width: 3,
            color: "#C87867",
        },
        yref: "paper",
        type: "line",
        color: "#C87867",
        mode: 'lines+text',
        showlegend: false,
    }

    var layout = {
        height: 600,
        yaxis: {
            title: ov,
            zeroline: false,
            showgrid: false,
        },
        font: {
            family: 'Poppins',
            size: 12.5,
            color: 'black'
        },
        yaxis2: {
            title: not,
            overlaying: 'y',
            side: 'right',
            zeroline: false,
            showgrid: false,
        },
        xaxis: {
        },
        annotations: [{
            showarrow: false,
            text: "Better ->",
            textangle:-90,
            y: y1_avg + 10,
            yaxis: 'y1',
            x: -0.5,
            font: {
                color: '#C87867',
            }
        },
        {
            showarrow: false,
            text: "<-Better",
            textangle:-90,
            y: y2_avg,
            x: -0.5,
            yaxis: 'y2',
            font: {
                color: 'grey',
              }
        },
        ],
        title: title,
        margin: {
            // autoexpand: true,
            b: (participant_max_len*3 + x1.length*2),
            // t: 200,
            // pad: 200,
        }
    }
    var current_width = window.screen.width;
    if(current_width >= 1200 && current_width <= 1500){
        layout.height = 480
    }
    else if(current_width > 1500 && current_width <= 1800){
        layout.height = 580
    }
    else if(current_width > 1800){
        layout.height = 650
    }
    let config = {
        responsive: true,
        editable: false,
        // staticPlot: true,

    }
    Plotly.newPlot(plot_id, [ trace3, trace4, trace5, trace1, trace2], layout, config);
}

function performance_activities_on_success(data, orignal = true){
    if(orignal)
        window.localStorage.setItem(`activities-result-${$("#page-header").attr("data-id")}`, JSON.stringify(data));

    // if(jQuery.isEmptyObject(data.items)){
    //     return false;
    // }
    
    var title = "";
    let language = window.localStorage.getItem("language")
    if(language == "es") title = "Desempeño en Ejercicio de Slalom"
    else title = "Slalom Exercise Performance"
    
    plot_activities_charts(
        data.items.slalom,
        "slalom-activity-plot", 
        title
    )
    if(language == "es") title = "Desempeño en Evasión de Barricada"
    else title = "Barricade Evasion Performance"
    plot_activities_charts(
        data.items.lane_change, 
        "lane-change-activity-plot", 
        title
    )


    data = data.items    

    $("#slalom-activity-text").html(
        `
        <div class = "language-en">

        <p><b>Type:</b> Regular Slalom – 4 Cones (50ft Chord)<br/>
        <b>Difficulty Level:</b> Medium / Hard</p>

        <p><b>The group's average top performance was: ${data.slalom.avg_pvehicles}%</b>
        <br/>
        ${data.slalom.pvehicles_above_avg} students are above the average of control, while ${data.slalom.pvehicles_below_avg} are below
        the group average.</p>
        <p><b>The group's average tries was: ${data.slalom.avg_tries}</b>, and the students achieved the
        minimum standard on average ${data.slalom.gp_met_std} times (please refer to the individual
        reports for each student stats)</p>
        </div>
        
        <div class = "language-es">
        <p><b>El rendimiento máximo promedio del grupo fue: ${data.slalom.avg_pvehicles}%</b>
        <br/>
        ${data.slalom.pvehicles_above_avg} los estudiantes están por encima del promedio de control, mientras que 
        ${data.slalom.pvehicles_below_avg} están por debajo del promedio del grupo</p>
        <p><b>El promedio de intentos del grupo fue: ${data.slalom.avg_tries}</b>, y los estudiantes lograron el estándar mínimo en promedio
        ${data.slalom.gp_met_std}
        veces (consulte los informes individuales para las estadísticas de cada estudiante).</p>
        </div>
        `
    )

    $("#lane-change-activity-text").html(
        `
        <div class = "language-en">
        <p><b>Type:</b> Regular LnCh – .75 Sec Reaction time (100ft Chord)<br/>
        <b>Difficulty Level:</b> Medium</p>
        <p><b>The group's average top performance was: ${data.lane_change.avg_pvehicles}%</b>
        <br />
        ${data.lane_change.pvehicles_above_avg} students are above the average of control, while  ${data.lane_change.pvehicles_below_avg} are below
        the group average.</p>

        <p><b>The group's average tries was: ${data.lane_change.avg_tries}, a considerable improvement over
        slalom's average of ${data.slalom.avg_tries}, at this point skill buildup starts to become
        evident; the students achieved the minimum standard on average ${data.lane_change.gp_met_std}
        times (please refer to the individual reports for each student stats).</p>
        </div>

        <div class = "language-es">
        <p><b>El rendimiento máximo promedio del grupo fue: ${data.lane_change.avg_pvehicles}%</b>
        <br />
        ${data.lane_change.pvehicles_above_avg} los estudiantes están por encima del promedio de control, mientras que  ${data.lane_change.pvehicles_below_avg}
        están por debajo del promedio del grupo.</p>

        <p><b>El promedio de intentos del grupo fue: ${data.lane_change.avg_tries}, una mejora considerable sobre promedio de slalom de
        ${data.slalom.avg_tries} en este punto la acumulación de habilidades comienza a ser evidente; los estudiantes alcanzaron el estándar mínimo en promedio
        ${data.lane_change.gp_met_std} veces (consulte los reportes individuales para las estadísticas de cada alumno).</p>

        </div>
        `
    )
    set_language_strings();
    
}


get_ajax(
    url = perf_list_url,
    data = {},
    on_success = performance_activities_on_success,
    on_failure = (res) => {console.error(res)},
    loader_ids = [".activity-loader-gif"]
)

$("#lane-change-activity-tab").click(function(){
    setTimeout(
        function() {
            const activities_result_data = JSON.parse(window.localStorage.getItem(`activities-result-${$("#page-header").attr("data-id")}`));
            var title = "";
            let language = window.localStorage.getItem("language")
            if(language == "es") title = "Desempeño en Evasión de Barricada"
            else title = "Barricade Evasion Performance"
            if(activities_result_data && activities_result_data.items){
                plot_activities_charts(
                    activities_result_data.items.lane_change, 
                    "lane-change-activity-plot", 
                    title
                )
                set_language_strings();
            }
        }, 250);
})


$("#slalom-activity-tab").click(function(){
    setTimeout(
        function() {
            const activities_result_data = JSON.parse(window.localStorage.getItem(`activities-result-${$("#page-header").attr("data-id")}`));
            var title = "";
            let language = window.localStorage.getItem("language")
            if(language == "es") title = "Desempeño en Ejercicio de Slalom"
            else title = "Slalom Exercise Performance"
            if(activities_result_data && activities_result_data.items)
                plot_activities_charts(
                    activities_result_data.items.slalom, 
                    "slalom-activity-plot", 
                    title
                )
            set_language_strings();
        }, 250);
})

