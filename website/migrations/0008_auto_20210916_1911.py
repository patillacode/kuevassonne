# Generated by Django 3.2.5 on 2021-09-16 17:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0007_auto_20210914_1842'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='record',
            options={'ordering': ['-id']},
        ),
        migrations.RemoveField(
            model_name='game',
            name='image',
        ),
        migrations.AlterField(
            model_name='game',
            name='avg_seconds_per_turn',
            field=models.IntegerField(blank=True, help_text='Number of seconds of the average turn', null=True),
        ),
        migrations.AlterField(
            model_name='game',
            name='total_time',
            field=models.IntegerField(blank=True, help_text='Number of seconds the game lasted for', null=True),
        ),
    ]
