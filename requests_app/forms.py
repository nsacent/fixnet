from django import forms
from .models import ServiceRequest


class ServiceRequestForm(forms.ModelForm):
    class Meta:
        model = ServiceRequest
        fields = [
            "client_name",
            "category",
            "title",
            "description",
            "location",
            "phone_number",
            "image",
            "priority",
        ]

        widgets = {
            "client_name": forms.TextInput(attrs={
                "class": "w-full bg-slate-100 text-slate-800 px-4 py-4 rounded-2xl outline-none text-sm",
                "placeholder": "Your name"
            }),
            "category": forms.Select(attrs={
                "class": "w-full bg-slate-100 text-slate-800 px-4 py-4 rounded-2xl outline-none text-sm"
            }),
            "title": forms.TextInput(attrs={
                "class": "w-full bg-slate-100 text-slate-800 px-4 py-4 rounded-2xl outline-none text-sm",
                "placeholder": "Example: WiFi not working"
            }),
            "description": forms.Textarea(attrs={
                "class": "w-full bg-slate-100 text-slate-800 px-4 py-4 rounded-2xl outline-none text-sm",
                "placeholder": "Describe the issue in detail",
                "rows": 4
            }),
            "location": forms.TextInput(attrs={
                "class": "w-full bg-slate-100 text-slate-800 px-4 py-4 rounded-2xl outline-none text-sm",
                "placeholder": "Example: Ntinda, Kampala"
            }),
            "phone_number": forms.TextInput(attrs={
                "class": "w-full bg-slate-100 text-slate-800 px-4 py-4 rounded-2xl outline-none text-sm",
                "placeholder": "Example: 0700000000"
            }),
            "image": forms.ClearableFileInput(attrs={
                "class": "w-full bg-white text-slate-800 px-4 py-3 rounded-2xl outline-none text-sm border border-slate-200"
            }),
            "priority": forms.Select(attrs={
                "class": "w-full bg-slate-100 text-slate-800 px-4 py-4 rounded-2xl outline-none text-sm"
            }),
        }


class ClientPaymentProofForm(forms.Form):
    payment_proof = forms.ImageField(
        required=True,
        widget=forms.ClearableFileInput(attrs={
            "class": "mt-2 w-full bg-white px-4 py-3 rounded-xl outline-none border border-slate-200"
        })
    )


class CancelRequestForm(forms.Form):
    cancellation_reason = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            "class": "mt-2 w-full bg-slate-100 px-4 py-3 rounded-xl outline-none",
            "rows": 4,
            "placeholder": "Tell us why you want to cancel this request..."
        })
    )