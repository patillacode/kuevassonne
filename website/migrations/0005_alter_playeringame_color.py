# Generated by Django 3.2.5 on 2021-09-05 23:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0004_alter_game_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playeringame',
            name='color',
            field=models.CharField(choices=[('RED', 'Red'), ('BLUE', 'Blue'), ('YELLOW', 'Yellow'), ('PINK', 'Pink'), ('GREEN', 'Green'), ('BLACK', 'Black'), ('ORANGE', 'Orange'), ('WHITE', 'White'), ('BROWN', 'Brown')], max_length=7),
        ),
    ]
