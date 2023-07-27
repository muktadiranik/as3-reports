var users_table_filter = {
    "profile": "",
    "country": "",
}

var companies_table_filter = {}
var companies_data = []
var choicesInstances = {};

function populate_select_options(data, id_){
    return new Choices(`#${id_}`, {
        silent: false,
        allowHTML : true,
        choices: data, 
        delimiter: ',',
        maxItemCount: 6,
        renderChoiceLimit: 3,
        searchEnabled: true,
        position: 'bottom',
        loadingText: 'Loading...',
        noResultsText: 'No results found',
        noChoicesText: 'No choices to choose from',
        searchResultLimit: 4,
        searchChoices: true,
        resetScrollPosition: true,
        shouldSort: true,
    });
}

$(".create-basic-model-btn").click(function(){
    var data_url = $(this).attr("data-url")
    $("#_id_basic_model_create_form").attr("data-url", data_url)
    $(".model_data_type").html($(this).attr("data-type"))
    $("#_id_basic_model_create_form").attr("data-type", $(this).attr("data-type"))
})

function get_user_table_content(data) {
    content = `
    <table class="table table-responsive table-lg">
        <thead>
            <tr>
                <th>USERNAME</th>
                <th>NAME</th>
                <th>COMPANY</th>
                <th>ACTION</th>
            </tr>
        </thead>
        <tbody>
    `
    for (var i = 0; i < data.length; i++) {
        content += `
        <tr data-id = "${data[i].id}">
            <td >
            ${data[i].country == "USA" ?
            '<span ><img src = "/static/assets/images/united-states-of-america.png" style = "width:20px; height:20px;"/></span>': 
            '<span><img src = "/static/assets/images/mexico.png" style = "width:20px; height:20px;" /></span>'}
            <span>
            ${data[i].username}<br>
            ${data[i].last_login ? 
                `<span class = 'fs-6 fw-lighter'><i class="bi bi-clock"></i> ${data[i].last_login}</span>`
                : `<span class = 'fs-6 fw-lighter'><i class="bi bi-clock"></i> Never logined</span>`
            }
            </span>    
            </td>
            <td>
                ${data[i].name}
            </td>
            <td >
                ${data[i].company.name?data[i].company.name:""}
            </td>
            <td>
            <a data-id = "${data[i].id}" class = "clickable-row send-welcome-email-btn">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-send-plus-fill" viewBox="0 0 16 16">
            <path d="M15.964.686a.5.5 0 0 0-.65-.65L.767 5.855H.766l-.452.18a.5.5 0 0 0-.082.887l.41.26.001.002 4.995 3.178 1.59 2.498C8 14 8 13 8 12.5a4.5 4.5 0 0 1 5.026-4.47L15.964.686Zm-1.833 1.89L6.637 10.07l-.215-.338a.5.5 0 0 0-.154-.154l-.338-.215 7.494-7.494 1.178-.471-.47 1.178Z"/>
            <path d="M16 12.5a3.5 3.5 0 1 1-7 0 3.5 3.5 0 0 1 7 0Zm-3.5-2a.5.5 0 0 0-.5.5v1h-1a.5.5 0 0 0 0 1h1v1a.5.5 0 0 0 1 0v-1h1a.5.5 0 0 0 0-1h-1v-1a.5.5 0 0 0-.5-.5Z"/>
          </svg>
            </a>
                <a data-bs-toggle="modal" data-bs-target="#add-edit-user-modal"  style = "color:grey"
                    class = 'edit-user-modal-action clickable-row edit-user-btn'  data-id = "${data[i].id}">
                <i class="bi bi-pencil-square"></i>
                </a>
                <a style = "color:red" class = 'delete-user-modal-action clickable-row'  data-id = "${data[i].id}">
                    <i class="bi bi-trash"></i>
                </a>
         
            </td>
        </tr>
        `
    }
    content += `</tbody></table>`
    return content;
}

function before_addedit_fn(_id) {
    $(_id).html(`
    <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
    Loading...`)
    $(_id).prop("disabled", true);
}

function after_addedit_fn(_id) {
    $(_id).html('Submit')
    $(_id).prop("disabled", false);
}

function populate_users_table(res, original = true) {
    if (original) {
        var users = res.items
        window.localStorage.setItem("admin-users", JSON.stringify(users));
        $('#id_user_search_input').val("")
    } else {
        var users = res
    }
    var container = $('#user-table-pagination')
    var total_length = users.length;
    var page_size = 5;
    var html = get_user_table_content(users.slice(0, page_size))
    $("#users-table").html(html);

    container.pagination({
        dataSource: users,
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
            var html = get_user_table_content(users.slice(start, end))
            $("#users-table").html(html);
        }
    })
}

function is_valid_user_table_content(data) {
    content = `
        <ul class="list-group list-group-flush">
    `

    for (var i = 0; i < data.length; i++) {
        content += `
            <li class="list-group-item">
                <a href = "/admin/company/${data[i].id}" target = "_blank" style = "color:black">
                ${data[i].name} <i class="bi bi-box-arrow-up-right"></i>
                <a>
                <a class = 'download-student-report clickable-row btn btn-sm' style = "color:red" onclick=global_company_report_download('${data[i].report_url}'); >
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-file-earmark-pdf" viewBox="0 0 16 16">
                <path d="M14 14V4.5L9.5 0H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2zM9.5 3A1.5 1.5 0 0 0 11 4.5h2V14a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1h5.5v2z"/>
                <path d="M4.603 14.087a.81.81 0 0 1-.438-.42c-.195-.388-.13-.776.08-1.102.198-.307.526-.568.897-.787a7.68 7.68 0 0 1 1.482-.645 19.697 19.697 0 0 0 1.062-2.227 7.269 
                7.269 0 0 1-.43-1.295c-.086-.4-.119-.796-.046-1.136.075-.354.274-.672.65-.823.192-.077.4-.12.602-.077a.7.7 0 0 1 .477.365c.088.164.12.356.127.538.007.188-.012.396-.047.614-.084.51-.27 
                1.134-.52 1.794a10.954 10.954 0 0 0 .98 1.686 5.753 5.753 0 0 1 1.334.05c.364.066.734.195.96.465.12.144.193.32.2.518.007.192-.047.382-.138.563a1.04 1.04 0 0 1-.354.416.856.856 0 0 
                1-.51.138c-.331-.014-.654-.196-.933-.417a5.712 5.712 0 0 1-.911-.95 11.651 11.651 0 0 0-1.997.406 11.307 11.307 0 0 1-1.02 1.51c-.292.35-.609.656-.927.787a.793.793 0 
                0 1-.58.029zm1.379-1.901c-.166.076-.32.156-.459.238-.328.194-.541.383-.647.547-.094.145-.096.25-.04.361.01.022.02.036.026.044a.266.266 0 0 0 .035-.012c.137-.056.355-.235.635-.572a8.18 8.18 0 
                0 0 .45-.606zm1.64-1.33a12.71 12.71 0 0 1 1.01-.193 11.744 11.744 0 0 1-.51-.858 20.801 20.801 0 0 1-.5 1.05zm2.446.45c.15.163.296.3.435.41.24.19.407.253.498.256a.107.107 0 0 0 .07-.015.307.307 
                0 0 0 .094-.125.436.436 0 0 0 .059-.2.095.095 0 0 0-.026-.063c-.052-.062-.2-.152-.518-.209a3.876 3.876 0 0 0-.612-.053zM8.078 7.8a6.7 6.7 0 0 0 .2-.828c.031-.188.043-.343.038-.465a.613.613 0 
                0 0-.032-.198.517.517 0 0 0-.145.04c-.087.035-.158.106-.196.283-.04.192-.03.469.046.822.024.111.054.227.09.346z"/>
              </svg>
                </a>
            </li>
        `
    }
    content += `</ul>`
    return content;
}

