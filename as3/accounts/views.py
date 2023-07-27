from as3.accounts.forms import AdminUserLoginForm, CompanyUserLoginForm
from as3.core.models import Users
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.db.models.query_utils import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views import View
from django.conf import settings
from django.shortcuts import render, get_object_or_404


class LoginView(View):
    @staticmethod
    def formclass(namespace):
        if namespace == 'company-accounts':
            return CompanyUserLoginForm
        elif namespace == 'admin-accounts':
            return AdminUserLoginForm
        
    @staticmethod
    def template(namespace):
        if namespace == 'company-accounts':
            return "accounts/company/login.html"
        elif namespace == 'admin-accounts':
            return "accounts/admin/login.html"
           
    def get(self, request, *_, **__):
        namespace = self.request.resolver_match.namespace
        if request.user.is_authenticated:
            return redirect("/")
        form = self.formclass(namespace)(request.POST or None)
        return render(request, self.template(namespace), {"form" : form})
    
    def post(self, request, *_, **__):
        namespace = self.request.resolver_match.namespace
        form = self.formclass(namespace)(request.POST or None)
        
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username = username, password = password)
            if not user and Users.objects.filter(email = username).exists():
                _username = Users.objects.get(email = username).username
                user = authenticate(username = _username, password = password)
            if not user:
                return render(request, self.template(namespace), {"form" : form}) 
            login(request, user)
            puser = get_object_or_404(Users, id = user.id)
            if puser.is_superadmin_or_admin:
                request.session["user-type"] = "admin"
                return redirect("core:admin:admin_index")
            else:
                request.session["user-type"] = "company"
                return redirect("core:index")
        else:
            return render(request, self.template(namespace), {"form" : form}) 
        
def logout_view(request):
    user_type = request.session.get("user-type")
    logout(request)
    if user_type == 'admin':
        return HttpResponseRedirect("/admin")
    return HttpResponseRedirect("/")


@login_required(login_url='/accounts/login/')
def profile_view(request):
	return HttpResponseRedirect("/")


def password_reset_request(request):
    ns = request.resolver_match.namespaces
    if ns and ns[0] != 'company-accounts':
        return redirect(reverse(f"{ns[0]}:login")) 
    
    template_name = "accounts/password/password_reset.html"
    
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            try:
                user = Users.objects.get(email=data)
            except Users.DoesNotExist as e:
                return HttpResponse('Invalid header found. {}'.format(e))
            
            if user.idCountry.name == "MX":
                email_template_name = "accounts/email/[es]password_reset_email.html"
                subject = "Restablece tu contraseña"
            else:
                email_template_name = "accounts/email/[en]password_reset_email.html"
                subject = "Reset your password"
            
            c = {
                "email":user.email,
                'domain':settings.DOMAIN,
                'site_name': 'as3international',
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "user": user,
                'token': default_token_generator.make_token(user),
                'protocol': 'http',
            }
            user.send_email.delay(
                subject = subject,
                html_content = render_to_string(email_template_name, c),
                to_emails= user.email,
            )
            return redirect (reverse("company-accounts:password_reset_done"))
                        
    password_reset_form = PasswordResetForm()
    return render(request, template_name, context={"password_reset_form":password_reset_form})
    
    