from django.core.management.base import BaseCommand

from shop.models import Category, Collection, ColorOption, Material, Product, Review
from shop.utils import ru_slugify

# Цвета отделки: (название, тип, hex). Тип — weave/cushion/frame.
COLORS = [
    ('Графит', ColorOption.WEAVE, '#3b3a36'),
    ('Мокко', ColorOption.WEAVE, '#6f5b45'),
    ('Слоновая кость', ColorOption.WEAVE, '#e8e0d2'),
    ('Терракота', ColorOption.WEAVE, '#b5623a'),
    ('Беж', ColorOption.CUSHION, '#d9cbb3'),
    ('Графитовый лён', ColorOption.CUSHION, '#4a4a45'),
    ('Олива', ColorOption.CUSHION, '#6b6f4f'),
    ('Чёрный муар', ColorOption.FRAME, '#1c1c1c'),
    ('Белый', ColorOption.FRAME, '#f2f2ef'),
    ('Сталь', ColorOption.FRAME, '#8a8d90'),
]

# Габариты демо-товаров: название → (длина, ширина, высота, вес) в см и кг.
DIMENSIONS = {
    'Кресло «Кокон»': (100, 100, 195, 18),
    'Диван «Ривьера»': (210, 85, 80, 42),
    'Кресло «Прованс»': (65, 70, 90, 12),
    'Комплект «Азоре»': (240, 80, 85, 75),
    'Стол обеденный «Соренто»': (180, 90, 75, 40),
    'Шезлонг «Малибу»': (195, 65, 35, 16),
    'Столик кофейный «Верона»': (60, 60, 45, 9),
    'Кресло «Барселона»': (70, 72, 100, 13),
}

# Категории с мягкими элементами — им доступны цвета подушек.
SOFT_CATEGORIES = {'Кресла', 'Диваны', 'Комплекты', 'Шезлонги', 'Подвесные кресла'}

MATERIALS = [
    ('Роуп', 'Роуп дарит мягкость и уют даже в уличных пространствах: мебель выглядит так же изысканно, как и внутри дома.'),
    ('Ротанг', 'Эко-ротанг — материал, который выдерживает десятилетия и не теряет эстетики даже под палящим солнцем или дождём.'),
    ('Шпон', 'Шпон — тонкий лист древесины на металлическом каркасе. Экологичный, водостойкий, не выцветает и не боится перепадов температур.'),
    ('HPL', 'Столбы с HPL подходят и для частного использования, и для общественных заведений — служат не менее 10 лет в любом климате.'),
]

CATEGORIES = [
    'Кресла', 'Диваны', 'Столы обеденные', 'Столы кофейные',
    'Шезлонги', 'Комплекты', 'Подвесные кресла', 'Аксессуары',
]

COLLECTIONS = [
    ('Терраса', 'Коллекция для летних террас и веранд частного дома.'),
    ('Лаунж', 'Мягкие зоны отдыха для отелей, ресторанов и SPA.'),
    ('Сад', 'Всесезонная мебель для сада и открытых пространств.'),
]

PRODUCTS = [
    ('Кресло «Кокон»', 'Роуп', 'Подвесные кресла', 'Терраса', 42000, 'Подвесное кресло-кокон для уютного отдыха на террасе.'),
    ('Диван «Ривьера»', 'Роуп', 'Диваны', 'Лаунж', 128000, 'Трёхместный диван для лаунж-зоны с влагостойкими подушками.'),
    ('Кресло «Прованс»', 'Ротанг', 'Кресла', 'Сад', 36000, 'Классическое кресло из эко-ротанга для сада и веранды.'),
    ('Комплект «Азоре»', 'Ротанг', 'Комплекты', 'Терраса', 245000, 'Комплект: диван, два кресла и кофейный столик.'),
    ('Стол обеденный «Соренто»', 'HPL', 'Столы обеденные', 'Сад', 89000, 'Обеденный стол со столешницей HPL, устойчивой к погоде.'),
    ('Шезлонг «Малибу»', 'Роуп', 'Шезлонги', 'Сад', 54000, 'Регулируемый шезлонг для бассейна и террасы.'),
    ('Столик кофейный «Верона»', 'Шпон', 'Столы кофейные', 'Лаунж', 31000, 'Кофейный столик со столешницей из натурального шпона.'),
    ('Кресло «Барселона»', 'Ротанг', 'Кресла', 'Лаунж', 39000, 'Лаунж-кресло с высокой спинкой из плетёного ротанга.'),
]

