from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cardapio", "0003_alter_pedido_forma_pagamento"),
    ]

    operations = [
        migrations.AlterField(
            model_name="pedido",
            name="status_pagamento",
            field=models.CharField(
                choices=[("pago", "Pago")],
                default="pago",
                help_text="Estado atual do pagamento",
                max_length=20,
            ),
        ),
    ]
