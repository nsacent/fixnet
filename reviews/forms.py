from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = [
            "rating",
            "comment",
        ]

        widgets = {
            "rating": forms.Select(
                choices=[
                    (1, "1 - Poor"),
                    (2, "2 - Fair"),
                    (3, "3 - Good"),
                    (4, "4 - Very Good"),
                    (5, "5 - Excellent"),
                ],
                attrs={
                    "class": "w-full bg-slate-100 px-4 py-3 rounded-xl outline-none"
                }
            ),
            "comment": forms.Textarea(attrs={
                "class": "w-full bg-slate-100 px-4 py-3 rounded-xl outline-none",
                "rows": 4,
                "placeholder": "Write your feedback about the technician..."
            }),
        }