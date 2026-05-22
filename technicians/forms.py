from django import forms
from .models import TechnicianProfile


class TechnicianProfileForm(forms.ModelForm):
    class Meta:
        model = TechnicianProfile
        fields = [
            "profile_photo",
            "business_name",
            "bio",
            "skills",
            "service_area",
            "experience_level",
            "availability_status",

        ]

        widgets = {
            "business_name": forms.TextInput(attrs={
                "class": "mt-2 w-full bg-slate-100 px-4 py-3 rounded-xl outline-none",
                "placeholder": "Example: Vimbah Network Solutions"
            }),
            "bio": forms.Textarea(attrs={
                "class": "mt-2 w-full bg-slate-100 px-4 py-3 rounded-xl outline-none",
                "rows": 4,
                "placeholder": "Briefly describe your experience..."
            }),
            "skills": forms.Textarea(attrs={
                "class": "mt-2 w-full bg-slate-100 px-4 py-3 rounded-xl outline-none",
                "rows": 4,
                "placeholder": "Example: WiFi repair, CCTV installation, LAN cabling, router setup"
            }),
            "service_area": forms.TextInput(attrs={
                "class": "mt-2 w-full bg-slate-100 px-4 py-3 rounded-xl outline-none",
                "placeholder": "Example: Kampala, Ntinda, Nakawa"
            }),
            "experience_level": forms.Select(attrs={
                "class": "mt-2 w-full bg-slate-100 px-4 py-3 rounded-xl outline-none"
            }),
            "profile_photo": forms.ClearableFileInput(attrs={
                "class": "mt-2 w-full bg-white px-4 py-3 rounded-xl outline-none border border-slate-200"
            }),
            "availability_status": forms.Select(attrs={
                "class": "mt-2 w-full bg-slate-100 px-4 py-3 rounded-xl outline-none"
            }),
        }