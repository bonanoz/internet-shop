from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import LeadForm, OrderForm
from .models import Category, Collection, Material, Product, Review
from .utils import notify_telegram

PRODUCTION_STEPS = [
    ('Заявка и консультация', 'Обсуждаем задачу, бюджет и сроки — по телефону или на встрече.'),
    ('Поиск или конструирование', 'Подбираем готовое изделие в наличии или проектируем индивидуальный вариант.'),
    ('Плетение мебели', 'Мастера вручную плетут корпус из выбранного материала.'),
    ('Сварка и порошковая окраска', 'Каркас сваривается и окрашивается порошковым методом для равномерного покрытия.'),
    ('Контроль качества', 'Каждое изделие проверяется перед отправкой клиенту.'),
    ('Согласование с клиентом', 'Присылаем фото и видео готового изделия на согласование.'),
    ('Упаковка и брендирование', 'Аккуратно упаковываем изделие для транспортировки.'),
    ('Логистика и доставка', 'Рассчитываем маршрут и доставляем по всей России от 3 дней.'),
]

FAQ_ITEMS = [
    ('Как сделать заказ?', 'Оставьте заявку на сайте или позвоните нам — менеджер уточнит детали и поможет выбрать модель.'),
    ('Какой вес выдерживает плетёная мебель?', 'Конструкция выдерживает нагрузку до 120 кг на одно посадочное место.'),
    ('Для какого климата подходит мебель?', 'Материалы устойчивы к перепадам температур от -70 до +70°C, не боятся влаги и солнца.'),
    ('Из чего изготавливаются каркасы?', 'Каркасы производятся по выбору клиента из тонкостенной стали или алюминия.'),
    ('Как происходит покраска каркасов?', 'Каркасы красятся порошковым методом — это обеспечивает плотное и равномерное покрытие.'),
    ('Из чего изготавливаются мягкие элементы?', 'Используются влагостойкие материалы, безопасные для взрослых и детей, гипоаллергенные.'),
]

HOME_SEGMENTS = [
    {
        'title': 'Для дома',
        'description': 'Мебель для квартиры, частного дома, дачи и летней террасы.',
        'cta_text': 'Смотреть каталог',
        'cta_url_name': 'catalog_list',
    },
    {
        'title': 'Для ресторанов и отелей',
        'description': 'Комплексное оснащение террас, зон отдыха и общественных пространств.',
        'cta_text': 'Условия для бизнеса',
        'cta_url_name': 'b2b_page',
    },
    {
        'title': 'Индивидуальный проект',
        'description': 'Разработаем мебель по вашему эскизу вместе с дизайнером.',
        'cta_text': 'Обсудить проект',
        'cta_url_name': 'designers_page',
    },
]


def home(request):
    collections = Collection.objects.filter(is_featured=True)[:6]
    featured_products = Product.objects.filter(is_featured=True, is_available=True).select_related('material')[:8]
    reviews = Review.objects.filter(is_published=True).select_related('product')[:6]
    return render(request, 'home.html', {
        'segments': HOME_SEGMENTS,
        'collections': collections,
        'featured_products': featured_products,
        'production_steps': PRODUCTION_STEPS,
        'faq_items': FAQ_ITEMS,
        'reviews': reviews,
    })


def _paginate_products(request, products):
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def catalog_list(request):
    products = Product.objects.filter(is_available=True).select_related('material', 'category')
    search = request.GET.get('search')
    if search:
        products = products.filter(Q(name__icontains=search) | Q(description__icontains=search))
    return render(request, 'catalog_list.html', {
        'page_obj': _paginate_products(request, products),
        'materials': Material.objects.all(),
        'categories': Category.objects.all(),
        'search': search or '',
        'current_material': None,
    })


def catalog_by_material(request, material_slug):
    material = get_object_or_404(Material, slug=material_slug)
    products = Product.objects.filter(is_available=True, material=material).select_related('category')
    return render(request, 'catalog_list.html', {
        'page_obj': _paginate_products(request, products),
        'materials': Material.objects.all(),
        'categories': Category.objects.filter(products__material=material).distinct(),
        'search': '',
        'current_material': material,
        'meta_title': f'{material.name} — каталог | ESTIVO',
    })


