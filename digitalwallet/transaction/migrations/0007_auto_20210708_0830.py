# Generated by Django 3.2.4 on 2021-07-08 08:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('transaction', '0006_transaction'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='is_topup',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='source_id',
        ),
        migrations.RemoveField(
            model_name='transactiondetails',
            name='device',
        ),
        migrations.AddField(
            model_name='transaction',
            name='updated_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='user_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterModelTable(
            name='transaction',
            table='transactions',
        ),
        migrations.CreateModel(
            name='Card',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('card_number', models.IntegerField(unique=True)),
                ('balance', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('user_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'cards',
                'managed': True,
            },
        ),
        migrations.AddField(
            model_name='transaction',
            name='from_card_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='from_card_id', to='transaction.card'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='to_card_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='to_card_id', to='transaction.card'),
        ),
    ]