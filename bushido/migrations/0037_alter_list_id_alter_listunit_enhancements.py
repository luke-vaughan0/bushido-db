# Generated by Django 4.1.1 on 2023-06-02 18:38

from django.db import migrations, models
import shortuuid.main


class Migration(migrations.Migration):

    dependencies = [
        ('bushido', '0036_alter_list_id_alter_listunit_equipment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='list',
            name='id',
            field=models.CharField(default=shortuuid.main.ShortUUID.uuid, editable=False, max_length=20, primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='listunit',
            name='enhancements',
            field=models.ManyToManyField(blank=True, to='bushido.enhancement'),
        ),
    ]
