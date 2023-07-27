function populate_low_performer_text() {
    $("#low-performer-text").html(`
    <div class="language-en">
    <p>
        Being a low-performing student could be due to several things; the most important is lack of
        experience and/or confidence with the vehicle, which results in lost time during the exercise
    </p>
    <p>
        The key factors to watch for here are that a lower than 60% of the performance result could mean
        a severe lack of skill and should be considered a risk factor for a professional driver; anything
        below 40% is considered a dangerous driver.
        </p>
        <p>
        When a driver gets a low result on this exercise is usually due to failure to control the vehicle under
        pressure, this results in hitting obstacles or missing gates and being penalized because of it;
        this is usually due to lack of experience and could be corrected with stress inoculation training.
    </p>
    <p>
        <span class="low-students-text-name"></span>
        need to be exposed to more deliberate practice to ensure the proper reaction at a time of crisis
    </p>
</div>
<div class="language-es">
    <p>
        Ser un estudiante de bajo rendimiento podría deberse a varias cosas; lo más importante es la falta de 
        experiencia y/o confianza con el vehículo, lo que resulta en pérdida de tiempo durante el ejercicio
        </p>
        <p>
        Los factores clave a tener en cuenta aquí son que una menor del 60% del resultado de rendimiento podría significar
        una grave falta de habilidad y debe ser considerado un factor de riesgo para un conductor profesional; cualquier cosa
        por debajo del 40% se considera un conductor peligroso.
        </p>
        <p>
        Cuando un conductor obtiene un resultado bajo en este ejercicio es generalmente debido a la falta de control del vehículo bajo
        presión, esto resulta en golpear obstáculos o perder puertas y ser penalizado por ello;
        esto generalmente se debe a la falta de experiencia y podría corregirse con entrenamiento de inoculación de estrés.
        </p>
        <p>
        <span class="low-students-text-name"></span>
        deben estar expuestos a una práctica más deliberada para garantizar la reacción adecuada en un momento de crisis
    </p>
</div>`)
}

function populate_top_performer_text() {
    $("#top-performer-text").html(`
        <div class="language-en">
            <p>
                This are your team's top performers for the period specified on the cover of this report, all
                names included in this list must have achieved the minimum of 80% contol over the car's capabilities.
                </p>
                <p>
                These are the Top 10 performers for the 2020 - 2022 term. To be on this list, each student must
                have achieved a grade of at least 80% or higher during the final exercise.
                </p>
                <p>
                A higher Performance means a faster driver; this means the driver is more confident with his
                vehicle. Anyone above the group's 61 % average can be considered a good driver, primarily if that
                is achieved under stress
                </p>
                <p>
                On the other hand, Slalom & Barricade will relate the amount of control for each student; a higher
                number means more experience. The ideal driver should achieve above 80% in slalom and barricade; anyone
                 above the group's 55% average should be considered a good driver.
            </p>

            <p>
                The reverse is probably the most crucial part of the final exercise, and students are required
                to do this in under 20% of their overall time; statistically, the safest way out of a possible ambush is
                backward, not being able to achieve this places the driver at a significant disadvantage.
            </p>
        </div>
        <div class="language-es">
            <p>
                Estos son los mejores jugadores de su equipo durante el período especificado en la portada de  este informe, todos los
                nombres incluidos en esta lista deben haber alcanzado el control mínimo del 80% sobre las capacidades del automóvil.
                </p>
                <p>
                Estos son los 10 mejores artistas del 2020: término 2022. Para estar en esta lista, cada estudiante debe
                haber alcanzado una calificación de al menos 80% o superior durante el ejercicio final.
                </p>
                <p>
                Un mayor rendimiento significa un conductor más rápido; este significa que el conductor tiene más confianza con su
                vehículo. Cualquiera por encima del promedio del 61 % del grupo puede ser considerado un buen conductor, principalmente si eso
                se logra bajo estrés
                </p>
                <p>
                Por otro lado, Slalom & Barricade relacionará la cantidad de control para cada estudiante; una mayor
                número significa más experiencia. El conductor ideal debe alcanzar por encima del 80% en slalom y
                barricada; cualquiera por encima del promedio del 55% del grupo debe ser considerado un buen conductor.
            </p>
            <p>
                El reverso es probablemente la parte más crucial del ejercicio final, y los estudiantes deben hacer este
                en menos del 20% de su tiempo total; estadísticamente, la forma más segura de salir de una posible emboscada es
                hacia atrás, no poder lograr esto coloca al conductor en una desventaja significativa.
            </p>
        </div>
 `)
}

