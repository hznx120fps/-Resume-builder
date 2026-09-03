from django.db import migrations, models


def set_light_theme(apps, schema_editor):
    Profile = apps.get_model('builder', 'Profile')
    Profile.objects.all().update(theme='light')


class Migration(migrations.Migration):

    dependencies = [
        ('builder', '0012_profile_system_theme_defaults'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='theme',
            field=models.CharField(
                choices=[('light', 'Світла'), ('dark', 'Темна'), ('system', 'Системна')],
                default='light',
                max_length=10,
            ),
        ),
        migrations.RunPython(set_light_theme, migrations.RunPython.noop),
    ]