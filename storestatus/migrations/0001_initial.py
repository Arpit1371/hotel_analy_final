# Generated by Django 4.1.7 on 2023-03-31 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='StoreStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('store_id', models.BigIntegerField()),
                ('status', models.CharField(max_length=10)),
                ('timestamp_utc', models.DateTimeField()),
            ],
        ),
    ]