function populate_performers_activity(res, orignal = true) {
    if(orignal){
        var performers = res.items
        window.localStorage.setItem(`performers-${$("#page-header").attr("data-id")}`, JSON.stringify(performers));
    }
    else
        var performers = JSON.parse(window.localStorage.getItem(`performers-${$("#page-header").attr("data-id")}`));
    if(!performers.length){
        return false;
    }
    performers.sort(function(a, b) {
        return b.final_result - a.final_result;
    });
    let top_students = performers.filter((ele)=>{
        return ele.final_result >= 80;
    }).slice(0, 7);
    if(top_students.length == 0){
        $("#top-performer-text").html(
            "<h6 class = 'text-center'>There are no top performers worth mentioning</h6>")
    }
    else{
        populate_performers_table(top_students, "#top-performer-table")
        populate_top_performer_text();
        plot_performers_chart(top_students, document.getElementById('top-performer-plot'), "Top")
    }
    
    let low_students = performers.filter((ele)=>{
        return ele.final_result < 80;
    }).reverse().slice(0, 7);
    if(low_students.length == 0){
        $("#low-performer-text").html(
            "<h6 class = 'text-center'>There are no low performers worth mentioning.</h6>")
    }
    else{
        var low_3 = []
        for (var i = 0; i < Math.min(3, low_students.length); i++) {
            low_3.push(low_students[i].first_name + " " + low_students[i].last_name);
        }
        populate_low_performer_text();
        if(low_3.length){
            let low_3_text = low_3[0];
            if(low_3.length >= 2)
                low_3_text += ', ' + low_3[1]
            if(low_3.length == 3)
                low_3_text += ", and " + low_3[2]
            $(".low-students-text-name").html(low_3_text)
        }
        populate_performers_table(low_students, "#low-performer-table")
        plot_performers_chart(low_students, document.getElementById('low-performer-plot'), "Low")
        set_language_strings();
    }
}

function populate_performers_table(students, _id) {
    var students_rows = ""
    let reverse_sum = 0;
    let slalom_sum = 0;
    let lane_change_sum = 0;
    let final_result_sum = 0;
    let total_students = students.length;

    for (var i = 0; i < total_students; i++) {
        reverse_sum += students[i].reverse;
        slalom_sum += students[i].slalom;
        lane_change_sum += students[i].lane_change;
        final_result_sum += students[i].final_result;

        students_rows += `
            <tr>
            <td class="col-auto">
                ${students[i].first_name} ${students[i].last_name}
            </td>
            <td class="col-auto center">
                ${students[i].stress}
            </td>
            <td class="col-auto center">
                ${students[i].reverse}
            </td>
            <td class="col-auto center">
                ${students[i].slalom}
            </td>
            <td class="col-auto center">
                ${students[i].lane_change}
            </td>
            <td class="col-auto center">
                ${students[i].final_result}
            </td>
        </tr>`
    }
    students_rows += `
        <tr>
            <td class="col-auto">
                <b>
                <span class="language-en">Group Average</span>
                <span class="language-es">Promedio del Grupo</span>
                </b>
            </td>
            <td class="col-auto">
            </td>
            <td class="col-auto">
                <b>${(reverse_sum/total_students).toFixed(0)}</b>
            </td>
            <td class="col-auto">
                <b>${(slalom_sum/total_students).toFixed(0)}</b>
            </td>
            <td class="col-auto">
                <b>${(lane_change_sum/total_students).toFixed(0)}</b>
            </td>
            <td class="col-auto">
                <b>${(final_result_sum/total_students).toFixed(0)}</b>
            </td>
        </tr>`

    $(_id).html(
        `<table class="table table-responsive table-sm">
            <thead>
                <tr>
                <th class="col-sm-5 col-xs-5 col-md-5 col-xl-5 col-xxl-5">
                <span class="language-en">FULL NAME</span>
                <span class="language-es">NOMBRE COMPLETO</span>
                </th>
                <th class="col-sm-2 col-xs-2 col-md-2 col-xl-2 col-xxl-2">
                <span class="language-en">STRESS LEVEL</span>
                <span class="language-es">NIVEL DE ESTRÉS</span>
                </th>
                <th class="col-sm-1 col-xs-1 col-md-1 col-xl-1 col-xxl-1">
                <span class="language-en">REVERSE (%)</span>
                <span class="language-es">REVERSA (%)</span>
                </th>
                <th class="col-sm-1 col-xs-1 col-md-1 col-xl-1 col-xxl-1">
                <span class="language-en">SLALOM TEST (%)</span>
                <span class="language-es">PRUEBA DE SLALOM(%)</span>
                </th>
                <th class="col-sm-2 col-xs-2 col-md-2 col-xl-2 col-xxl-2">
                <span class="language-en">BARRICADE EVASION (%)</span>
                <span class="language-es">EVASIÓN DE BARRICADA (%)</span>
                </th>
                <th class="col-sm-1 col-xs-1 col-md-1 col-xl-1 col-xxl-1">
                <span class="language-en">PERFORMANCE (%)</span>
                <span class="language-es">DESEMPEÑO (%)</span>
                </th>
                </tr>
            </thead>
            <tbody>
                ${students_rows}
            </tbody>
        </table>
        `
    )
}

function performance_on_error(response) {
    alert(response)
}