function populate_companies_table(res, original = true) {
    if (original) {
        var companies = res.items
        window.localStorage.setItem("admin-companies", JSON.stringify(companies));
        $('#id_company_search_input').val("")
    } else {
        var companies = res
    }

    var container = $('#companies-table-pagination')
    var total_length = companies.length;
    var page_size = 8;
    var html = is_valid_user_table_content(companies.slice(0, page_size))
    $("#companies-table").html(html);

    container.pagination({
        dataSource: companies,
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
            var html = is_valid_user_table_content(companies.slice(start, end))
            $("#companies-table").html(html);
        }
    })
}

function on_company_click_modal(rid) {
    $("#company-detail-modal-label").html(companies_data[rid][1])
    $("#company-user-modal-body").html(
        `<table class="table table-responsive table-lg">
        <tbody>
        <tr><td>Slalom Average</td> <td>${companies_data[rid][3].toFixed(2)}</td></tr>
        <tr><td>Performance Average</td> <td>${companies_data[rid][4].toFixed(2)}</td></tr>
        <tr><td>Lane change Average</td> <td>${companies_data[rid][5].toFixed(2)}</td></tr>
        <tr><td>Low stress Average</td> <td>${companies_data[rid][6].toFixed(2)}</td></tr>
        <tr><td>High stress Average</td> <td>${companies_data[rid][7].toFixed(2)}</td></tr>
        <tr><td>Pass Count</td> <td>${companies_data[rid][8]}</td></tr>
        </tbody>
        </table>
        `
    )
    $("#detail_page_btn").attr("href", `/admin/company/${companies_data[rid][0]}`);
}

function get_vehicle_table_content(data) {
    content = `
    <ul class="list-group">`
    for (var i = 0; i < data.length; i++) {
        content += `
        <li class="list-group-item d-flex justify-content-between align-items-center">
            <div class="col-8 text-left">
                <h6>${data[i].name}
                <a data-bs-toggle="modal" data-bs-target="#add-edit-vehicle-modal" style = "color:grey"
                class='edit-vehicle-modal-action clickable-row edit-vehicle-btn'  data-id = "${data[i].id}">
                <i class="bi bi-pencil-square"></i>
                </a>
                </h6>
            </div>
            <div class="col-4 text-right">
                <img src="${data[i].image ? data[i].image:no_image_url}" class="img-fluid" />
            </div>
        </li>
        <br/>
        `
    }
    content += `</ul>`
    return content;
}

function get_all_admin_ajax() {
    get_ajax(
        url = $("#users-table").attr("data-url"),
        data = users_table_filter,
        on_success = populate_users_table,
        on_failure = (res) => {
            console.error(res)
        },
        // loader_ids = ".heat-map-loader"
    )

    get_ajax(
        url = $("#companies-table").attr("data-url"),
        data = companies_table_filter,
        on_success = populate_companies_table,
        on_failure = (res) => {
            console.error(res)
        },
        // loader_ids = ".heat-map-loader"
    )


    get_ajax(
        url = $("#vehicles-table").attr("data-url"),
        data = {},
        on_success = populate_vehicles_table,
        on_failure = (res) => {
            console.error(res)
        },
        // loader_ids = ".heat-map-loader"
    )

    get_ajax(
        url = $("#course-upload-table").attr("data-url"),
        data = {},
        on_success = populate_course_upload_table,
        on_failure = (res) => {
            console.error(res)
        },
        // loader_ids = ".heat-map-loader"
    )
}

function populate_vehicles_table(res, original = true) {
    if (original) {
        var vehicles = res.items
        window.localStorage.setItem("admin-vehicles", JSON.stringify(vehicles));
        $('#id_vehicle_search_input').val("")
    } else {
        var vehicles = res
    }
    var container = $('#vehicles-table-pagination')
    var total_length = vehicles.length;
    var page_size = 4;
    var html = get_vehicle_table_content(vehicles.slice(0, page_size))
    $("#vehicles-table").html(html);

    container.pagination({
        dataSource: vehicles,
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
            var html = get_vehicle_table_content(vehicles.slice(start, end))
            $("#vehicles-table").html(html);
        }
    })
}

