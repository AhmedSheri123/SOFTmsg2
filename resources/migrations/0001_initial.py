# Generated by Django 4.2.16 on 2024-10-30 05:47

from django.db import migrations, models
import django.db.models.deletion
import tinymce.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DocsServiceSectionsModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=254, verbose_name='Section Name')),
                ('desc', models.TextField(verbose_name='Section Description')),
                ('is_enabled', models.BooleanField(default=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='DocsServicesModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=254, verbose_name='Service Name')),
                ('desc', models.TextField(verbose_name='Service Description')),
                ('is_enabled', models.BooleanField(default=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='SectionContentsModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=254, verbose_name='Content Name')),
                ('desc', models.TextField(verbose_name='Content Description')),
                ('content', tinymce.models.HTMLField()),
                ('is_enabled', models.BooleanField(default=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='resources.docsservicesectionsmodel')),
            ],
        ),
        migrations.AddField(
            model_name='docsservicesectionsmodel',
            name='service',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='resources.docsservicesmodel'),
        ),
    ]
