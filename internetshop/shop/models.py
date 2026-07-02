from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse

from .utils import ru_slugify


class Material(models.Model):
    """Материал плетения: роуп, ротанг, шпон, HPL."""

    name = models.CharField(max_length=64)
    slug = models.SlugField(max_length=64, unique=True)
    description = models.TextField(blank=True)
    hero_image = models.ImageField(upload_to='materials/', blank=True, null=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Материал'
        verbose_name_plural = 'Материалы'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = ru_slugify(self.name)
        super().save(*args, **kwargs)


class Category(models.Model):
    """Категория товара: кресла, диваны, столы и т.д.

    Не привязана к материалу — одна и та же категория (например, "Столы")
    встречается и у роупа, и у ротанга, и у шпона/HPL.
    """

    name = models.CharField(max_length=64)
    slug = models.SlugField(max_length=64, unique=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = ru_slugify(self.name)
        super().save(*args, **kwargs)


class Collection(models.Model):
    """Коллекция/серия для витрины и подборок на главной."""

    name = models.CharField(max_length=128)
    slug = models.SlugField(max_length=128, unique=True)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to='collections/', blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Коллекция'
        verbose_name_plural = 'Коллекции'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = ru_slugify(self.name)
        super().save(*args, **kwargs)


class ColorOption(models.Model):
    """Цвет отделки для конфигуратора товара.

    Единый справочник на весь сайт, сгруппированный по типу отделки
    (плетение / подушки / каркас). Товар подключает нужные цвета через
    M2M ``Product.available_colors``. На цену не влияет — это только
    визуальный выбор (swatch на странице товара и базовый цвет 3D-модели).
    """

    WEAVE = 'weave'
    CUSHION = 'cushion'
    FRAME = 'frame'
    FINISH_TYPE_CHOICES = [
        (WEAVE, 'Плетение'),
        (CUSHION, 'Подушки'),
        (FRAME, 'Каркас'),
    ]

    name = models.CharField('Название цвета', max_length=64)
    finish_type = models.CharField('Тип отделки', max_length=16, choices=FINISH_TYPE_CHOICES)
    hex = models.CharField(
        'HEX-цвет', max_length=7, default='#cccccc',
        help_text='Например #3b3a36 — для образца и базового цвета 3D-модели',
    )
    swatch_image = models.ImageField(
        'Образец текстуры', upload_to='colors/', blank=True, null=True,
        help_text='Необязательно — если задан, показывается вместо однотонного образца',
    )
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['finish_type', 'order', 'name']
        verbose_name = 'Цвет отделки'
        verbose_name_plural = 'Цвета отделки'

    def __str__(self):
        return f'{self.get_finish_type_display()} — {self.name}'


class Product(models.Model):
    name = models.CharField(max_length=128)
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    sku = models.CharField('Артикул', max_length=64, blank=True)

    short_description = models.CharField(max_length=300, blank=True)
    description = models.TextField()

    material = models.ForeignKey(
        Material, on_delete=models.PROTECT, null=True, blank=True, related_name='products',
    )
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, null=True, blank=True, related_name='products',
    )
    collection = models.ForeignKey(
        Collection, on_delete=models.SET_NULL, null=True, blank=True, related_name='products',
    )

    price = models.IntegerField(help_text='Цена в рублях (или цена "от" для комплектов)')
    old_price = models.IntegerField(null=True, blank=True, help_text='Прежняя цена — для акций')

    max_load_kg = models.IntegerField('Нагрузка на посадочное место, кг', default=120)
    warranty_years = models.IntegerField('Гарантия, лет', default=3)
    temp_min_c = models.IntegerField('Мин. температура эксплуатации, °C', default=-70)
    temp_max_c = models.IntegerField('Макс. температура эксплуатации, °C', default=70)

    # Габариты (см) и вес (кг) — показываются в характеристиках, если заданы.
    length_cm = models.IntegerField('Длина, см', null=True, blank=True)
    width_cm = models.IntegerField('Ширина, см', null=True, blank=True)
    height_cm = models.IntegerField('Высота, см', null=True, blank=True)
    weight_kg = models.IntegerField('Вес, кг', null=True, blank=True)

    # Конфигуратор цвета: какие цвета отделки доступны для этого товара.
    available_colors = models.ManyToManyField(
        ColorOption, blank=True, related_name='products', verbose_name='Доступные цвета',
    )

    # 3D-модель (.glb) со сменой цвета материалов. Пока файла нет —
    # страница товара показывает обычную 2D-галерею (fallback).
    model_3d = models.FileField(
        '3D-модель (.glb)', upload_to='models/', blank=True, null=True,
        help_text='Материалы в модели должны называться weave / cushion / frame',
    )
    model_3d_poster = models.ImageField(
        'Постер 3D-модели', upload_to='models/posters/', blank=True, null=True,
    )

    is_available = models.BooleanField('В наличии/под заказ', default=True)
    is_featured = models.BooleanField('Показывать на главной', default=False)

    main_image = models.ImageField(upload_to='products/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', 'name']
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = ru_slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('product_detail', args=[self.slug])

    def colors_by_type(self):
        """Доступные цвета, сгруппированные по типу отделки, в порядке
        Плетение → Подушки → Каркас. Пустые группы не попадают в результат —
        товар из ротанга без отдельного каркаса не покажет группу «Каркас».
        Возвращает список кортежей ``(label, finish_type, [ColorOption, ...])``.
        """
        groups = []
        colors = list(self.available_colors.all())
        for finish_type, label in ColorOption.FINISH_TYPE_CHOICES:
            options = [c for c in colors if c.finish_type == finish_type]
            if options:
                groups.append((label, finish_type, options))
        return groups


class ProductImage(models.Model):
    """Дополнительные фото товара (галерея на странице товара)."""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='gallery')
    image = models.ImageField(upload_to='products/gallery/')
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Фото товара'
        verbose_name_plural = 'Фото товара'

    def __str__(self):
        return f'{self.product.name} — фото {self.order}'


