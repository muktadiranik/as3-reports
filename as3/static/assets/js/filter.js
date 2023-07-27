var start = moment().subtract(1, 'year');
var end = moment()
var filter_obj = {
    "groups": '',
    "teams": '',
    "locations": '',
    "programs": '',
    "start_date": '', // start.unix(),
    "end_date": '', // end.unix(),
}
var choicesInstances = {};

window.localStorage.setItem(`as3-filters-${$("#page-header").attr("data-id")}`, JSON.stringify(filter_obj))
var filter_get_url = $("#filterOffcanvasRight").attr("get_filters_url");

function update_choice_select() {
    let choices = document.querySelectorAll('.choices');
    let initChoice;
    for (let i = 0; i < choices.length; i++) {
        if (choices[i].classList.contains("multiple-remove")) {
            initChoice = new Choices(choices[i], {
                delimiter: ',',
                editItems: true,
                maxItemCount: -1,
                removeItemButton: true,
            });
        } else {
            initChoice = new Choices(choices[i]);
        }
    }
}

function populate_select_options(data, id_){
    tdata = "<optgroup>"
    for(var i = 0; i< data.length; i++){
        tdata +=`
        <option value="${data[i].key}">${data[i].value}</option>
        `
    }
    $(`#${id_}`).html(tdata);
    return new Choices(`#${id_}`, {
        allowHTML : true,
        delimiter: ',',
        editItems: true,
        maxItemCount: -1,
        removeItemButton: true,
    });
}

function populate_filter_select(res){
    choicesInstances["groups"] = populate_select_options(res.items.groups, "select-groups");
    choicesInstances["teams"] = populate_select_options(res.items.teams, "select-teams");
    choicesInstances["locations"] = populate_select_options(res.items.locations, "selectLocations");
    choicesInstances["programs"] = populate_select_options(res.items.programs, "selectPrograms");
}

function cb(st, en) {
    $('#_id_event_date_selector span').html(st.format('MMMM D, YYYY') + ' - ' + en.format('MMMM D, YYYY'));
    $('#_id_event_date_selector').attr("start", st);
    $('#_id_event_date_selector').attr("end", en);
    filter_obj.start_date = st.unix();
    filter_obj.end_date = en.unix();
}

function before_filter_fn(){
    $("#_id_filter_main_btn").html(`
    <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
    Applying...`)
    $("#_id_filter_reset_btn").html(`
    <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
    Applying...`)
    $("#_id_filter_main_btn").prop("disabled", true);
    $("#_id_filter_reset_btn").prop("disabled", true);
    $(".filter-affected").html("");
}
function after_filter_fn(){
    $("#_id_filter_main_btn").html('Apply Filter')
    $("#_id_filter_main_btn").prop("disabled", false);
    $("#_id_filter_reset_btn").html('Reset Filter')
    $("#_id_filter_reset_btn").prop("disabled", false);
}

function call_all_ajax(){
    before_filter_fn();
    setTimeout(() => {
        after_filter_fn();
    }, "2000");


    get_ajax(
        url = $("#heatmap-plot").attr("data-url"),
        data = filter_obj,
        on_success = performer_averages_on_success,
        on_failure = (res) => {console.error(res)},
        loader_ids = [".heatmap-loader-gif", ".overview-loader"],
    )

    get_ajax(
        url = $("#courses-table").attr("data-href"),
        data = filter_obj,
        on_success = populate_courses_table,
        on_failure = (e) => console.error(e),
        loader_ids = [".course-table-gif"],
    );

    get_ajax(
        url = $("#students-table").attr("data-url"),
        data = filter_obj,
        on_success = student_performers_on_success,
        on_failure = (res) => {console.error(res)},
        loader_ids = [".students-table-loader-gif", ".performance-loader-gif", ".control-performance-loader-gif"],
    )

    get_ajax(
        url = $("#activity-section").attr("perf-list-url"),
        data = filter_obj,
        on_success = performance_activities_on_success,
        on_failure = (res) => {console.error(res)},
        loader_ids = [".activity-loader-gif"],
        
    );
    get_ajax(
        url = $("#expired-certificates").attr("data-url"),
        data = {},
        on_success = expired_certificates_onsuccess,
        on_failure = (e) => console.error(e),
        loader_ids = [".overview-exp-loader"]
    );
}

$(document).ready(function(){
    $("#_id_filter_main_btn").click(function(e){
        e.preventDefault();
        window.localStorage.setItem(`as3-filters-${$("#page-header").attr("data-id")}`, JSON.stringify(filter_obj))
        call_all_ajax();
    })

    $("#_id_filter_reset_btn").click(function(e){
        e.preventDefault();
        for (const [key, value] of Object.entries(choicesInstances)) {
            value.removeActiveItems()
        }
        const start_dt = moment().subtract(1, 'year')
        const end_dt = moment()
        filter_obj = {
            "groups": '',
            "teams": '',
            "locations": '',
            "programs": '',
            "start_date": start_dt,
            "end_date": end_dt,
        }
        window.localStorage.setItem(`as3-filters-${$("#page-header").attr("data-id")}`, JSON.stringify(filter_obj))
        cb(start_dt, end_dt);
        call_all_ajax()
    })

    $("#select-groups").change(function (e) {
        $("#students-table tbody").html("");
        filter_obj["groups"] = $(this).val().join()
    })
    $("#select-teams").change(function (e) {
        filter_obj["teams"] = $(this).val().join()
    })
    $("#selectLocations").change(function (e) {
        filter_obj["locations"] = $(this).val().join()
    })
    $("#selectPrograms").change(function (e) {
        filter_obj["programs"] = $(this).val().join()
    })

    get_ajax(
        url = filter_get_url,
        data = {},
        on_success = populate_filter_select,
        on_failure = (res) => {console.error("Error in getting filters", res)},
        loader_ids = [".filter-select-spinner"],
        display_type = "inline-block"
    )

})

$('#_id_event_date_selector').daterangepicker({
    "showDropdowns": true,
    ranges: {
        // 'Today': [moment(), moment()],
        // 'Yesterday': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
        'Last 7 Days': [moment().subtract(6, 'days'), moment()],
        'Last 30 Days': [moment().subtract(29, 'days'), moment()],
        'This Month': [moment().startOf('month'), moment().endOf('month')],
        'Last Month': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')],
        'This Year': [moment().startOf('year'), moment().endOf('year')],
        'Last Year': [moment().subtract(1, 'year').startOf('year'), moment().subtract(1, 'year').endOf('year')],
    },
    "startDate": start,
    "endDate": end,
    "drops": "up",
    "alwaysShowCalendars": true,
    "opens": "center"
}, cb);
cb(start, end, filter_obj);