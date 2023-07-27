get_ajax(
    url = $("#courses-table").attr("data-href"),
    data = {},
    on_success = populate_courses_table,
    on_failure = (e) => console.error(e),
    loader_ids = [".course-table-gif"]
);

function get_expired_certificates_content(rows) {
    table_content = ""
    for (var i = 0; i < rows.length; i++) {
        var d =  rows[i].event_date

        table_content += `<tr>
        <td class="col-auto">
            ${rows[i].name}
        </td>
        <td class="col-auto">
           ${d}
        </td>
    </tr>`
    }
    return table_content;
}

function expired_certificates_onsuccess(res) {
    $("#expired_certificates_count").html(res.last_18_months_students_count)

    if (res.expired_certificates.length == 0) {
        $("#expired_certificates_table").html(
            `<p>
            <span class="language-en">
                No Certificates are expired
            </span>
            <span class="language-es">
                No hay certificados por expirar
            </span>
        </p>`
        )
    } else {

        var container = $('#exp-cert-table-pagination')
        var total_length = res.expired_certificates.length;
        var page_size = 5;
        var html = get_expired_certificates_content(res.expired_certificates.slice(0, page_size))
        $("#expired_certificates_table tbody").html(html);
        // $("#card_total_courses_count").html(res.items.length)

        container.pagination({
            dataSource: res.expired_certificates,
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
                var html = get_expired_certificates_content(res.expired_certificates.slice(start, end))
                $("#expired_certificates_table tbody").html(html);
            }
        })
    }

    if (res.to_be_expired_certificates.length == 0) {
        $("#tobe_expired_certificates_table").html(
            `<p>
            <span class="language-en">
                No Certificates about to Expire
            </span>
            <span class="language-es">
                No hay certificados por expirar
            </span>
        </p>`
        )
    } else {
        container = $('#exp-about-cert-table-pagination')
        total_length = res.to_be_expired_certificates.length;
        page_size = 5;
        html = get_expired_certificates_content(res.to_be_expired_certificates.slice(0, page_size))
        $("#tobe_expired_certificates_table tbody").html(html);
        // $("#card_total_courses_count").html(res.items.length)

        container.pagination({
            dataSource: res.to_be_expired_certificates,
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
                html = get_expired_certificates_content(res.to_be_expired_certificates.slice(start, end))
                $("#tobe_expired_certificates_table tbody").html(html);
            }
        })
    }


}

get_ajax(
    url = $("#expired-certificates").attr("data-url"),
    data = {},
    on_success = expired_certificates_onsuccess,
    on_failure = (e) => console.error(e),
    loader_ids = [".overview-exp-loader"]
);

function get_course_table_content(courses) {
    var table_content = ``
    for (var i = 0; i < courses.length; i++) {
        table_content += `<tr class='clickable-row' 
            data-href="${courses[i].detail_url}">
            <td class="col-auto">
                ${courses[i].program.name}
            </td>
            <td class="col-auto">
                ${courses[i].venue.name} 
                ${courses[i].venue.country.name ? " | " + courses[i].venue.country.name:""}
            </td>
            <td class="col-auto">
                ${courses[i].event_date}
            </td>
        </tr>`
    }
    return table_content;
}

function populate_courses_table(res){
    var container = $('#course-table-pagination')
    var total_length = res.items.length;

    var page_size = 5;
    var html = get_course_table_content(res.items.slice(0, page_size))
    $("#courses-table tbody").html(html);  

    container.pagination({
        dataSource: res.items,
        showPageNumbers: false,
        showNavigator: true,
        showFirstOnEllipsisShow: false,
        className: 'paginationjs-theme-grey paginationjs',
        pageSize: page_size,
        callback: function(data, pagination) {
            let start = (pagination.pageNumber-1)*page_size;
            let end = (pagination.pageNumber)*page_size;
            if (total_length < end) end = total_length
            var html = get_course_table_content(res.items.slice(start, end))
            $("#courses-table tbody").html(html);    
        }
    }) 
}
