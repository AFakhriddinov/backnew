# Generated by Django 4.1.1 on 2022-09-14 13:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0018_alter_article_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="article",
            name="price",
            field=models.DecimalField(decimal_places=0, max_digits=20),
        ),
    ]
