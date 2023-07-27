
function get_course_vehicles_content(items){
    var content = ""
    for(var i = 0; i < items.length; i++){
        content += `
        <div class = "row">
            <h6 class = "fw-bold">${items[i].name}</h6>
            <div class="col-xxl-5 col-xl-5 col-lg-5 col-md-5 col-sm-5 text-left" data-id = "${items[i].id}">
                <img src="${items[i].image}" class="img-fluid" />
            </div>
            <div class="col-xxl-7 col-xl-7 col-lg-7 col-md-7 col-sm-7 text-right">
                <span class = "fw-bold">                    
                <span class="language-en">
                    Lat Acc Capability: 
                </span>
                <span class="language-es">
                    Capacidad de Acc Lat:
                </span>
            </span> ${items[i].lat_acc}
                <br/>
                <span class = "fw-bold">
                    <span class="language-en">
                        Slalom Top Speed: 
                    </span>
                    <span class="language-es">
                        Maxima Velocidad en Slalom:
                    </span>
                </span>${items[i].top_speed_slalom}MPH</span> 
                <br/>
                <span class = "fw-bold">
                    <span class="language-en">
                        Barricade Top Speed: 
                    </span>
                    <span class="language-es">
                        Maxima Velocidad en Barricada:
                    </span>
                </span>${items[i].top_speed_lnch}MPH</span>
            </div>
        </div>
        `
    }
    return content;

}

function populate_course_vehicles(res, orignal = false){
    var container = $('#vehicles-table-pagination')
    var total_length = res.items.length;
    var page_size = 1;
    container.pagination({
        showPageNumbers: false,
        showNavigator: true,
        showFirstOnEllipsisShow: false,
        pageRange: 1,
        dataSource: res.items,
        className: 'paginationjs-theme-grey paginationjs',
        pageSize: page_size,
        callback: function (data, pagination) {
            let start = (pagination.pageNumber - 1) * page_size;
            let end = (pagination.pageNumber) * page_size;
            if (total_length < end) end = total_length
            var html = get_course_vehicles_content(res.items.slice(start, end))
            $("#vehicles-table").html(html);
            set_language_strings();
        }
    })
}

get_ajax(
    url = $("#vehicles-table").attr("data-url"),
    data = {},
    on_success = populate_course_vehicles,
    on_failure = (res) => {
        console.error(res)
    },
    // loader_ids = ".heat-map-loader"
)


function get_comment_content(items){
    var comments_content = ''
    const img_src = $("#comments-table").attr('img-src');
    for(var i = 0; i < items.length; i++){
        let short_comment = items[i].comment.substring(0, 80)
        comments_content += `
        <div class="recent-message d-flex px-4 py-3">
            <div class="avatar">
                <img src="${img_src}">
            </div>
            <div class="name ms-4">
                <p class="mb-1 fw-bold">${items[i].participant}</p>
                <p class="fw-lighter lh-sm fs-6 text-break text-muted mb-0" 
                    id = "comment-sm-${items[i].id}">
                    ${short_comment}
                    <a data-id="${items[i].id}" href="#" 
                        class="show-hide-btn fs-6 text-muted"><u>
                        <span class="language-en">
                            Read more
                        </span>
                        <span class="language-es">
                            Leer Más
                        </span>
                    </u></a>
                </p>
                <p class="fw-lighter lh-sm fs-6 text-break text-muted mb-0" style="display:none;" 
                    id = "comment-lg-${items[i].id}">
                    ${items[i].comment} 
                    <br/>
                    <a data-id="${items[i].id}" href="#" class="show-hide-btn text-muted"><u>
                        <span class="language-en">
                            Read Less
                        </span>
                        <span class="language-es">
                            Leer Menos
                        </span>
                    </u></a>
                </p>
            </div>
        </div>`
    }

    return comments_content;

}

function populate_comments(res, orignal = false){
    var container = $('#comments-table-pagination')
    var total_length = res.items.length;
    var page_size = 2;
    container.pagination({
        showPageNumbers: false,
        showNavigator: true,
        showFirstOnEllipsisShow: false,
        pageRange: 1,
        dataSource: res.items,
        className: 'paginationjs-theme-grey paginationjs',
        pageSize: page_size,
        callback: function (data, pagination) {
            let start = (pagination.pageNumber - 1) * page_size;
            let end = (pagination.pageNumber) * page_size;
            if (total_length < end) end = total_length
            var html = get_comment_content(res.items.slice(start, end))
            $("#comments-table .content").html(html);
            set_language_strings();
        }
    })
}

get_ajax(
    url = $("#comments-table").attr("data-url"),
    data = {},
    on_success = populate_comments,
    on_failure = (res) => {
        console.error(res)
    },
    // loader_ids = ".heat-map-loader"
)
