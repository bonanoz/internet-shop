# Generated for the ESTIVO restructure

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Material',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('slug', models.SlugField(max_length=64, unique=True)),
                ('description', models.TextField(blank=True)),
                ('hero_image', models.ImageField(blank=True, null=True, upload_to='materials/')),
                ('order', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name': 'Материал',
                'verbose_name_plural': 'Материалы',
                'ordering': ['order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('slug', models.SlugField(max_length=64, unique=True)),
                ('order', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name': 'Категория',
                'verbose_name_plural': 'Категории',
                'ordering': ['order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('slug', models.SlugField(max_length=128, unique=True)),
                ('description', models.TextField(blank=True)),
                ('cover_image', models.ImageField(blank=True, null=True, upload_to='collections/')),
                ('is_featured', models.BooleanField(default=False)),
                ('order', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name': 'Коллекция',
                'verbose_name_plural': 'Коллекции',
                'ordering': ['order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('slug', models.SlugField(blank=True, max_length=160, unique=True)),
                ('sku', models.CharField(blank=True, max_length=64, verbose_name='Артикул')),
                ('short_description', models.CharField(blank=True, max_length=300)),
                ('description', models.TextField()),
                ('price', models.IntegerField(help_text='Цена в рублях (или цена "от" для комплектов)')),
                ('old_price', models.IntegerField(blank=True, help_text='Прежняя цена — для акций', null=True)),
                ('max_load_kg', models.IntegerField(default=120, verbose_name='Нагрузка на посадочное место, кг')),
                ('warranty_years', models.IntegerField(default=3, verbose_name='Гарантия, лет')),
                ('temp_min_c', models.IntegerField(default=-70, verbose_name='Мин. температура эксплуатации, °C')),
                ('temp_max_c', models.IntegerField(default=70, verbose_name='Макс. температура эксплуатации, °C')),
                ('is_available', models.BooleanField(default=True, verbose_name='В наличии/под заказ')),
                ('is_featured', models.BooleanField(default=False, verbose_name='Показывать на главной')),
                ('main_image', models.ImageField(blank=True, null=True, upload_to='products/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='products', to='shop.category')),
                ('collection', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products', to='shop.collection')),
                ('material', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='products', to='shop.material')),
            ],
            options={
                'verbose_name': 'Товар',
                'verbose_name_plural': 'Товары',
                'ordering': ['-is_featured', 'name'],
            },
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='products/gallery/')),
                ('order', models.IntegerField(default=0)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gallery', to='shop.product')),
            ],
            options={
                'verbose_name': 'Фото товара',
                'verbose_name_plural': 'Фото товара',
                'ordering': ['order', 'id'],
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_name', models.CharField(max_length=256, verbose_name='ФИО')),
                ('customer_phone', models.CharField(max_length=32, verbose_name='Телефон')),
                ('customer_email', models.CharField(blank=True, max_length=256, verbose_name='Email')),
                ('delivery_address', models.TextField(blank=True, verbose_name='Адрес доставки')),
                ('comment', models.TextField(blank=True, verbose_name='Комментарий')),
                ('status', models.CharField(choices=[('new', 'Новая заявка'), ('contacted', 'Связались с клиентом'), ('in_production', 'В производстве'), ('shipped', 'Отправлен'), ('completed', 'Завершён'), ('cancelled', 'Отменён')], default='new', max_length=20)),
                ('payment_status', models.CharField(choices=[('not_required', 'Не требуется'), ('awaiting', 'Ожидает оплаты'), ('paid', 'Оплачен')], default='not_required', max_length=20)),
                ('total_price', models.IntegerField(blank=True, help_text='Цена товара на момент заявки', null=True)),
                ('telegram_notified', models.BooleanField(default=False)),
                ('admin_notes', models.TextField(blank=True, verbose_name='Заметки менеджера')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='orders', to='shop.product')),
            ],
            options={
                'verbose_name': 'Заявка на товар',
                'verbose_name_plural': 'Заявки на товар',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Lead',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, verbose_name='Имя')),
                ('phone', models.CharField(max_length=32, verbose_name='Телефон')),
                ('email', models.CharField(blank=True, max_length=256, verbose_name='Email')),
                ('lead_type', models.CharField(choices=[('private', 'Частный клиент'), ('designer', 'Дизайн-проект'), ('b2b', 'B2B (отель/ресторан/кафе)')], default='private', max_length=20)),
                ('message', models.TextField(blank=True, verbose_name='Сообщение')),
                ('source_page', models.CharField(blank=True, max_length=128, verbose_name='Источник')),
                ('status', models.CharField(choices=[('new', 'Новая'), ('processing', 'В обработке'), ('done', 'Обработана'), ('rejected', 'Отклонена')], default='new', max_length=20)),
                ('telegram_notified', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Заявка/лид',
                'verbose_name_plural': 'Заявки/лиды',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author', models.CharField(max_length=256)),
                ('rating', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('usage_duration', models.CharField(blank=True, max_length=64, verbose_name='Срок использования')),
                ('text', models.TextField()),
                ('is_published', models.BooleanField(default=False, verbose_name='Опубликован')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='shop.product')),
            ],
            options={
                'verbose_name': 'Отзыв',
                'verbose_name_plural': 'Отзывы',
                'ordering': ['-created_at'],
            },
        ),
    ]
