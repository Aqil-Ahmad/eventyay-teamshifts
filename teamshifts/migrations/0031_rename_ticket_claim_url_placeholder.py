from django.db import migrations
from eventyay.helpers.placeholders import rename_placeholder
from i18nfield.strings import LazyI18nString

FIELDS = {
    "TeamShiftsEmailTemplate": ("subject", "body"),
    "TeamShiftsCustomEmailTemplate": ("subject", "body"),
    "TeamShiftsEmailQueue": ("subject", "message"),
}


def renamed(value):
    data = value.data if isinstance(value, LazyI18nString) else value
    if isinstance(data, dict):
        return LazyI18nString({lang: rename_placeholder(text, "ticket_claim_url", "voucher_redeem_url") for lang, text in data.items()})
    if isinstance(data, str):
        return LazyI18nString(rename_placeholder(data, "ticket_claim_url", "voucher_redeem_url"))
    return value


def rename_ticket_claim_url(apps, schema_editor):
    for model_name, fields in FIELDS.items():
        model = apps.get_model("teamshifts", model_name)
        for row in model.objects.all().iterator():
            changed = []
            for field in fields:
                value = getattr(row, field)
                data = value.data if isinstance(value, LazyI18nString) else value
                if data and "ticket_claim_url" in str(data):
                    setattr(row, field, renamed(value))
                    changed.append(field)
            if changed:
                row.save(update_fields=changed)


class Migration(migrations.Migration):
    dependencies = [
        ("teamshifts", "0030_teamapplicationquestionoption"),
    ]

    operations = [
        migrations.RunPython(rename_ticket_claim_url, reverse_code=migrations.RunPython.noop),
    ]
