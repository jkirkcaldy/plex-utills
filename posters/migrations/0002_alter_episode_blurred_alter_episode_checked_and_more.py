# Generated by Django 4.1.7 on 2023-03-18 15:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posters', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='episode',
            name='blurred',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='episode',
            name='checked',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='film',
            name='checked',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='plex',
            name='audio_posters',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='plex',
            name='autocollections',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='plex',
            name='backup',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='plex',
            name='default_poster',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='plex',
            name='disney',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='plex',
            name='films4kposters',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='plex',
            name='hdr',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='plex',
            name='hide4k',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='plex',
            name='loglevel',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='plex',
            name='manualplexpath',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='plex',
            name='mcu_collection',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='plex',
            name='mini3d',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='plex',
            name='mini4k',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='plex',
            name='new_hdr',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='plex',
            name='pixar',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='plex',
            name='posters3d',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='plex',
            name='posters4k',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='plex',
            name='recreate_hdr',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='plex',
            name='skip_media_info',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='plex',
            name='spoilers',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='plex',
            name='tmdb_restore',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='plex',
            name='tr_r_p_collection',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='plex',
            name='transcode',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='plex',
            name='tv4kposters',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='season',
            name='checked',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]