$(document).ready(function () {
    //clearing the localstorage on admin page. To save memory
    window.localStorage.clear();
    populate_course_upload_section();
    document.getElementById('course-uploader-loader').classList.add("hidden");

    get_all_admin_ajax()

    $('#create-basic-model-modal').on('shown.bs.modal', function() {
        $(document).off('focusin.modal');
        $("#id_basic_model_input").focus()
    });
    
    $("#_id_basic_model_create_form").submit(function(e){
        e.preventDefault();
        var values = $(this).serializeArray();
        let url = $(this).attr("data-url")
        let dtype = $(this).attr("data-type")
        post_ajax(
            url = url,
            data = values,
            on_success = function(res){
                get_ajax(
                    url = url,
                    data = {},
                    on_success = function(res){
                        $("#_id_basic_model_create_form")[0].reset();
                        var items = []
                        for(var i = 0; i < res.items.length; i++){
                            items.push({
                                value: res.items[i].id,
                                label: res.items[i].name,
                                selected: false,
                                disabled: false,
                            })
                        }
                        choicesInstances[dtype].destroy()
                        choicesInstances[dtype] = populate_select_options(items, `select${dtype}`);
                    },
                    on_failure = function(res){
                        console.error(res)
                    }
                )
            },
            on_failure = function(res){
                console.error(res)
                Swal.fire({
                    title: "Fail to create company",
                    text: res.responseText,
                    icon: "error",
                    showConfirmButton: true,
                })
            }
        )
    })

    $(document.body).on("click", ".edit-user-btn", function (e) {
        e.preventDefault()
        $('#admin_create_edit_form')[0].reset();
        $("#submit-user").attr("submit_type", "edit");
        const users = JSON.parse(window.localStorage.getItem("admin-users"))
        const data_id = $(this).attr("data-id");
        $("#admin_create_edit_form").attr("data-id", data_id);
        const user = users.filter(function (el) {
            return el.id == data_id
        })[0];
        $(".user_createtype_head").html(`Edit User: ${user.username}`);
        $(".user_createtype_btn").html("Update User")

        $("#password-field #id_password").prop("disabled", true);
        $("#password-field").hide();

        for (let key in user) {
            $(`#admin_create_edit_form input[name='${key}'`).val(user[key])
        }
        if (user.company.id) {
            $("#id_user_company_select").val(user.company.id)
        }

        $("#superadmin_option").remove()
        if (user.profile == "Superadmin") {
            $("#id_profile").append("<option value = 'Superadmin' selected id = 'superadmin_option'>Superadmin</option>")
            $("superadmin_option").val("Superadmin")
            $("#id_profile").attr("readonly", "readonly")
        } else {
            $("#id_profile").removeAttr("readonly")
            $("#id_profile").val(user.profile)
        }
        if (user.profile == "Company") {
            $("#id_user_company_select").attr("disabled", false)
        } else {
            $("#id_user_company_select").attr("disabled", true)
        }

        $("#id_country").val(user.country)
        $(`#admin_create_edit_form input[name='username`).prop('disabled', true);
    })


    $(document.body).on("click", ".edit-vehicle-modal-action", function (e) {
        const vehicle_id = $(this).attr("data-id");
        let vehicles = JSON.parse(window.localStorage.getItem("admin-vehicles"))
        const vehicle = vehicles.filter(function (el) {
            return el.id == vehicle_id
        })[0];
        console.log(vehicle)
        $('#vehicle-image-image-preview').css('background-image', 'url('+vehicle.image +')');

        $("#vehicle_create_edit_form")[0].reset()
        $("#id_vehicle_name").val(vehicle.name);
        $("#id_last_acc").val(vehicle.latAcc);
        $("#id_vehicle_type").val(vehicle.type);
        $("#id_vehicle_model").val(vehicle.model);
        $("#id_vehicle_make").val(vehicle.make);

        // $("#id_vehicle_image").val(vehicle.image);
        $("#vehicle_create_edit_form").attr("data-url", vehicle.url)
    });

    $(document.body).on("click", ".send-welcome-email-btn", function (e) {
        const users = JSON.parse(window.localStorage.getItem("admin-users"))
        const data_id = $(this).attr("data-id");
        $("#admin_create_edit_form").attr("data-id", data_id);
        const user = users.filter(function (el) {
            return el.id == data_id
        })[0];

        Swal.fire({
            title: `Do you want to send an welcome email to ${user.email}?`,
            icon: "warning",
            showCloseButton: true,
            showCancelButton: true,
            focusConfirm: true,
            confirmButtonText: '<i class="bi bi-hand-thumbs-up-fill"></i> Yes send it!',
        }).then(function (isConfirm) {
            if (!isConfirm.isConfirmed) {
                return;
            }
            post_ajax(
                url = `/core/v1/api/admin/user/${data_id}/send-welcome-email`,
                data = {},
                on_success = function(res){
                    Swal.fire({
                        title: "Email sent successfully",
                        icon: "success",
                        showConfirmButton: true,
                    })
                },
                on_failure = function(res){
                    console.error(res);
                    Swal.fire({
                        title: "Fail to send email",
                        icon: "error",
                        showConfirmButton: true,
                    })
                }
            )
        });
    });
    
    $(document.body).on("click", "#add-user-btn", function (e) {
        $("#id_profile").removeAttr("readonly")
        $("#superadmin_option").remove()

        $("#id_user_company_select").val("-1")
        $("#id_user_company_select").attr("disabled", true)

        $(".user_createtype_head").html("Create new User");
        $(".user_createtype_btn").html("Add User")
        $("#submit-user").attr("submit_type", "add");
        $('#admin_create_edit_form')[0].reset();
        $("#password-field #id_password").prop("disabled", false);
        $("#password-field").show();
        $(`#admin_create_edit_form input[name='username`).prop('disabled', false);
    })

    $(document.body).on("click", ".delete-user-modal-action", function (e) {
        const data_id = $(this).attr("data-id")
        let data = {
            "csrftoken": getCookie('csrftoken')
        }
        Swal.fire({
            title: "Do you want to delete this user permanently?",
            icon: "warning",
            showCloseButton: true,
            showCancelButton: true,
            focusConfirm: true,
            confirmButtonText: '<i class="bi bi-hand-thumbs-up-fill"></i> Yes delete it!',
        }).then(function (isConfirm) {
            if (!isConfirm) {
                return;
            }
            $.ajax({
                type: 'DELETE',
                url: `/core/v1/api/admin/user/${data_id}/`,
                data: data,
                success: function (response) {
                    Swal.fire({
                        title: "User Deletion successful",
                        icon: "success",
                        showConfirmButton: true,
                    })
                    get_ajax(
                        url = $("#users-table").attr("data-url"),
                        data = users_table_filter,
                        on_success = populate_users_table,
                        on_failure = (res) => {
                            console.error(res)
                        },
                    );
                },
                error: function (response) {
                    console.error(response)
                    Swal.fire({
                        title: "User Deletion Failed",
                        text: response.responseJSON["error"],
                        icon: "error",
                        showConfirmButton: true,
                    })
                }
            })
        })
    });


    $("#id_profile").change(function () {
        if ($(this).val() == "Company")
            $("#id_user_company_select").attr("disabled", false)
        else {
            $("#id_user_company_select").val("-1")
            $("#id_user_company_select").attr("disabled", true)
        }
    })

    $("#country-select").change(function (e) {
        e.preventDefault();
        const val = $(this).val();
        users_table_filter.country = val;
        get_ajax(
            url = $("#users-table").attr("data-url"),
            data = users_table_filter,
            on_success = populate_users_table,
            on_failure = (res) => {
                console.error(res)
            },
            // loader_ids = ".heat-map-loader"
        )
    })

    $("#profile-select").change(function (e) {
        e.preventDefault();
        const val = $(this).val();
        users_table_filter.profile = val;
        get_ajax(
            url = $("#users-table").attr("data-url"),
            data = users_table_filter,
            on_success = populate_users_table,
            on_failure = (res) => {
                console.error(res)
            },
            // loader_ids = ".heat-map-loader"
        )
    })

    $("#admin_create_edit_form").submit(function (e) {
        e.preventDefault()
        var values = $(this).serializeArray();
        before_addedit_fn("#submit-user");
        var req_type = $("#submit-user").attr("submit_type")
        if (req_type == "add") {
            post_ajax(
                url = $("#add-user-btn").attr("data-url"),
                data = values,
                on_success = (res) => {
                    if (res.status == "success") {
                        Swal.fire({
                            title: "User is created successfully",
                            icon: "success",
                            showConfirmButton: true,
                        })
                        $('#admin_create_edit_form')[0].reset();
                        $('#add-edit-user-modal').modal('toggle');
                        get_ajax(
                            url = $("#users-table").attr("data-url"),
                            data = users_table_filter,
                            on_success = populate_users_table,
                            on_failure = (res) => {
                                console.error(res)
                            }
                        )
                    } else {
                        Swal.fire({
                            title: `${res.error}`,
                            icon: "error",
                            showConfirmButton: true,
                        })
                    }
                    after_addedit_fn("#submit-user")
                },
                on_failure = (res) => {
                    console.error(res)
                    Swal.fire({
                        title: `${res.responseJSON.error}`,
                        icon: "error",
                        showConfirmButton: true,
                    })
                    after_addedit_fn("#submit-user")
                },
                // loader_id = ".heat-map-loader"
            )
        } else if (req_type == "edit") {
            const dataid = $("#admin_create_edit_form").attr("data-id");
            before_addedit_fn("#submit-user");
            $.ajax({
                type: 'PUT',
                url: `/core/v1/api/admin/user/${dataid}/`,
                data: values,
                success: function (response) {
                    if (response.status == "success") {
                        Swal.fire({
                            title: "User is updated successfully",
                            icon: "success",
                            showConfirmButton: true,
                        })
                        $('#add-edit-user-modal').modal('toggle');
                        get_ajax(
                            url = $("#users-table").attr("data-url"),
                            data = users_table_filter,
                            on_success = populate_users_table,
                            on_failure = (res) => {
                                console.error(res)
                            },
                        );
                    } else {
                        Swal.fire({
                            title: `${response.error}`,
                            icon: "error",
                            showConfirmButton: true,
                        })
                    }
                    after_addedit_fn("#submit-user")
                },
                error: function (response) {
                    console.error(response)
                    Swal.fire({
                        title: "Error editing the user record",
                        text: response.responseJSON.error,
                        icon: "error",
                        showConfirmButton: true,
                    })
                    after_addedit_fn("#submit-user")
                }
            })
        }

    })

    // File type validation
    $("#id_vehicle_image").change(function () {
        var file = this.files[0];
        var fileType = file.type;
        var match = ['image/jpeg', 'image/png', 'image/jpg'];
        if (!((fileType == match[0]) || (fileType == match[1]) || (fileType == match[2]) || (fileType == match[3]) || (fileType == match[4]) || (fileType == match[5]))) {
            Swal.fire({
                title: "Wrong file format",
                text: 'Sorry, only JPG, JPEG, & PNG files are allowed to upload.',
                icon: "error",
                showConfirmButton: true,
            });
            $("#id_vehicle_image").val('');
            return false;
        }
    });

    $("#vehicle_create_edit_form").on('submit', function (e) {
        e.preventDefault();
        var data = new FormData(this);
        before_addedit_fn("#submit-edit-vehicle")
        put_ajax(
            url = $(this).attr("data-url"),
            data = data,
            on_success = (e) => {
                after_addedit_fn("#submit-edit-vehicle");
                Swal.fire({
                    title: `Successfully updated the vehicle`,
                    icon: "success",
                    showConfirmButton: true,
                    focusConfirm: true,
                })
                get_ajax(
                    url = $("#vehicles-table").attr("data-url"),
                    data = {},
                    on_success = populate_vehicles_table,
                    on_failure = (res) => {
                        console.error(res)
                    },
                    // loader_ids = ".heat-map-loader"
                )
                jQuery('#add-edit-vehicle-modal').modal('toggle');
            },
            on_failure = (e) => {
                after_addedit_fn("#submit-edit-vehicle");
                var err_msg = "";
                for (var key in e.responseJSON) {
                    err_msg += `${key}: ${e.responseJSON[key]}\n`
                }
                Swal.fire({
                    title: `Failed due to error. Try Again`,
                    text: err_msg,
                    icon: "error",
                    showConfirmButton: true,
                })
            }
        )
    })

    $('#id_user_search_input').keypress(function () {
        let users = JSON.parse(window.localStorage.getItem("admin-users"))
        var dInput = this.value;
        var re = new RegExp(dInput, "i");
        let filtered_users = users.filter((user) => {
            // console.log(re.test(user.company.name), user.company.name)
            return re.test(user.username) || re.test(user.name) || re.test(user.company.name) || re.test(user.country) || re.test(user.profile)
        })
        populate_users_table(filtered_users, original = false)
    });

    $('#id_company_search_input').keypress(function () {
        let companies = JSON.parse(window.localStorage.getItem("admin-companies"))
        var dInput = this.value;
        var re = new RegExp(dInput, "i");
        let filtered_companies = companies.filter((company) => {
            return re.test(company.name) || re.test(company.email)
        })
        populate_companies_table(filtered_companies, original = false)
    });

    $('#id_Vehicle_search_input').keypress(function () {
        let vehicles = JSON.parse(window.localStorage.getItem("admin-vehicles"))
        var dInput = this.value;
        var re = new RegExp(dInput, "i");
        let filtered_vehicles = vehicles.filter((vehicle) => {
            return re.test(vehicle.name);
        })
        populate_vehicles_table(filtered_vehicles, original = false)
    });


    $(document).on('keypress', '#course_uploaded_table_search', function (e) {
        var dInput = $(this).val();
        let items = JSON.parse(window.localStorage.getItem("course-upload-table-data"))
        var re = new RegExp(dInput, "i");
        let filtered_items = items.filter((item) => {
            return re.test(item.user.username) || re.test(item.user.profile) ||
                re.test(item.course.country) || re.test(item.course.program) ||
                re.test(item.course.event_date) || re.test(item.course.venue) || re.test(item.comment)
        })
        populate_course_upload_table(filtered_items, original = false)
    });

    $(document).on('keypress', '#course_upload_glimpse_search', function (e) {
        var dInput = $(this).val();
        let items = JSON.parse(window.localStorage.getItem("course-upload-glimpse-validate-data"))
        var re = new RegExp(dInput, "i");
        let filtered_items = items.filter((item) => {
            return re.test(item.participant) || re.test(item.company) || re.test(item.vehicle_name) || re.test(item.studentId)
        })
        populate_course_upload_result(filtered_items, original = false)
    });

    $(document).on('click', '.delete-course-upload-modal-action', function (e) {
        let url = $(this).attr("data-url");
        delete_course_upload(url);
    });

    $(document).on('click', '#submit-course-upload', function (e) {
        e.preventDefault();
        let confirm = $("#upload-confirm")
        if (!confirm.is(':checked')) {
            Swal.fire({
                title: "Please check the confirmation",
                icon: "info",
                showCloseButton: true,
                showCancelButton: true,
                focusConfirm: true,
            })
            return false;
        }
        let data_id = $("#course_upload_final_result").attr("data-id")
        let data = {
            instance_id: data_id,
            post: 1,
            reports_base_dir: $("#course_upload_final_result").attr("reports_base_dir"),
            comment: $("#id_upload_comment").val(),
            program: $("#selectProgram").val(),
            company: $("#selectCompany").val(),
            venue: $("#selectLocation").val(),
            course_date: $("#select-event-date span").html(),
        }
        let url = document.getElementById("uploadCourseOffcanvasBottom").getAttribute("data-upload")

        before_addedit_fn('#submit-course-upload')
        Swal.fire({
            title: "Uploading the course!",
            html: swal_upload_course_desc,
            onRender: function () {
                $('.swal2-content').prepend(sweet_loader);
            },
            allowOutsideClick: false,
            showConfirmButton: false,
        });

        post_ajax(
            url = url,
            data = data,
            on_success = (res) => {
                Swal.fire({
                    title: `Successfully uploaded the course`,
                    icon: "success",
                    showConfirmButton: true,
                    focusConfirm: true,
                })
                get_all_admin_ajax()
                populate_course_upload_section()
                jQuery('#uploadCourseOffcanvasBottom').offcanvas('hide');
                after_addedit_fn('#submit-course-upload')
                for (let [key, value] of Object.entries(choicesInstances)) {
                    value.enable()
                }
                document.getElementById('select-event-date').style.pointerEvents = 'auto';
            },
            on_failure = (e) => {
                Swal.fire({
                    title: `Failed due to error. ${e.responseJSON.error}. Try Again`,
                    icon: "error",
                    showConfirmButton: true,
                })
                after_addedit_fn('#submit-course-upload')
                populate_course_upload_section()
                for (let [key, value] of Object.entries(choicesInstances)) {
                    value.enable()
                }
                document.getElementById('select-event-date').style.pointerEvents = 'auto';
            }
        )
    })

    get_ajax(
        url = $("#selectLocation").attr("data-url"),
        data = {},
        on_success = function(res){
            var items = []
            for(var i = 0; i < res.items.length; i++)
                items.push({
                    value: res.items[i].id,
                    label: res.items[i].name,
                    selected: false,
                    disabled: false,
                })
            choicesInstances["Location"] = populate_select_options(items, "selectLocation");
        },
        on_failure = function(res){
            console.error(res)
        }
    )
    get_ajax(
        url = $("#selectProgram").attr("data-url"),
        data = {},
        on_success = function(res){
            var items = []
            for(var i = 0; i < res.items.length; i++)
                items.push({
                    value: res.items[i].id,
                    label: res.items[i].name,
                    selected: false,
                    disabled: false,
                })
            choicesInstances["Program"] = populate_select_options(items, "selectProgram");
        },
        on_failure = function(res){
            console.error(res)
        }
    )
    get_ajax(
        url = $("#selectCompany").attr("data-url"),
        data = {},
        on_success = function(res){
            var items = []
            for(var i = 0; i < res.items.length; i++)
                items.push({
                    value: res.items[i].id,
                    label: res.items[i].name,
                    selected: false,
                    disabled: false,
                })
            choicesInstances["Company"] = populate_select_options(items, "selectCompany");
        },
        on_failure = function(res){
            console.error(res)
        }
    )

    $(function() {
        let today =  moment();
        $('#select-event-date span').html(today.format('MM/DD/YYYY'));
        $('#select-event-date').daterangepicker({
            singleDatePicker: true,
            showDropdowns: true,
            minYear: 2000,
            "minDate": "01/01/2010",
            "maxDate": today.format('MM/DD/YYYY')
        }, function(start, end, label) {
            $('#select-event-date span').html(start.format('MM/DD/YYYY'));
            $('#select-event-date').attr("value", start);
        });
    });
})

