function set_loader_gif(loaderids, display_type){
    for(var i = 0; i < loaderids.length; i++){
        $(`${loaderids[i]} .pre-loader`).css("display", display_type)
        $(loaderids[i]).css("display", display_type)
    } 
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

$.ajaxSetup({ 
    beforeSend: function(xhr, settings) {
        if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
            // Only send the token to relative URLs i.e. locally.
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    } 
});

function get_ajax(url, data, on_success, on_failure, loader_ids = [], display_type = "block", before_fn = undefined, after_fn = undefined) {
    set_loader_gif(loader_ids, display_type)
    if(before_fn) before_fn()
    url = url.replace(/^\s+|\s+$/g, '');

    $.ajax({
        type: 'GET',
        url: url,
        data: data,
        success: function (response) {
            on_success(response);
            set_loader_gif(loader_ids, "none");
            if(after_fn)  after_fn();
        },
        error: function (response) {
            on_failure(response);
            set_loader_gif(loader_ids, "none");
            if(after_fn) after_fn();
        }
    })
}


function post_ajax(url, data, on_success, on_failure) {
    url = url.replace(/^\s+|\s+$/g, '');
    $.ajax({
        type: 'POST',
        url: url,
        data: data,
        traditional: true,
        beforesend: function(response){

        },
        success: function (response) {
            on_success(response);
        },
        error: function (response) {
            on_failure(response);
        }
    })
}
function imageExists(image_url){

    var http = new XMLHttpRequest();

    http.open('HEAD', image_url, false);
    http.send();

    return http.status != 404;

}


function put_ajax(url, data, on_success, on_failure) {
    url = url.replace(/^\s+|\s+$/g, '');
    $.ajax({
        type: 'PUT',
        url: url,
        data: data,
        cache:false,
        contentType: false,
        processData: false,
        beforesend: function(response){

        },
        success: function (response) {
            on_success(response);
        },
        error: function (response) {
            on_failure(response);
        }
    })
}



$("#language-select").change(function (e) {
    e.preventDefault()
    const language = $(this).val()
    const url = $(this).attr("data-url")
    window.localStorage.setItem(key = "language", value = language);
    set_language_strings();

    const send_data = {
        "language": language,
    }
    post_ajax(url, send_data, (res) => {
        console.log(res)
    }, (res) => {
        console.log(res)
    })
    let students_res = window.localStorage.getItem(`students-api-response-${$("#page-header").attr("data-id")}`);
    if(students_res){
        student_performers_on_success(JSON.parse(students_res), false)
    }
    let performance_activities_res = window.localStorage.getItem(`activities-result-${$("#page-header").attr("data-id")}`);
    if(performance_activities_res){
        performance_activities_on_success(JSON.parse(performance_activities_res), false)
    }
    let scatter_perf_res = window.localStorage.getItem(`scatter-perf-${$("#page-header").attr("data-id")}`);
    if(scatter_perf_res){
        perf_scatter_plt_on_success(JSON.parse(scatter_perf_res), false)
    }
    let averages_res = window.localStorage.getItem(`averages-response-${$("#page-header").attr("data-id")}`);
    if(averages_res){
        performer_averages_on_success(JSON.parse(averages_res), false)
    }
    
})

function set_language_strings(){
    let language = window.localStorage.getItem("language")
    if (!language) {
        language = "en"
        window.localStorage.setItem(key = "language", value = language);
    }
    $("#language-select").val(language);
    if (language == "es") {
        $(`.language-es`).css("display", "inline-block")
        $(`.language-en`).css("display", "none")

        $(`.language-en`).hide()
        $(`.language-es`).show()
    } else if (language == "en") {
        $(`.language-en`).css("display", "inline-block")
        $(`.language-es`).css("display", "none")

        $(`.language-es`).hide()
        $(`.language-en`).show()
    }
}

function getPathFromUrl(url) {
    return url.split("?")[0];
}

function getParameterByName(url, name) {
    var match = RegExp('[?&]' + name + '=([^&]*)').exec(url);
    return match && decodeURIComponent(match[1].replace(/\+/g, ' '));
}


function global_company_report_download(url, filters = {}){
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
    $.ajax({
        url: url,
        type: "GET",
        data: filters,
        xhrFields: {
            responseType: 'blob'
        },
        success: function (returnhtml, textStatus, request) {
            console.log(typeof (returnhtml))
            //$("#loader").hide(); // hides loading sccreen in success call back
            Swal.fire({
                title: "Report generated successfully!",
                icon: "success",
                showConfirmButton: true,
                // timer: 1000
            }).then(function () {
                const fname = request.getResponseHeader('filename')
                var a = document.createElement('a');
                var binaryData = [];
                binaryData.push(returnhtml);
                var url = window.URL.createObjectURL(new Blob(binaryData, {
                    type: "application/pdf"
                }))
                a.href = url;
                a.download = fname;
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
    $("#global-report-download-modal").modal("hide")
}

$(document.body).on("click", "tr.clickable-row", function (e) {
    e.preventDefault()
    window.document.location = $(this).attr("data-href");
});

$(document.body).on("click", ".show-hide-btn", function (e) {
    e.preventDefault()
    var id = $(this).data("id");
    $("#comment-sm-" + id).toggle();
    $("#comment-lg-" + id).toggle();
})



var isLast = function(word) {
    return $(word).next().length > 0 ? false : true;
  }
  
  var getNext = function(word) {
    return $(word).next();
  }
  
  var getVisible = function () {
    return document.getElementsByClassName('is-visible');
  }
  
  var getFirst =  function() {
    var node = $('.words-wrapper').children().first();
    return node;
  }
  
  var switchWords = function(current, next) {
    $(current).removeClass('is-visible').addClass('is-hidden');
    $(next).removeClass('is-hidden').addClass('is-visible');
  }
  
  var loaderGetStarted = function() {
    //We start by getting the visible element and its sibling
    var first = getVisible();
    var next = getNext(first);
    if(isLast(next)){
        return false;
    }
    //If our element has a sibling, it's not the last of the list. We switch the classes
    if (next.length !== 0) {
       switchWords(first,next);
    } else {
      
      //The element is the last of the list. We remove the visible class of the current element
      $(first).removeClass('is-visible').addClass('is-hidden');
      
      //And we get the first element of the list, and we give it the visible class. And it starts again.
      var newEl = getFirst();
      $(newEl).removeClass('is-hidden').addClass('is-visible');
    }
    
  }
  var textLoaderNowPlaying = undefined;
  var initTextLoader = function() {
    textLoaderNowPlaying = setInterval(function() {loaderGetStarted()}, 4500);
  }
  var destroyTextLoader = function(){
    if(textLoaderNowPlaying)
        clearInterval(textLoaderNowPlaying);
  }
  
  