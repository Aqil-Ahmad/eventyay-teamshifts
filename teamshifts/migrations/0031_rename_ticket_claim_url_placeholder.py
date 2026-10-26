from django.db import migrations
from eventyay.helpers.placeholders import rename_placeholder
from i18nfield.strings import LazyI18nString

FIELDS = {
    "TeamShiftsEmailTemplate": ("subject", "body"),
    "TeamShiftsCustomEmailTemplate": ("subject", "body"),
    "TeamShiftsEmailQueue": ("subject", "message"),
}


def renamed(value, old, new):
    data = value.data if isinstance(value, LazyI18nString) else value
    if isinstance(data, dict):
        return LazyI18nString({lang: rename_placeholder(text, old, new) for lang, text in data.items()})
    if isinstance(data, str):
        return LazyI18nString(rename_placeholder(data, old, new))
    return value


def rename(apps, old, new):
    for model_name, fields in FIELDS.items():
        model = apps.get_model("teamshifts", model_name)
        for row in model.objects.all().iterator():
            changed = []
            for field in fields:
                value = getattr(row, field)
                data = value.data if isinstance(value, LazyI18nString) else value
                if data and old in str(data):
                    setattr(row, field, renamed(value, old, new))
                    changed.append(field)
            if changed:
                row.save(update_fields=changed)


def forwards(apps, schema_editor):
    rename(apps, "ticket_claim_url", "voucher_redeem_url")


def backwards(apps, schema_editor):
    rename(apps, "voucher_redeem_url", "ticket_claim_url")


class Migration(migrations.Migration):
    dependencies = [
        ("teamshifts", "0030_teamapplicationquestionoption"),
    ]

    operations = [
        migrations.RunPython(forwards, reverse_code=backwards),
    ]
