from django import forms
from technicians.models import TechnicianProfile
from requests_app.models import ServiceRequest


class TechnicianChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        rating = obj.average_rating or 0
        service_area = obj.service_area or "No area set"
        availability = obj.get_availability_status_display()

        return f"{obj.user.username} — {service_area} — ★ {rating} — {availability}"


class AssignTechnicianForm(forms.Form):
    technician = TechnicianChoiceField(
        queryset=TechnicianProfile.objects.filter(
            is_verified=True,
            availability_status=TechnicianProfile.AVAILABILITY_AVAILABLE,
        ).select_related("user"),
        empty_label="Select verified available technician",
        widget=forms.Select(attrs={
            "class": (
                "mt-2 w-full appearance-none bg-white border border-slate-200 "
                "text-slate-800 px-4 py-4 pr-12 rounded-2xl outline-none "
                "focus:border-blue-500 focus:ring-4 focus:ring-blue-50 "
                "text-sm font-semibold shadow-sm"
            )
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

    platform_commission_percent = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        min_value=0,
        max_value=100,
        widget=forms.NumberInput(attrs={
            "class": "mt-2 w-full bg-slate-100 px-4 py-3 rounded-xl outline-none",
            "placeholder": "Example: 20"
        })
    )

class UpdatePaymentForm(forms.Form):
    payment_status = forms.ChoiceField(
        choices=ServiceRequest.PAYMENT_STATUS_CHOICES,
        widget=forms.Select(attrs={
            "class": "mt-2 w-full bg-slate-100 px-4 py-3 rounded-xl outline-none"
        })
    )

    payment_method = forms.ChoiceField(
        choices=[("", "Select payment method")] + list(ServiceRequest.PAYMENT_METHOD_CHOICES),
        required=False,
        widget=forms.Select(attrs={
            "class": "mt-2 w-full bg-slate-100 px-4 py-3 rounded-xl outline-none"
        })
    )

    amount_paid = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=0,
        widget=forms.NumberInput(attrs={
            "class": "mt-2 w-full bg-slate-100 px-4 py-3 rounded-xl outline-none",
            "placeholder": "Amount paid"
        })
    )

    payment_note = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "class": "mt-2 w-full bg-slate-100 px-4 py-3 rounded-xl outline-none",
            "rows": 4,
            "placeholder": "Transaction reference, MoMo number, receipt note..."
        })
    )

    payment_proof = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            "class": "mt-2 w-full bg-white px-4 py-3 rounded-xl outline-none border border-slate-200"
        })
    )

    payment_proof_status = forms.ChoiceField(
        choices=ServiceRequest.PAYMENT_PROOF_STATUS_CHOICES,
        widget=forms.Select(attrs={
            "class": "mt-2 w-full bg-slate-100 px-4 py-3 rounded-xl outline-none"
        })
    )


class UpdateTechnicianPayoutForm(forms.Form):
    technician_payout_status = forms.ChoiceField(
        choices=ServiceRequest.PAYOUT_STATUS_CHOICES,
        widget=forms.Select(attrs={
            "class": "w-full"
        })
    )

    technician_payout_method = forms.ChoiceField(
        choices=[("", "Select payout method")] + list(ServiceRequest.PAYOUT_METHOD_CHOICES),
        required=False,
        widget=forms.Select(attrs={
            "class": "w-full"
        })
    )

    technician_payout_note = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "class": "mt-2 w-full bg-slate-100 px-4 py-3 rounded-xl outline-none",
            "rows": 4,
            "placeholder": "Payout reference, MoMo number, bank reference..."
        })
    )

