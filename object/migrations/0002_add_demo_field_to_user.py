from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('object', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            "ALTER TABLE auth_user ADD COLUMN demo BOOLEAN DEFAULT TRUE;",
            reverse_sql="ALTER TABLE auth_user DROP COLUMN demo;"
        ),
    ]