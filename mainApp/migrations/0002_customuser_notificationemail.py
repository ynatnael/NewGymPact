# Generated by Django 4.2.23 on 2025-06-19 17:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainApp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='notificationEmail',
            field=models.EmailField(blank=True, help_text='Email for notifications', max_length=254, null=True),
        ),
    ]
