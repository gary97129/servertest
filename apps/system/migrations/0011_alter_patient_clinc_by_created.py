# Generated by Django 3.2 on 2023-04-24 12:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0010_auto_20230424_1957'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patient',
            name='clinc_by_created',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='clinc_by_created', to=settings.AUTH_USER_MODEL, verbose_name='上級創建者'),
        ),
    ]