REVIEWS = [
    ('Кресло «Кокон»', 'Мария', 5, '1 год', 'Кресло-кокон любимое всеми в семье. Пользуемся с большим удовольствием!'),
    ('Диван «Ривьера»', 'Андрей', 5, '2 года', 'Диван стоит на террасе ресторана круглый год — выглядит как новый.'),
    ('Комплект «Азоре»', 'Елена', 5, '8 месяцев', 'Качество превзошло ожидания, сделали точно под наши размеры.'),
]


class Command(BaseCommand):
    help = 'Наполняет БД демо-данными для разработки и проверки вёрстки.'

    def handle(self, *args, **options):
        materials = {}
        for i, (name, desc) in enumerate(MATERIALS):
            m, _ = Material.objects.get_or_create(
                slug=ru_slugify(name),
                defaults={'name': name, 'description': desc, 'order': i},
            )
            materials[name] = m

        categories = {}
        for i, name in enumerate(CATEGORIES):
            c, _ = Category.objects.get_or_create(
                slug=ru_slugify(name),
                defaults={'name': name, 'order': i},
            )
            categories[name] = c

        collections = {}
        for i, (name, desc) in enumerate(COLLECTIONS):
            col, _ = Collection.objects.get_or_create(
                slug=ru_slugify(name),
                defaults={'name': name, 'description': desc, 'is_featured': True, 'order': i},
            )
            collections[name] = col

        # Цвета отделки, сгруппированные по типу для привязки к товарам.
        colors_by_type = {ColorOption.WEAVE: [], ColorOption.CUSHION: [], ColorOption.FRAME: []}
        for i, (cname, finish_type, hex_code) in enumerate(COLORS):
            color, _ = ColorOption.objects.get_or_create(
                name=cname, finish_type=finish_type,
                defaults={'hex': hex_code, 'order': i},
            )
            colors_by_type[finish_type].append(color)

        products = {}
        for name, mat, cat, col, price, desc in PRODUCTS:
            p, _ = Product.objects.get_or_create(
                slug=ru_slugify(name),
                defaults={
                    'name': name,
                    'material': materials.get(mat),
                    'category': categories.get(cat),
                    'collection': collections.get(col),
                    'price': price,
                    'short_description': desc,
                    'description': desc + '\n\nИзготовлено вручную на собственном производстве ESTIVO. Гарантия 3 года.',
                    'is_featured': True,
                    'is_available': True,
                },
            )
            products[name] = p

            # Габариты (перезаписываем на демо-значения при каждом прогоне).
            dims = DIMENSIONS.get(name)
            if dims:
                p.length_cm, p.width_cm, p.height_cm, p.weight_kg = dims
                p.save(update_fields=['length_cm', 'width_cm', 'height_cm', 'weight_kg'])

            # Привязка палитр: плетение — всем; подушки — мягкой мебели;
            # каркас — всем, кроме ротанга (следуя ТЗ владельца).
            available = list(colors_by_type[ColorOption.WEAVE])
            if cat in SOFT_CATEGORIES:
                available += colors_by_type[ColorOption.CUSHION]
            if mat != 'Ротанг':
                available += colors_by_type[ColorOption.FRAME]
            p.available_colors.set(available)

        for prod_name, author, rating, duration, text in REVIEWS:
            product = products.get(prod_name)
            if product:
                Review.objects.get_or_create(
                    product=product, author=author,
                    defaults={'rating': rating, 'usage_duration': duration, 'text': text, 'is_published': True},
                )

        self.stdout.write(self.style.SUCCESS(
            f'Готово: {Material.objects.count()} материалов, {Category.objects.count()} категорий, '
            f'{Product.objects.count()} товаров, {ColorOption.objects.count()} цветов, '
            f'{Review.objects.count()} отзывов.'
        ))
