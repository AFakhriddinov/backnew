# Generated by Django 4.1 on 2022-09-02 06:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_alter_article_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=255, null=True, verbose_name='Elektron pochta manzili*'),
        ),
    ]
