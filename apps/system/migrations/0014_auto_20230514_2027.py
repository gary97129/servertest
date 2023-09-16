# Generated by Django 3.2 on 2023-05-14 12:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0013_remove_manufacturers_long'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='manufacturers',
            name='parent',
        ),
        migrations.AddField(
            model_name='manufacturers',
            name='long',
            field=models.CharField(max_length=50, null=True, verbose_name='長度'),
        ),
        migrations.AddField(
            model_name='manufacturers',
            name='parentId',
            field=models.IntegerField(blank=True, null=True, verbose_name='樹狀'),
        ),
    ]
