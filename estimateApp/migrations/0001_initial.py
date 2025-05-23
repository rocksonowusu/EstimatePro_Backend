# Generated by Django 5.1.7 on 2025-04-07 11:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('online_name', models.CharField(blank=True, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='BusinessProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('business_name', models.CharField(max_length=255)),
                ('phone', models.CharField(max_length=50)),
                ('address', models.CharField(max_length=255)),
                ('website', models.CharField(blank=True, max_length=255)),
                ('tax_id', models.CharField(blank=True, max_length=100)),
                ('established', models.CharField(blank=True, max_length=20)),
                ('industry', models.CharField(blank=True, max_length=100)),
                ('description', models.TextField(blank=True)),
                ('background_image', models.ImageField(blank=True, null=True, upload_to='business_images/')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='business_profile', to='estimateApp.userprofile')),
            ],
        ),
    ]
