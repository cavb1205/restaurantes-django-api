# Generated by Django 5.2 on 2025-04-17 16:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_alter_categoria_options_alter_producto_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='producto',
            name='restaurante',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='productos', to='api.restaurante'),
        ),
    ]
