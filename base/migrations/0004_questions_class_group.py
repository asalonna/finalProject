# Generated by Django 4.1 on 2022-09-04 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_remove_usermarks_question_usermarks_question'),
    ]

    operations = [
        migrations.AddField(
            model_name='questions',
            name='class_group',
            field=models.CharField(default='test', max_length=50),
            preserve_default=False,
        ),
    ]
