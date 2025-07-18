from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('telegrambot', '0004_chatmessage_forward_from_chatmessage_message_id_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProcessedUpdate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('update_id', models.CharField(max_length=50, unique=True, verbose_name='ID обновления')),
                ('processed_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата обработки')),
            ],
            options={
                'verbose_name': 'Обработанное обновление',
                'verbose_name_plural': 'Обработанные обновления',
                'ordering': ['-processed_at'],
            },
        ),
        migrations.AddIndex(
            model_name='processedupdate',
            index=models.Index(fields=['update_id'], name='telegrambot_update_i_e0d1a8_idx'),
        ),
        migrations.AddIndex(
            model_name='processedupdate',
            index=models.Index(fields=['processed_at'], name='telegrambot_process_9c0e9c_idx'),
        ),
    ]