def catalog_by_category(request, material_slug, category_slug):
    material = get_object_or_404(Material, slug=material_slug)
    category = get_object_or_404(Category, slug=category_slug)
    products = Product.objects.filter(is_available=True, material=material, category=category)
    return render(request, 'catalog_list.html', {
        'page_obj': _paginate_products(request, products),
        'materials': Material.objects.all(),
        'categories': Category.objects.filter(products__material=material).distinct(),
        'search': '',
        'current_material': material,
        'current_category': category,
        'breadcrumbs': [
            ('Каталог', reverse('catalog_list')),
            (material.name, reverse('catalog_by_material', args=[material.slug])),
            (category.name, None),
        ],
        'meta_title': f'{category.name} из {material.name.lower()} | ESTIVO',
        'meta_description': f'{category.name} из {material.name.lower()} ручной работы — ESTIVO. Гарантия 3 года, доставка по России от 3 дней.',
    })


def product_detail(request, slug):
    product = get_object_or_404(Product.objects.select_related('material', 'category'), slug=slug)
    related_products = (
        Product.objects.filter(is_available=True, category=product.category)
        .exclude(pk=product.pk)[:4]
    )
    reviews = product.reviews.filter(is_published=True)
    crumbs = [('Каталог', reverse('catalog_list'))]
    if product.material:
        crumbs.append((product.material.name, reverse('catalog_by_material', args=[product.material.slug])))
    crumbs.append((product.name, None))
    return render(request, 'product_detail.html', {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'breadcrumbs': crumbs,
    })


def _lead_page(request, template_name, lead_type, extra_context=None):
    if request.method == 'POST':
        form = LeadForm(request.POST)
        if form.is_valid():
            lead = form.save(commit=False)
            lead.source_page = template_name
            lead.save()
            sent = notify_telegram(
                f'📩 Новая заявка ({lead.get_lead_type_display()})\n'
                f'Имя: {lead.name}\nТелефон: {lead.phone}\nEmail: {lead.email}\n'
                f'Сообщение: {lead.message}'
            )
            if sent:
                lead.telegram_notified = True
                lead.save(update_fields=['telegram_notified'])
            messages.success(request, 'Заявка отправлена! Мы свяжемся с вами в ближайшее время.')
            return redirect(request.path)
    else:
        form = LeadForm(initial={'lead_type': lead_type})

    context = {'form': form}
    if extra_context:
        context.update(extra_context)
    return render(request, template_name, context)


def b2b_page(request):
    return _lead_page(request, 'b2b.html', 'b2b')


def designers_page(request):
    return _lead_page(request, 'designers.html', 'designer')


def about_page(request):
    return render(request, 'about.html', {
        'materials': Material.objects.all(),
        'production_steps': PRODUCTION_STEPS,
    })


def delivery_payment_page(request):
    return render(request, 'delivery_payment.html')


def warranty_page(request):
    return render(request, 'warranty.html')


def faq_page(request):
    return render(request, 'faq.html', {'faq_items': FAQ_ITEMS})


def contacts_page(request):
    return _lead_page(request, 'contacts.html', 'private')


def order_create(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.product = product
            order.save()
            sent = notify_telegram(
                f'📦 Новая заявка на товар: {product.name}\n'
                f'💸 Цена: {order.total_price} рублей\n'
                f'ФИО: {order.customer_name}\nТелефон: {order.customer_phone}\n'
                f'Адрес доставки: {order.delivery_address}\nКомментарий: {order.comment}'
            )
            if sent:
                order.telegram_notified = True
                order.save(update_fields=['telegram_notified'])
            return redirect('order_success')
    else:
        form = OrderForm()

    return render(request, 'order_form.html', {'product': product, 'form': form})


def order_success(request):
    return render(request, 'order_success.html')


def lead_create(request):
    """Общая точка приёма лид-форм со страниц, которые сами не рендерят форму
    напрямую (например, hero на главной)."""
    if request.method == 'POST':
        form = LeadForm(request.POST)
        if form.is_valid():
            lead = form.save(commit=False)
            lead.source_page = request.POST.get('source_page', '')
            lead.save()
            sent = notify_telegram(
                f'📩 Новая заявка ({lead.get_lead_type_display()})\n'
                f'Имя: {lead.name}\nТелефон: {lead.phone}\nEmail: {lead.email}\n'
                f'Сообщение: {lead.message}'
            )
            if sent:
                lead.telegram_notified = True
                lead.save(update_fields=['telegram_notified'])
            messages.success(request, 'Заявка отправлена! Мы свяжемся с вами в ближайшее время.')
    return redirect(request.POST.get('next', 'home'))


def handler404(request, exception=None):
    return render(request, '404.html', status=404)