function delete_course_upload(url) {
    Swal.fire({
        title: "Do you want to delete this course permanently?",
        icon: "warning",
        showCloseButton: true,
        showCancelButton: true,
        focusConfirm: true,
        confirmButtonText: '<i class="bi bi-hand-thumbs-up-fill"></i> Yes delete it!',
    }).then(function (isConfirm) {
        if (!isConfirm.isConfirmed) {
            return;
        }
        Swal.fire({
            title: "Deleting the course!",
            html: swal_delete_upload_course_desc,
            onRender: function () {
                $('.swal2-content').prepend(sweet_loader);
            },
            allowOutsideClick: false,
            showConfirmButton: false,
        });
        $.ajax({
            type: 'DELETE',
            url: url,
            data: {},
            success: function (response) {
                Swal.fire({
                    title: "Course Deleted successfully",
                    icon: "success",
                    showConfirmButton: true,
                })
                get_all_admin_ajax()

            },
            error: function (response) {
                console.error(response)
                Swal.fire({
                    title: "Course Deletion Failed",
                    text: response.responseJSON.error,
                    icon: "error",
                    showConfirmButton: true,
                })
            }
        })
    })

}


function populate_course_upload_section() {
    $("#course-upload-form-section").html(`
    <div class="row">
        <div id="course_upload_info_list"></div>
    </div>
    <br />
    <div class="row">
        <form id="file-upload-form" class="course-uploader" enctype="multipart/form-data">
            <input id="file-upload" type="file" name="courseFileUpload"
                accept=".zip, .tar.gz, .tgz, .tar.bz2, .tbz, .7z" />
            <label for="file-upload" id="file-drag">
                <h3>
                    <i class="bi bi-file-earmark-check hidden" style="color: green"
                        id="success-upload-icon"></i>
                    <i class="bi bi-file-earmark-excel hidden" style="color: red" id="error-upload-icon"></i>

                </h3>
                <div id="start">
                    <i class="fa fa-download" aria-hidden="true"></i>
                    <div>Select a Zip file or drag here</div>
                    <h1 class="fw-bolder fs-1"><i class="bi bi-upload"></i></h1>
                    <div id="notimage" class="hidden">Please select an appropriate ZIP file</div>
                    <span id="file-upload-btn" class="btn btn-primary"><i
                            class="bi bi-file-earmark-zip-fill"></i> Select a ZIP file</span>
                </div>
                <div id="response" class="hidden">
                    <div id="messages"></div>
                    <progress class="progress" id="file-progress" value="0">
                        <span>0</span>%
                    </progress>
                </div>
            </div>
            </label>
        </form>

        <div id = "course-uploader-loader" class = "hidden" style = "text-align:center;">

        </div>
    </div>

    <div class="row">
        <div id="course_upload_final_result"></div>
    </div>
    `)
    ekUpload();
}

