# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-10 17:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('norma', '0012_auto_20160309_1407'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vinculonormajuridica',
            name='tipo_vinculo',
            field=models.CharField(blank=True, choices=[('A', 'Altera a norma'), ('R', 'Revoga integralmente a norma'), ('P', 'Revoga parcialmente a norma'), ('T', 'Revoga integralmente por consolidação'), ('C', 'Norma correlata'), ('S', 'Ressalva a norma'), ('E', 'Reedita a norma'), ('I', 'Reedita a norma com alteração'), ('G', 'Regulamenta a norma'), ('K', 'Suspende parcialmente a norma'), ('L', 'Suspende integralmente a norma'), ('N', 'Julgada integralmente inconstitucional'), ('O', 'Julgada parcialmente inconstitucional')], max_length=1),
        ),
    ]