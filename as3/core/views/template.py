from django.views.generic import TemplateView
from django.shortcuts import render
from django.views.defaults import page_not_found, bad_request, permission_denied, server_error

def handler404(request, exception = None):
    # return page_not_found(request, None)
    return render(request, "pages/errors/404.html", {})

def handler400(request, exception = None):
    # return bad_request(request, None)
    return render(request, "pages/errors/400.html", {})

def handler403(request, exception = None):
    print(exception)
    # return permission_denied(request, None)
    return render(request, "pages/errors/403.html", {})

def handler500(request, exception = None):
    # return server_error(request, None)
    return render(request, "pages/errors/500.html", {})