function get_course_upload_table_json(items) {
    content = `
    <table class="table table-responsive table-lg">
        <thead>
            <tr>
                <th>PROGRAM</th>
                <th>EVENT DATE</th>
                <th>UPLOAD</th>
                <th>COMMENT/ERROR</th>
                <th>OPTIONS</th>
            </tr>
        </thead>
        <tbody>
    `
    for (var i = 0; i < items.length; i++) {
        content += `
        <tr data-id = "${items[i].id}">
                
            <td class = "clickable-row" data-href = '${items[i].course.url}'>

               ${items[i].exception.length?'<i class="bi bi-exclamation-octagon-fill" style = "color: red; font-size:24px;"></i>': ''}
                ${items[i].course.program}
                <br />
                <i class="bi bi-geo-alt-fill"></i> ${items[i].course.venue}, ${items[i].course.country}
                
            </td>
            <td >
                ${items[i].course.event_date}
            </td>
            <td>
                By <a href="mailto:${items[i].user.email}">${items[i].user.username}</a>
                <br/>
                at ${items[i].timestamp}
            </td>
            <td >
            ${items[i].comment ? items[i].comment.substring(0, 100): ""}
            ${items[i].exception.length?`<span style = "color: red;"> Course upload failed,<a onclick=show_exception(${i})> see why?</a></span>`: ''}
            </td>
            <td >
            <a href="${items[i].file}">
            <i class="bi bi-file-earmark-arrow-down-fill"></i>
            </a>
            <a style = "color:red" class = 'delete-course-upload-modal-action clickable-row' data-id = "${items[i].id}" data-url = "${items[i].instance_url}">
                <i class="bi bi-trash"></i>
            </a>
            </td>
        </tr>
        `
    }
    content += `</tbody></table>`
    return content
}


