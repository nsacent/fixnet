from datetime import datetime, timedelta

from django.utils import timezone


def get_report_date_range(request, default_filter="this_month"):
    today = timezone.localdate()

    date_filter = request.GET.get("date_filter", default_filter)
    start_date_input = request.GET.get("start_date", "")
    end_date_input = request.GET.get("end_date", "")

    start_date = None
    end_date = None

    if date_filter == "today":
        start_date = today
        end_date = today

    elif date_filter == "this_week":
        start_date = today - timedelta(days=today.weekday())
        end_date = today

    elif date_filter == "this_month":
        start_date = today.replace(day=1)
        end_date = today

    elif date_filter == "this_year":
        start_date = today.replace(month=1, day=1)
        end_date = today

    elif date_filter == "custom":
        if start_date_input:
            start_date = datetime.strptime(start_date_input, "%Y-%m-%d").date()

        if end_date_input:
            end_date = datetime.strptime(end_date_input, "%Y-%m-%d").date()

    date_filter_options = [
        {
            "value": "today",
            "label": "Today",
            "selected": date_filter == "today",
        },
        {
            "value": "this_week",
            "label": "This Week",
            "selected": date_filter == "this_week",
        },
        {
            "value": "this_month",
            "label": "This Month",
            "selected": date_filter == "this_month",
        },
        {
            "value": "this_year",
            "label": "This Year",
            "selected": date_filter == "this_year",
        },
        {
            "value": "custom",
            "label": "Custom Range",
            "selected": date_filter == "custom",
        },
    ]

    return {
        "date_filter": date_filter,
        "start_date_input": start_date_input,
        "end_date_input": end_date_input,
        "start_date": start_date,
        "end_date": end_date,
        "date_filter_options": date_filter_options,
    }

def format_ugx(value):
    value = value or 0

    try:
        value = float(value)
    except (TypeError, ValueError):
        value = 0

    return f"UGX {value:,.0f}"