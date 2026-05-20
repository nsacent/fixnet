from django import forms
from technicians.models import TechnicianProfile
from requests_app.models import ServiceRequest


class AssignTechnicianForm(forms.Form):
    technician = forms.ModelChoiceField(
        queryset=TechnicianProfile.objects.filter(is_verified=True),
        empty_label="Select verified technician",
        widget=forms.Select(attrs={
            "class": "mt-2 w-full bg-slate-100 px-4 py-3 rounded-xl outline-none"
        })
    )


class UpdateRequestStatusForm(forms.Form):
    status = forms.ChoiceField(
        choices=ServiceRequest.STATUS_CHOICES,
        widget=forms.Select(attrs={
            "class": "mt-2 w-full bg-slate-100 px-4 py-3 rounded-xl outline-none"
        })
    )

class UpdateAdminNotesForm(forms.Form):
    admin_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "class": "mt-2 w-full bg-slate-100 px-4 py-3 rounded-xl outline-none",
            "rows": 5,
            "placeholder": "Write internal admin notes here..."
        })
    )

class UpdateFinalPriceForm(forms.Form):
    final_price = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=0,
        widget=forms.NumberInput(attrs={
            "class": "mt-2 w-full bg-slate-100 px-4 py-3 rounded-xl outline-none",
            "placeholder": "Enter final price"
        })
    )

    price_note = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "class": "mt-2 w-full bg-slate-100 px-4 py-3 rounded-xl outline-none",
            "rows": 4,
            "placeholder": "Explain the final price if different from estimate..."
        })
    )