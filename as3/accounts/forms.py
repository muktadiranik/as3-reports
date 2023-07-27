from django.contrib.auth import authenticate
from django import forms
from as3.core.models import Companies, Users
from as3.core.models.base import CompanyUsers
from ..core.models.records import DataFinalExerciseComputed


class CompanyUserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput,)

    def __init__(self, *args, **kwargs):
        super(CompanyUserLoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control form-control-xl',
            'placeholder': "Username/Email",
            "name": "username"})
        self.fields['password'].widget.attrs.update({
            'class': 'form-control form-control-xl',
            'placeholder': "Password",
            "name": "password"})

    def clean(self, *ar, **kw):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        if username and password:
            user = authenticate(username=username, password=password)
            if not user and Users.objects.filter(email=username).exists():
                _username = Users.objects.get(email=username).username
                user = authenticate(username=_username, password=password)
            if not user:
                raise forms.ValidationError(
                    "Username/Password combination is invalid.")
            if not user.active:
                raise forms.ValidationError("User is no longer active.")
            # if not CompanyUsers.objects.filter(idUser=user).exists():
            #     raise forms.ValidationError(
            #         "No company found. Contact techincal support.")

            # company_instance = CompanyUsers.objects.get(idUser=user).idCompany
            # final_report = DataFinalExerciseComputed.objects.select_related(
            #     "idParticipation").filter(idParticipation__idCompany=company_instance)
            # if not final_report.exists():
            #     raise forms.ValidationError(
            #         f"No report found for company({company_instance.name}). Contact techincal support.")

        return self.cleaned_data


class AdminUserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput,)

    def __init__(self, *args, **kwargs):
        super(AdminUserLoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control form-control-xl',
            'placeholder': "Username/Email",
            "name": "username"})
        self.fields['password'].widget.attrs.update({
            'class': 'form-control form-control-xl',
            'placeholder': "Password",
            "name": "password"})

    def clean(self, *ar, **kw):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        if username and password:
            user = authenticate(username=username, password=password)
            if not user and Users.objects.filter(email=username).exists():
                _username = Users.objects.get(email=username).username
                user = authenticate(username=_username, password=password)
            if not user:
                raise forms.ValidationError(
                    "Username/Password combination is invalid.")
            if not user.active:
                raise forms.ValidationError("User is no longer active.")
            try:
                puser = Users.objects.get(id=user.id)
                if not puser.is_superadmin_or_admin:
                    raise forms.ValidationError(
                        f"You are authenticated as {username}, but are not authorized to access this page. Would you like to login to a different account?")
            except Users.DoesNotExist:
                raise forms.ValidationError(
                    f"No user found with provided username.")

        return self.cleaned_data
