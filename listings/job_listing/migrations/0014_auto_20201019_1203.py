# Generated by Django 3.1.1 on 2020-10-19 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job_listing', '0013_auto_20201019_1201'),
    ]

    operations = [
        migrations.AlterField(
            model_name='applyjob',
            name='status',
            field=models.CharField(choices=[('sent', 'Sent'), ('recieved', 'Recieved'), ('rejected', 'Rejected'), ('approved', 'Approved')], default='recieved', max_length=10),
        ),
    ]
