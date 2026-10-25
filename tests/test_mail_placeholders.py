"""TeamShifts email placeholders stay in TeamShifts and use the shared event placeholders from core."""

from zoneinfo import ZoneInfo

import pytest
from django.utils.formats import date_format
from django_scopes import scopes_disabled
from eventyay.base.email import get_available_placeholders, get_email_context, shared_event_placeholders

from teamshifts.forms import EMAIL_PLACEHOLDERS
from teamshifts.mail import MAIL_CONTEXT_KEY

TEAMSHIFTS_ONLY = ("full_name", "role_name", "shift_schedule_url", "shift_name", "voucher_code", "applicant_name")


@pytest.mark.django_db
@pytest.mark.parametrize("parameters", [["event"], ["event", "user", "team"]])
def test_teamshifts_placeholders_stay_out_of_other_editors(event, parameters):
    with scopes_disabled():
        available = get_available_placeholders(event, parameters)

    for identifier in TEAMSHIFTS_ONLY:
        assert identifier not in available


@pytest.mark.django_db
def test_teamshifts_placeholders_are_offered_with_the_teamshifts_key(event):
    parameters = ["event", MAIL_CONTEXT_KEY, "user", "role", "shift", "application", "voucher_code"]
    with scopes_disabled():
        available = get_available_placeholders(event, parameters)

    for identifier in TEAMSHIFTS_ONLY:
        assert identifier in available


@pytest.mark.django_db
def test_teamshifts_emails_render_plugin_and_shared_placeholders(event, user):
    user.fullname = "Jane Volunteer"
    user.save()
    event.settings.contact_mail = "team@example.com"
    with scopes_disabled():
        context = get_email_context(event=event, user=user, **{MAIL_CONTEXT_KEY: True})

    assert context["full_name"] == "Jane Volunteer"
    assert str(context["event_name"]) == "Test Event"
    assert context["organizer_name"] == "Test Organizer"
    assert str(context["event_url"]).endswith("/test-organizer/test-event/")
    assert str(context["event_dates"]) == event.get_date_range_display()
    assert str(context["event_start_date"]) == date_format(event.date_from.astimezone(ZoneInfo(event.settings.timezone)), "DATE_FORMAT")
    assert context["event_contact_email"] == "team@example.com"


def test_editor_lists_every_visible_shared_event_placeholder():
    for placeholder in shared_event_placeholders():
        assert (placeholder.identifier in EMAIL_PLACEHOLDERS) is placeholder.is_visible