function show_exception(itemid) {
    const item = JSON.parse(window.localStorage.getItem("course-upload-table-data"))
    Swal.fire({
        icon: 'error',
        title: 'Oops... Unable to upload the course',
        text: item[itemid].exception,
        customClass: 'swal-wide',
    })
}

function populate_course_upload_table(response, orignal = true) {
    if (orignal) {
        $("#course-upload-table").html(`
            <div class = "row">
                <div class = "search col-4" style = "justify-content: left;">
                    <input type="text" class="form-control filter-input" placeholder="Search Anything here..."  id="course_uploaded_table_search" >
                    <div class="form-control-icon" style = "float:right; margin-top: -30px; margin-right: 10px;">
                        <i class="bi bi-search"></i>
                    </div>
                </div>
                <div class = "pagination col-8" style = "justify-content: right;">
                </div>
            </div>
            <div class = "row">
                <div class = "table_view">
                </div>
            </div>
        `)
        window.localStorage.setItem("course-upload-table-data", JSON.stringify(response.items))
        var items = response.items;
    } else {
        var items = response;
    }
    var container = $('#course-upload-table .pagination')
    var total_length = items.length;
    var page_size = 3;
    var html = get_course_upload_table_json(items.slice(0, page_size))
    $("#course-upload-table .table_view").html(html);

    container.pagination({
        dataSource: items,
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
            var html = get_course_upload_table_json(items.slice(start, end))
            $("#course-upload-table .table_view").html(html);
        }
    })

}

function get_upload_course_glimpse_table(items) {
    content = `
    <table class="table table-responsive table-sm">
        <thead>
            <tr>
                <th>Participant</th>
                <th>Company</th>
                <th>Vehicle</th>
                <th>Stress</th>
                <th data-toggle="tooltip" data-placement="top" title="Slalom|Lane Change|Reverse Slalom">Excercises</th>
                <th>Final Time(sec)</th>
                <th>Final Result</th>
            </tr>
        </thead>
        <tbody>
    `
    for (var i = 0; i < items.length; i++) {
        content += `
        <tr data-id = "${items[i].studentId}">
            <td data-id = "${items[i].studentId}">
            ${items[i].participant}
            ${items[i].IsStudentNew?'<span class="badge bg-success">New</span>':''}
            <a class = "btn btn-sm" href = "${items[i].report_url}" target="_blank">
                 <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-file-earmark-pdf" viewBox="0 0 16 16">
                <path d="M14 14V4.5L9.5 0H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2zM9.5 3A1.5 1.5 0 0 0 11 4.5h2V14a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1h5.5v2z"/>
                <path d="M4.603 14.087a.81.81 0 0 1-.438-.42c-.195-.388-.13-.776.08-1.102.198-.307.526-.568.897-.787a7.68 7.68 0 0 1 1.482-.645 19.697 19.697 0 0 0 1.062-2.227 7.269 7.269 0 0 1-.43-1.295c-.086-.4-.119-.796-.046-1.136.075-.354.274-.672.65-.823.192-.077.4-.12.602-.077a.7.7 0 0 1 .477.365c.088.164.12.356.127.538.007.188-.012.396-.047.614-.084.51-.27 1.134-.52 1.794a10.954 10.954 0 0 0 .98 1.686 5.753 5.753 0 0 1 1.334.05c.364.066.734.195.96.465.12.144.193.32.2.518.007.192-.047.382-.138.563a1.04 1.04 0 0 1-.354.416.856.856 0 0 1-.51.138c-.331-.014-.654-.196-.933-.417a5.712 5.712 0 0 1-.911-.95 11.651 11.651 0 0 0-1.997.406 11.307 11.307 0 0 1-1.02 1.51c-.292.35-.609.656-.927.787a.793.793 0 0 1-.58.029zm1.379-1.901c-.166.076-.32.156-.459.238-.328.194-.541.383-.647.547-.094.145-.096.25-.04.361.01.022.02.036.026.044a.266.266 0 0 0 .035-.012c.137-.056.355-.235.635-.572a8.18 8.18 0 0 0 .45-.606zm1.64-1.33a12.71 12.71 0 0 1 1.01-.193 11.744 11.744 0 0 1-.51-.858 20.801 20.801 0 0 1-.5 1.05zm2.446.45c.15.163.296.3.435.41.24.19.407.253.498.256a.107.107 0 0 0 .07-.015.307.307 0 0 0 .094-.125.436.436 0 0 0 .059-.2.095.095 0 0 0-.026-.063c-.052-.062-.2-.152-.518-.209a3.876 3.876 0 0 0-.612-.053zM8.078 7.8a6.7 6.7 0 0 0 .2-.828c.031-.188.043-.343.038-.465a.613.613 0 0 0-.032-.198.517.517 0 0 0-.145.04c-.087.035-.158.106-.196.283-.04.192-.03.469.046.822.024.111.054.227.09.346z"/>
                </svg>
            </a>
            </td>
            <td >
            ${items[i].company}
            ${items[i].isCompanyNew?'<span class="badge bg-success">New</span>':''}
            </td>
            <td >
            ${items[i].vehicle_name}
            ${items[i].IsNewVehicle?'<span class="badge bg-success">New</span>':''}
            </td>
            <td>
                ${items[i].stress}
            </td>
            <td>
                <span class="badge bg-info" data-toggle="tooltip" data-placement="top" title="Slalom">${items[i].slalom}</span>
                <span class="badge bg-secondary" data-toggle="tooltip" data-placement="top" title="Lane Change">${items[i].LnCh}</span>
                <span class="badge bg-success" data-toggle="tooltip" data-placement="top" title="Reverse Slalom">${items[i].rev_slalom}</span>
            </td>
            <td >
            ${items[i].f_time}
            </td>
            <td >
            ${items[i].final_result}%
            </td>
        </tr>
        `
    }
    content += `</tbody></table>`
    return content
}


