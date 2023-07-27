var sort_by_name = 0;
var sort_by_final_result = 0;
var checked_ids = new Set();

function get_student_table_content(students) {
    // <i id="name-sort" class="sort-student bi bi-sort-alpha-down clickable-row"order="increasing"></i>
    // <i id="group-sort" class="sort-student bi bi-sort-alpha-down clickable-row center" order="none"></i>
    // <i id="team-sort" class="sort-student bi bi-sort-alpha-down clickable-row center" order="none"></i>
    // <i id="result-sort" class="sort-student bi bi-sort-numeric-down clickable-row center" order="none"></i>

    let student_html = "";
    for (var i = 0; i < students.length; i++) {
        // class = "clickable-row" data-bs-toggle="offcanvas"
        // ${students[i]["result"]["final_result"]==average.qs.max? '<i class="bi bi-trophy-fill"></i>':''}
        data_id = students[i].id+'-'+students[i].course.id
        student_html += `
        
            <tr >
                <td class="col-auto">
                    <div class="custom-control custom-checkbox">
                        <input type="checkbox" class="form-check-input form-check-secondary check-secondary student_check"  
                            name="student_${data_id}_check" 
                            data-id = "${data_id}"  ${checked_ids.has(data_id)? "checked='checked'":""}>
                        ${students[i]['first_name']} ${students[i]['last_name']}
                        <br/>${students[i]['company']["name"]}
                    </div>

                </td>
                <td class="col-auto">
                    ${students[i].group.name?students[i].group.name:''}
                </td>
                <td class="col-auto">
                    ${students[i]['team']["name"]?students[i]['team']["name"]:''}
                </td>
                <td class="col-auto">
                    ${students[i].final_result + '%'}
                </td>
                <td class="col-auto">
                    <span class="clickable-row" onclick=get_student_report_url("${students[i].report}")>
                        <button type="button" class="btn btn-outline-secondary">
                            <i class="bi bi-file-earmark-arrow-down-fill"></i>
                        </button>
                    </span>
                </td>
            </tr>
        `
    };
    return student_html;
}

function get_student_report_url(url){
    Swal.fire({
        title: "Downloading!",
        html: swal_desc,
        onRender: function () {
            // there will only ever be one sweet alert open.
            $('.swal2-content').prepend(sweet_loader);
        },
        allowOutsideClick: false,
        showConfirmButton: false,
    });
    var language = $("#language-select").val();
    get_ajax(
        url,
        data = {"language": language},
        on_success = student_report_download,
        on_failure = (res) => {
            console.error(res)
            Swal.fire({
                icon: 'error',
                title: "Error in download!",
                showConfirmButton: false,
                timer: 1000
            });
        },
    )
}

function student_report_download(res) {
    $.ajax({
        url: res.url,
        type: "GET",
        xhrFields: {
            responseType: 'blob'
        },
        success: function (response, status, request) {
            //$("#loader").hide(); // hides loading sccreen in success call back
            Swal.fire({
                title: "Download Finished!",
                icon: "success",
                showConfirmButton: true,
                // timer: 500
            }).then(function () {
                var a = document.createElement('a');
                var binaryData = [];
                binaryData.push(response);
                var url = window.URL.createObjectURL(new Blob(binaryData, {
                    type: "application/pdf"
                }))
                a.href = url;
                a.download = res.fname;
                document.body.append(a);
                a.click();
                a.remove();
                window.URL.revokeObjectURL(url);
            });
        },
        error: function (res) {
            Swal.fire({
                icon: 'error',
                title: "Error in download!",
                showConfirmButton: false,
                timer: 1000
            });
        }
    });
}

function populate_students_table(res, orignal = false){
    var container = $('#students-table-pagination')
    var total_length = res.items.length;
    var page_size = 6;
    container.pagination({
        dataSource: res.items,
        className: 'paginationjs-theme-grey paginationjs',
        pageRange: 1,
        pageSize: page_size,
        callback: function (data, pagination) {
            let start = (pagination.pageNumber - 1) * page_size;
            let end = (pagination.pageNumber) * page_size;
            if (total_length < end) end = total_length
            var html = get_student_table_content(res.items.slice(start, end))
            $("#students-table tbody").html(html);
        }
    })
}


function student_on_failure(res) {
    console.log(res)
}

