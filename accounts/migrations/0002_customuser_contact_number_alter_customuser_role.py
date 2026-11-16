from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='contact_number',
            field=models.CharField(blank=True, default='', max_length=25, verbose_name='Contact Number'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='role',
            field=models.CharField(
                choices=[
                    ('ADMIN', 'Administrator'),
                    ('OPERATOR', 'Operator'),
                    ('MEMBER', 'Member'),
                    ('STUDENT', 'Student / Member'),
                ],
                default='MEMBER',
                max_length=15,
            ),
        ),
    ]
