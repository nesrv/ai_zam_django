from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('object', '0006_dokhodresursa'),
    ]

    operations = [
        migrations.RenameField(
            model_name='dokhodresursa',
            old_name='dokhod',
            new_name='vypolneno',
        ),
    ]