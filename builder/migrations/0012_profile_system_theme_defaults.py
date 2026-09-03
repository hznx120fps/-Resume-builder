from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('builder', '0011_activitylog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='theme',
            field=models.CharField(
                choices=[('light', 'Світла'), ('dark', 'Темна'), ('system', 'Системна')],
                default='system',
                max_length=10,
            ),
        ),
        migrations.AlterField(
            model_name='profile',
            name='gradient_enabled',
            field=models.BooleanField(default=False),
        ),
    ]