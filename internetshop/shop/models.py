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

    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='orders')
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
        if self.total_price is None and self.product_id:
            self.total_price = self.product.price
        super().save(*args, **kwargs)


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
