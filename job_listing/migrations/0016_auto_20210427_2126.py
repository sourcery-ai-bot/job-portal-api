# Generated by Django 3.1.7 on 2021-04-27 21:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job_listing', '0015_auto_20210427_2115'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='description',
            field=models.TextField(),
        ),
    ]