function reset_course_upload_section() {
    Swal.fire({
        title: "Do you want to reset?",
        icon: "warning",
        showCloseButton: true,
        showCancelButton: true,
        focusConfirm: true,
        confirmButtonText: '<i class="bi bi-hand-thumbs-up-fill"></i> Yes Reset!',
    }).then(function (isConfirm) {
        if (!isConfirm.isConfirmed) {
            return;
        }
        $.ajax({
            type: 'DELETE',
            url: $("#course_upload_final_result").attr("data-url"),
            data: {},
            success: function (response) {
                console.log(response)
            },
            error: function (response) {
                console.error(response)
            }
        })
        populate_course_upload_section()
    });
}

function populate_course_upload_result(items, gloabl_vars, orignal = true) {
    if (orignal) {
        $("#course_upload_final_result").html(`
        <div class = "course-upload-view">
            <div class = "row">
                <div class = "card">
                    <div class="card-header">
                        <div class="row">
                            <div class="col">
                                <h4 class="card-title">Uploaded Course</h4>
                            </div>
                        </div>
                        <br/>
                        <div class = "row">
                            <div class = "form-group position-relative has-icon-right col-7">
                                <input type="text" class="form-control" placeholder="Search Anything here..."  id="course_upload_glimpse_search" >
                                <div class="form-control-icon" style = "margin-right: 12px;">
                                    <i class="bi bi-search"></i>
                                </div>
                            </div>
                            <div class = "pagination col-5" style = "justify-content: right;">
                            </div>
                        </div>
                    </div>
                    <div class = "card-body">
                        <div class = "row">
                            <div class = "table_view">
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <br/>
            <div class = "row">
                <div class = "uploader-footer">
                    <div class = "form-group">
                        <h6>Comment about upload</h6>
                        <textarea class = "form-control" id = "id_upload_comment"></textarea>
                    </div>
                    <br/>
                    <div class="custom-control custom-checkbox">
                        <input type="checkbox" class="form-check-input form-check-primary form-check-glow" name="customCheck" id="upload-confirm">
                        <label class="form-check-label" for="upload-confirm">I hereby confirm that the course upload is perfectly fine. We can push this course to database.</label>
                    </div>
                </div>
            </div>
            <br/>
            <div style = "margin-bottom: 80px;">
                <button class = "btn btn-outline-primary" id = "submit-course-upload">Upload Course</button>
                <button class = "btn btn-outline-secondary" onclick=reset_course_upload_section();>Reset</button>
            </div>
        </div>
        `)
        window.localStorage.setItem("course-upload-glimpse-validate-data", JSON.stringify(items))
    }

    var container = $('#course_upload_final_result .pagination')
    var total_length = items.length;
    var page_size = 5;
    var html = get_upload_course_glimpse_table(items.slice(0, page_size))
    $("#course_upload_final_result .table_view").html(html);

    container.pagination({
        dataSource: items,
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
            var html = get_upload_course_glimpse_table(items.slice(start, end))
            $("#course_upload_final_result .table_view").html(html);
        }
    })
}

