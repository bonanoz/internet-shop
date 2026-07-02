from django.core.management.base import BaseCommand

from shop.models import Category, Collection, Material, Product, Review
from shop.utils import ru_slugify

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

        for prod_name, author, rating, duration, text in REVIEWS:
            product = products.get(prod_name)
            if product:
                Review.objects.get_or_create(
                    product=product, author=author,
                    defaults={'rating': rating, 'usage_duration': duration, 'text': text, 'is_published': True},
                )

        self.stdout.write(self.style.SUCCESS(
            f'Готово: {Material.objects.count()} материалов, {Category.objects.count()} категорий, '
            f'{Product.objects.count()} товаров, {Review.objects.count()} отзывов.'
        ))
