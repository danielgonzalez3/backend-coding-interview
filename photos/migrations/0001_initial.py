# Generated manually for initial migration

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pexels_id', models.IntegerField(db_index=True, help_text='Pexels photo ID', unique=True)),
                ('width', models.IntegerField(help_text='Photo width in pixels')),
                ('height', models.IntegerField(help_text='Photo height in pixels')),
                ('url', models.URLField(help_text='Pexels photo page URL', max_length=500)),
                ('photographer', models.CharField(db_index=True, max_length=255)),
                ('photographer_url', models.URLField(max_length=500)),
                ('photographer_id', models.IntegerField(db_index=True)),
                ('avg_color', models.CharField(help_text='Average color hex code', max_length=7)),
                ('alt', models.TextField(blank=True, help_text='Photo alt text/description')),
                ('src_original', models.URLField(max_length=500)),
                ('src_large2x', models.URLField(max_length=500)),
                ('src_large', models.URLField(max_length=500)),
                ('src_medium', models.URLField(max_length=500)),
                ('src_small', models.URLField(max_length=500)),
                ('src_portrait', models.URLField(max_length=500)),
                ('src_landscape', models.URLField(max_length=500)),
                ('src_tiny', models.URLField(max_length=500)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='PhotoFavorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('photo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorited_by', to='photos.photo')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='photo',
            index=models.Index(fields=['pexels_id'], name='photos_phot_pexels__idx'),
        ),
        migrations.AddIndex(
            model_name='photo',
            index=models.Index(fields=['photographer'], name='photos_phot_photogr_idx'),
        ),
        migrations.AddIndex(
            model_name='photo',
            index=models.Index(fields=['photographer_id'], name='photos_phot_photogr_0_idx'),
        ),
        migrations.AddIndex(
            model_name='photo',
            index=models.Index(fields=['created_at'], name='photos_phot_created_idx'),
        ),
        migrations.AddIndex(
            model_name='photofavorite',
            index=models.Index(fields=['user', 'created_at'], name='photos_phot_user_id_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='photofavorite',
            unique_together={('user', 'photo')},
        ),
    ]