function ekUpload() {
    function Init() {
        var fileSelect = document.getElementById('file-upload'),
            fileDrag = document.getElementById('file-drag'),
            submitButton = document.getElementById('submit-button');

        fileSelect.addEventListener('change', fileSelectHandler, false);

        // Is XHR2 available?
        var xhr = new XMLHttpRequest();
        if (xhr.upload) {
            // File Drop
            fileDrag.addEventListener('dragover', fileDragHover, false);
            fileDrag.addEventListener('dragleave', fileDragHover, false);
            fileDrag.addEventListener('drop', fileSelectHandler, false);
        }
    }

    function fileDragHover(e) {
        var fileDrag = document.getElementById('file-drag');

        e.stopPropagation();
        e.preventDefault();

        fileDrag.className = (e.type === 'dragover' ? 'hover' : 'modal-body file-upload');
    }

    function fileSelectHandler(e) {
        // Fetch FileList object
        var files = e.target.files || e.dataTransfer.files;

        // Cancel event and hover styling
        fileDragHover(e);
        if (files.length > 1) {
            alert("Only one file")
            return false;
        }
        parseFile(files[0]);
        uploadFile(files[0]);
        // for (var i = 0, f; f = files[i]; i++) {
        //     parseFile(f);
        //     uploadFile(f);
        // }
    }

    // Output
    function output(msg) {
        // Response
        var m = document.getElementById('messages');
        m.innerHTML = msg;
    }

    function parseFile(file) {
        $("#course_upload_final_result").html('')
        $("#course_upload_info_list").html('')

        output('<strong>' + file.name + '</strong>');

        // var fileType = file.type;
        var fileName = file.name;

        var isGood = (/\.(?=zip|tar.gz|tgz|tar.bz2|tbz|7z)/gi).test(fileName);
        if (isGood) {
            document.getElementById('start').classList.add("hidden");
            document.getElementById('response').classList.remove("hidden");
            document.getElementById('notimage').classList.add("hidden");
            // Thumbnail Preview
            // document.getElementById('success-upload-icon').classList.remove("hidden");
            // document.getElementById('error-upload-icon').classList.add("hidden");
        } else {
            // document.getElementById('error-upload-icon').classList.remove("hidden");
            // document.getElementById('success-upload-icon').classList.add("hidden");
            document.getElementById('notimage').classList.remove("hidden");
            document.getElementById('start').classList.remove("hidden");
            document.getElementById('response').classList.add("hidden");

            document.getElementById("file-upload-form").reset();
        }
    }

    function setProgressMaxValue(e) {
        var pBar = document.getElementById('file-progress');

        if (e.lengthComputable) {
            pBar.max = e.total;
        }
    }

    function updateFileProgress(e) {
        var pBar = document.getElementById('file-progress');

        if (e.lengthComputable) {
            pBar.value = e.loaded;
        }
    }

    function populate_error(response) {
        $("#course_upload_info_list").html(`
            <div class="alert alert-danger alert-dismissible fade show" role="alert">
            <span>
                <h4 class="alert-heading">Error while uploading data</h4>
                <p>   ${response.error} </p>
                <hr />
                <p class="mb-0">Correct the required files, and re-upload the zip.</p>
            <span>
            </div>
        `)
    }

    function uploadFile(file) {
        output(``);
        var xhr = new XMLHttpRequest(),
            fileInput = document.getElementById('class-roster-file'),
            pBar = document.getElementById('file-progress'),
            fileSizeLimit = 100; // In MB
        if (xhr.upload) {
            // Check if file is less than x MB
            $("#course-uploader-loader").html(`
            <div class="text">
                <br />
                <h5>
                    <span class="words-wrapper">
                    <b class="is-visible">Uploading the course zip file...</b>
                    <b>Reading the course files...</b>
                    <b>Loading the course files...</b>
                    <b>Creating Objects...</b>
                    <b>Creating Dataframes...</b>
                    <b>Manipulating Dataframes...</b>
                    <b>Checking for errors...</b>
                    <b>Creating Artifacts...</b>
                    <b>Creating plots...</b>
                    <b>Generating student reports...</b>
                    <b>Wait a moment...</b>
                    <b>Getting the Glimpse table to show...</b>
                    <b>This will take a while...</b>
                    <b>Taking more time then expected...</b>
                    <b>Wait to complete the process...</b>
                    </span>
                <h5>
            </div>
            `)
            document.getElementById('course-uploader-loader').classList.remove("hidden");
            destroyTextLoader();
            initTextLoader();

            if (file.size <= fileSizeLimit * 1024 * 1024) {
                // Progress bar
                pBar.style.display = 'inline';
                const url = document.getElementById("uploadCourseOffcanvasBottom").getAttribute("data-upload")

                xhr.upload.addEventListener('loadstart', setProgressMaxValue, false);
                xhr.upload.addEventListener('progress', updateFileProgress, false);

                // File received / failed
                output('<strong>' + file.name + '</strong>');

                for (let [key, value] of Object.entries(choicesInstances)) {
                    value.disable()
                }
                document.getElementById('select-event-date').style.pointerEvents = 'none';

                xhr.onreadystatechange = function (e) {
                    if (xhr.readyState == 4) {
                        $("#course_upload_info_list").html('')
                        let response = JSON.parse(xhr.response)
                        if (response.status == "error") {
                            document.getElementById('success-upload-icon').classList.add("hidden");
                            document.getElementById('error-upload-icon').classList.remove("hidden");
                            populate_error(response)
                            $("#file-upload-form")[0].reset()
                            output(`
                                <strong>${file.name}</strong>
                                <br/>
                                <h3 class= "fw-bolder fs-1"><i class="bi bi-upload"></i></h3>
                                <span id="file-upload-btn" class="btn btn-primary"><i class="bi bi-file-earmark-zip-fill"></i> Select a ZIP file</span>
                            `)
                            for (let [key, value] of Object.entries(choicesInstances)) {
                                value.enable()
                            }
                            document.getElementById('select-event-date').style.pointerEvents = 'auto';  
                            document.getElementById('course-uploader-loader').classList.add("hidden");

                        } else if (response.status == "success") {
                            document.getElementById('success-upload-icon').classList.remove("hidden");
                            document.getElementById('error-upload-icon').classList.add("hidden");
                            console.log(response, "in xhr response")
                            items = JSON.parse(response.items)
                            $("#course_upload_final_result").attr("reports_base_dir", items.report_dir)
                            populate_course_upload_result(JSON.parse(items.overall_df), items.gloabl_vars);
                            $("#course_upload_final_result").attr("data-id", response.instance.id)
                            $("#course_upload_final_result").attr("data-url", response.instance.url)
                            document.getElementById('course-uploader-loader').classList.add("hidden");
                        }
                        // Everything is good!
                    }

                };

                

                // Start upload
                xhr.open('POST', url, true);
                var formData = new FormData();
                // let new_fname = Math.random().toString(36).slice(2, 7) + '.' + file.name.split('.').pop();
                let program = $("#selectProgram").val();
                let company = $("#selectCompany").val();
                let venue = $("#selectLocation").val();
                let course_date = $("#select-event-date span").html();

                formData.append("course_date", course_date);
                formData.append("program", program);
                formData.append("venue", venue);
                formData.append("company", company);

                formData.append("file", file);
                formData.append("post", 0);

                xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
                xhr.setRequestHeader('X-File-Name', file.name);
                xhr.setRequestHeader('X-File-Size', file.size);
                // xhr.setRequestHeader('Content-Type', `application/x-www-form-urlencoded`);
                file.csrftoken = getCookie('csrftoken');
                xhr.send(formData);
            } else {
                output('Please upload a smaller file (< ' + fileSizeLimit + ' MB).');
            }
        }
    }

    // Check for the various File API support.
    if (window.File && window.FileList && window.FileReader) {
        Init();
    } else {
        document.getElementById('file-drag').style.display = 'none';
    }

    $(document.body).on("click", "td.clickable-row", function (e) {
        e.preventDefault()
        window.document.location = $(this).attr("data-href");
    });
}

function readURL(input) {
    if (input.files && input.files[0]) {
        const fileSize = input.files[0].size / 1024 / 1024; // in MiB
        if (fileSize > 5) {
            Swal.fire({
                title: "Image size exceed 5MB",
                icon: "warning",
                showConfirmButton: true,
            })
            return false;
        } 
        var reader = new FileReader();
        reader.onload = function(e) {
            $('#vehicle-image-image-preview').css('background-image', 'url('+e.target.result +')');
            $('#vehicle-image-image-preview').hide();
            $('#vehicle-image-image-preview').fadeIn(650);
        }
        reader.readAsDataURL(input.files[0]);
    }
}
$("#id_vehicle_image").change(function() {
    readURL(this);
});

$( "#vehicle-image-icon" ).hover(
    function() {
      $( "#vehicle-image-icon" ).addClass( "bi-file-earmark-arrow-up-fill" );
      $( "#vehicle-image-icon" ).removeClass( "bi-image-fill" );
    }, function() {
      $( "#vehicle-image-icon" ).removeClass( "bi-file-earmark-arrow-up-fill" );
      $( "#vehicle-image-icon" ).addClass( "bi-image-fill" );
    }
  );