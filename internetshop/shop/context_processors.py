SITE_INFO = {
    'brand_name': 'ESTIVO',
    'phone': '+7 927 200 43 03',
    'phone_href': '+79272004303',
    'email': 'esti-vo@mail.ru',
    'address': 'г. Тольятти, б-р Туполева 12А, офис 2-4',
    'work_hours': [
        ('Пн-Пт', '10:00–19:00'),
        ('Сб', '10:00–18:00'),
        ('Вс', '10:00–17:00'),
    ],
    'work_hours_note': 'Работаем по предварительной записи',
    'social_links': {
        'instagram': 'https://www.instagram.com/estivo.tlt',
        'whatsapp': 'https://wa.me/79272004303',
        'telegram': 'https://t.me/+7zVfVsf1abszODYy',
        'vk': 'https://vk.com/estivo_tlt',
        'pinterest': 'https://pin.it/4AWL8Yise',
    },
    'legal_name': 'ИП Мелихова Мирослава Сергеевна',
    'inn': '632147606449',
    'ogrnip': '323632700013220',
}


def site_info(request):
    """Контакты, соцсети и реквизиты компании — доступны в любом шаблоне
    без передачи вручную из каждого view (шапка/подвал сайта)."""
    return {'site_info': SITE_INFO}


def cart(request):
    """Корзина — доступна в любом шаблоне (счётчик в шапке на всех страницах)."""
    from .cart import Cart
    return {'cart': Cart(request)}