class Order(models.Model):
    """Заявка на товар. Бизнес работает по схеме заявка → консультация →
    изготовление → доставка → оплата, поэтому это не "заказ с оплатой картой",
    а точка контакта с клиентом, которую менеджер обрабатывает вручную.
    """

    STATUS_CHOICES = [
        ('new', 'Новая заявка'),
        ('contacted', 'Связались с клиентом'),
        ('in_production', 'В производстве'),
        ('shipped', 'Отправлен'),
        ('completed', 'Завершён'),
        ('cancelled', 'Отменён'),
    ]

    # TODO: интеграция с платёжным провайдером (ЮKassa/Т-Касса и т.п.) —
    # добавляется отдельным шагом между сохранением Order и редиректом на
    # order_success, когда у владельца будет аккаунт у провайдера.
    PAYMENT_STATUS_CHOICES = [
        ('not_required', 'Не требуется'),
        ('awaiting', 'Ожидает оплаты'),
        ('paid', 'Оплачен'),
    ]

    # Заявка теперь многотоварная — позиции лежат в OrderItem (related_name='items').
    # Поле product оставлено nullable ради старых одно-товарных заявок; новые
    # заявки из корзины его не заполняют.
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name='orders', null=True, blank=True,
    )
    customer_name = models.CharField('ФИО', max_length=256)
    customer_phone = models.CharField('Телефон', max_length=32)
    customer_email = models.CharField('Email', max_length=256, blank=True)
    delivery_address = models.TextField('Адрес доставки', blank=True)
    comment = models.TextField('Комментарий', blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='not_required')
    total_price = models.IntegerField(null=True, blank=True, help_text='Цена товара на момент заявки')

    telegram_notified = models.BooleanField(default=False)
    admin_notes = models.TextField('Заметки менеджера', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Заявка на товар'
        verbose_name_plural = 'Заявки на товар'

    def __str__(self):
        return f'Заявка №{self.pk} — {self.customer_name}'

    def save(self, *args, **kwargs):
        # Fallback для старой одно-товарной заявки: если позиций нет, но задан
        # product — снимаем цену с него. Многотоварные заявки проставляют
        # total_price во view checkout как сумму позиций.
        if self.total_price is None and self.product_id:
            self.total_price = self.product.price
        super().save(*args, **kwargs)

    def recalc_total(self):
        """Пересчитать сумму заявки по позициям и сохранить."""
        self.total_price = sum(item.line_total for item in self.items.all())
        self.save(update_fields=['total_price'])


class OrderItem(models.Model):
    """Позиция заявки: товар + количество + выбранные цвета отделки.

    ``unit_price`` и ``selected_colors`` — снимки на момент оформления, чтобы
    историческая заявка не «поплыла» при изменении цены товара или удалении
    цвета из справочника.
    """

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='order_items')
    quantity = models.PositiveIntegerField('Количество', default=1)
    unit_price = models.IntegerField('Цена за штуку', help_text='Снимок цены на момент заявки')
    selected_colors = models.JSONField(
        'Выбранные цвета', default=dict, blank=True,
        help_text='Снимок вида {"Плетение": "Графит", "Подушки": "Беж"}',
    )

    class Meta:
        verbose_name = 'Позиция заявки'
        verbose_name_plural = 'Позиции заявки'

    def __str__(self):
        return f'{self.product.name} × {self.quantity}'

    @property
    def line_total(self):
        return self.unit_price * self.quantity


class Lead(models.Model):
    """Единая модель для всех лид-форм сайта (общая консультация,
    дизайн-проект, B2B-заявка) — различаются полем lead_type."""

    LEAD_TYPE_CHOICES = [
        ('private', 'Частный клиент'),
        ('designer', 'Дизайн-проект'),
        ('b2b', 'B2B (отель/ресторан/кафе)'),
    ]
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('processing', 'В обработке'),
        ('done', 'Обработана'),
        ('rejected', 'Отклонена'),
    ]

    name = models.CharField('Имя', max_length=256)
    phone = models.CharField('Телефон', max_length=32)
    email = models.CharField('Email', max_length=256, blank=True)
    lead_type = models.CharField(max_length=20, choices=LEAD_TYPE_CHOICES, default='private')
    message = models.TextField('Сообщение', blank=True)
    source_page = models.CharField('Источник', max_length=128, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    telegram_notified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Заявка/лид'
        verbose_name_plural = 'Заявки/лиды'

    def __str__(self):
        return f'{self.get_lead_type_display()} — {self.name}'


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    author = models.CharField(max_length=256)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    usage_duration = models.CharField('Срок использования', max_length=64, blank=True)
    text = models.TextField()
    is_published = models.BooleanField('Опубликован', default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return f'{self.author} — {self.product.name} ({self.rating}/5)'
