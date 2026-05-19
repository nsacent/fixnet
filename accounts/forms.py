from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


INPUT_CLASS = "mt-2 w-full bg-slate-100 px-4 py-3 rounded-xl outline-none"


class ClientRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            "class": INPUT_CLASS,
            "placeholder": "Email address"
        })
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "phone_number",
            "district",
            "password1",
            "password2",
        ]

        widgets = {
            "username": forms.TextInput(attrs={
                "class": INPUT_CLASS,
                "placeholder": "Username"
            }),
            "phone_number": forms.TextInput(attrs={
                "class": INPUT_CLASS,
                "placeholder": "Phone number"
            }),
            "district": forms.TextInput(attrs={
                "class": INPUT_CLASS,
                "placeholder": "District / Area"
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["password1"].widget.attrs.update({
            "class": INPUT_CLASS,
            "placeholder": "Password"
        })
        self.fields["password2"].widget.attrs.update({
            "class": INPUT_CLASS,
            "placeholder": "Confirm password"
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.ROLE_CLIENT
        user.email = self.cleaned_data["email"]

        if commit:
            user.save()

        return user


class TechnicianRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            "class": INPUT_CLASS,
            "placeholder": "Email address"
        })
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "phone_number",
            "district",
            "password1",
            "password2",
        ]

        widgets = {
            "username": forms.TextInput(attrs={
                "class": INPUT_CLASS,
                "placeholder": "Username"
            }),
            "phone_number": forms.TextInput(attrs={
                "class": INPUT_CLASS,
                "placeholder": "Phone number"
            }),
            "district": forms.TextInput(attrs={
                "class": INPUT_CLASS,
                "placeholder": "District / Area"
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["password1"].widget.attrs.update({
            "class": INPUT_CLASS,
            "placeholder": "Password"
        })
        self.fields["password2"].widget.attrs.update({
            "class": INPUT_CLASS,
            "placeholder": "Confirm password"
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.ROLE_TECHNICIAN
        user.email = self.cleaned_data["email"]

        if commit:
            user.save()

        return user