$(document).ready(function () {
    $("#sort-student-name").click(function (e) {
        e.preventDefault()
        let students = JSON.parse(
            window.localStorage.getItem(
                `students-api-response-${$("#page-header").attr("data-id")}`
            )
        ).items
        students.sort((a, b)=>{
            let aname = (a.first_name+a.last_name).toLowerCase();
            let bname = (b.first_name+b.last_name).toLowerCase();
            if (aname < bname) {return -1;}
            if (aname > bname) {return 1;}
            return 0;
        })
        $("#sort-student-name .sort-student").removeClass("bi-filter")
        if(sort_by_name == -1 || sort_by_name == 0){
            sort_by_name = 1;
            $("#sort-student-name .sort-student").addClass("bi-sort-alpha-down")
            $("#sort-student-name .sort-student").removeClass("bi-sort-alpha-down-alt")
        }
        else if(sort_by_name == 1){
            sort_by_name = -1
            students.reverse()
            $("#sort-student-name .sort-student").addClass("bi-sort-alpha-down-alt")
            $("#sort-student-name .sort-student").removeClass("bi-sort-alpha-down")
        }
        populate_students_table({items: students}, original = false)
    });

    $("#sort-student-result").click(function (e) {
        e.preventDefault()
        let students = JSON.parse(
            window.localStorage.getItem(
                `students-api-response-${$("#page-header").attr("data-id")}`
            )
        ).items
        students.sort((a, b)=>{return a.final_result-b.final_result})
        $("#sort-student-result .sort-student").removeClass("bi-filter")
        if(sort_by_final_result == -1 || sort_by_final_result == 0){
            sort_by_final_result = 1;
            $("#sort-student-result .sort-student").addClass("bi-sort-numeric-down")
            $("#sort-student-result .sort-student").removeClass("bi-sort-numeric-down-alt")
        }
        else if(sort_by_final_result == 1){
            sort_by_final_result = -1
            students.reverse()
            $("#sort-student-result .sort-student").addClass("bi-sort-numeric-down-alt")
            $("#sort-student-result .sort-student").removeClass("bi-sort-numeric-down")
        }
        populate_students_table({items: students}, original = false)
    });

    $("#download_multiple_report").click(function(){
        let student_ids = Array.from(checked_ids);
        if(student_ids.length == 0){
            Swal.fire({
                title: "Please select atleast one student",
                icon: "info",
                showCloseButton: true,
                showCancelButton: true,
                focusConfirm: true,
            })
            return false;
        }
        
        Swal.fire({
            title: "Downloading the students report!",
            html: swal_download_multiple_course_desc,
            onRender: function () {
                $('.swal2-content').prepend(sweet_loader);
            },
            allowOutsideClick: false,
            showConfirmButton: false,
        });
        
        student_ids = student_ids.join(",")
        let language = $("#language-select").val()
        $.ajax({
            url: $(this).attr("data-url"),
            type: "GET",
            data: {"student_ids": student_ids, "language": language},
            xhrFields: {
                responseType: 'blob'
            },
            success: function (returnhtml, textStatus, request) {
                Swal.fire({
                    title: `Successfully downloaded the reports for selected students.`,
                    icon: "success",
                    showConfirmButton: true,
                    focusConfirm: true,
                })

                const fname = request.getResponseHeader('filename')
                var a = document.createElement('a');
                var binaryData = [];
                binaryData.push(returnhtml);
                var url = window.URL.createObjectURL(new Blob(binaryData, {
                    type: "application/x-zip-compressed"
                }))
                a.href = url;
                a.download = fname;
                document.body.append(a);
                a.click();
                a.remove();
                window.URL.revokeObjectURL(url);
            },
            error: function (res) {
                Swal.fire({
                    icon: 'error',
                    title: "Error in download!",
                    showConfirmButton: false,
                    timer: 1000
                });
            }
        });

    })

    get_ajax(
        url = $("#students-table").attr("data-url"),
        data = {},
        on_success = student_performers_on_success,
        on_failure = (res) => {console.error(res)},
        loader_ids = [".students-table-loader-gif", ".performance-loader-gif", ".control-performance-loader-gif"],
    )
    get_ajax(
        url = $("#heatmap-plot").attr("data-url"),
        data = {},
        on_success = performer_averages_on_success,
        on_failure = (res) => {console.error(res)},
        loader_ids = [".heatmap-loader-gif", ".overview-loader"],
    )

    $(".performer-tab").click(function () {
        setTimeout(
            function () {
                populate_performers_activity([], orignal = false);
                set_language_strings();
            }, 250);
    })

    $(document.body).on("click", ".student_check", function(){
        const dataid = $(this).attr("data-id");
        console.log(checked_ids)
        if($(this)[0].checked){
            $(this).prop('checked', true);
            checked_ids.add(dataid)
            let students = JSON.parse(window.localStorage.getItem(`students-api-response-${$("#page-header").attr("data-id")}`)).items
            if(checked_ids.size == students.length){
                $(".students_all_check").prop('checked', true);
            }
        }
        else{
            $(this).prop('checked', false);
            checked_ids.delete(dataid)
            $(".students_all_check").prop('checked', false);
        }

    })
    $(".students_all_check").click(function(){
        let students = JSON.parse(window.localStorage.getItem(`students-api-response-${$("#page-header").attr("data-id")}`)).items
        if($(this)[0].checked){
            $(".student_check").prop('checked', true);
        }
        else{
            $(".student_check").prop('checked', false);
        }

        for(var i = 0; i < students.length; i++){
            if($(this)[0].checked){
                checked_ids.add(students[i].id+'-'+students[i].course.id)
            }
            else{
                checked_ids.delete(students[i].id+'-'+students[i].course.id)
            }
        }
    })

})



$('#id_students_search_input').keypress(function() {
    let students = JSON.parse(window.localStorage.getItem(`students-api-response-${$("#page-header").attr("data-id")}`))
    var dInput = this.value;
    var re = new RegExp(dInput, "i");
    let filtered_students = students.items.filter((student)=>{
        return re.test(student.first_name + student.last_name) 
    })
    students.items = filtered_students;
    populate_students_table(students, original = false)
});