# Generated by Django 4.0.1 on 2022-01-08 17:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0005_order_rz_invoice_id_order_rz_payment_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='category_hi',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='category_mr',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='inventory',
            name='brand_hi',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='inventory',
            name='brand_mr',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='inventory',
            name='color_hi',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='inventory',
            name='color_mr',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='inventory',
            name='description_hi',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='inventory',
            name='description_mr',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='inventory',
            name='name_hi',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='inventory',
            name='name_mr',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
