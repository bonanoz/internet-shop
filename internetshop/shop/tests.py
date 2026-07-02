from unittest import mock

from django.test import TestCase
from django.urls import reverse

from .models import Category, ColorOption, Lead, Material, Order, Product


class SmokeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.material = Material.objects.create(name='Ротанг', slug='rotang')
        cls.other_material = Material.objects.create(name='Роуп', slug='roup')
        cls.category = Category.objects.create(name='Кресла', slug='kresla')
        cls.product = Product.objects.create(
            name='Кресло Тест', slug='kreslo-test', description='Описание',
            material=cls.material, category=cls.category, price=42000,
        )
        Product.objects.create(
            name='Диван Роуп', slug='divan-roup', description='Другой материал',
            material=cls.other_material, price=100000,
        )
        cls.weave = ColorOption.objects.create(name='Графит', finish_type=ColorOption.WEAVE, hex='#3b3a36')
        cls.weave2 = ColorOption.objects.create(name='Мокко', finish_type=ColorOption.WEAVE, hex='#6f5b45')
        cls.foreign = ColorOption.objects.create(name='Чужой', finish_type=ColorOption.WEAVE, hex='#000000')
        cls.product.available_colors.set([cls.weave, cls.weave2])

    def test_home_ok(self):
        self.assertEqual(self.client.get(reverse('home')).status_code, 200)

    def test_static_pages_ok(self):
        for name in ['catalog_list', 'b2b_page', 'designers_page', 'about_page',
                     'delivery_payment_page', 'warranty_page', 'faq_page', 'contacts_page', 'cart_detail']:
            self.assertEqual(self.client.get(reverse(name)).status_code, 200, name)

    def test_product_detail_ok(self):
        resp = self.client.get(self.product.get_absolute_url())
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Кресло Тест')

    def test_catalog_filters_by_material(self):
        resp = self.client.get(reverse('catalog_by_material', args=['rotang']))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Кресло Тест')
        self.assertNotContains(resp, 'Диван Роуп')

    def test_lead_form_saves(self):
        with mock.patch('shop.views.notify_telegram', return_value=True):
            resp = self.client.post(reverse('b2b_page'), {
                'name': 'Отель Ромашка',
                'phone': '+7 900 123-45-67',
                'email': '',
                'lead_type': 'b2b',
                'message': 'Нужно 40 кресел',
            })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Lead.objects.get().lead_type, 'b2b')

    def test_handler404(self):
        resp = self.client.get('/nesushchestvuyushchaya-stranica/')
        self.assertEqual(resp.status_code, 404)


class CartTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name='Кресла', slug='kresla')
        cls.product = Product.objects.create(
            name='Кресло Тест', slug='kreslo-test', description='Описание',
            category=cls.category, price=42000,
        )
        cls.weave = ColorOption.objects.create(name='Графит', finish_type=ColorOption.WEAVE, hex='#3b3a36')
        cls.weave2 = ColorOption.objects.create(name='Мокко', finish_type=ColorOption.WEAVE, hex='#6f5b45')
        cls.foreign = ColorOption.objects.create(name='Чужой', finish_type=ColorOption.WEAVE, hex='#000000')
        cls.product.available_colors.set([cls.weave, cls.weave2])

    def test_cart_add_creates_line(self):
        resp = self.client.post(reverse('cart_add', args=[self.product.id]), {'color_weave': self.weave.id})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(len(self.client.session['cart']), 1)

    def test_cart_add_ajax_returns_count(self):
        resp = self.client.post(
            reverse('cart_add', args=[self.product.id]), {'quantity': 2},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['count'], 2)

    def test_cart_rejects_foreign_color(self):
        """Цвет, не привязанный к товару, не попадает в позицию (защита от подмены)."""
        self.client.post(reverse('cart_add', args=[self.product.id]), {'color_weave': self.foreign.id})
        line = next(iter(self.client.session['cart'].values()))
        self.assertEqual(line['colors'], {})

    def test_same_product_different_colors_are_separate_lines(self):
        self.client.post(reverse('cart_add', args=[self.product.id]), {'color_weave': self.weave.id})
        self.client.post(reverse('cart_add', args=[self.product.id]), {'color_weave': self.weave2.id})
        self.assertEqual(len(self.client.session['cart']), 2)

    def test_same_product_same_color_increments_quantity(self):
        self.client.post(reverse('cart_add', args=[self.product.id]), {'color_weave': self.weave.id})
        self.client.post(reverse('cart_add', args=[self.product.id]), {'color_weave': self.weave.id})
        cart = self.client.session['cart']
        self.assertEqual(len(cart), 1)
        self.assertEqual(next(iter(cart.values()))['quantity'], 2)

    def test_checkout_creates_order_with_items(self):
        self.client.post(reverse('cart_add', args=[self.product.id]), {'color_weave': self.weave.id})
        with mock.patch('shop.views.notify_telegram', return_value=True) as mock_notify:
            resp = self.client.post(reverse('checkout'), {
                'customer_name': 'Иван',
                'customer_phone': '+7 900 123-45-67',
                'customer_email': '',
                'delivery_address': 'Тольятти',
                'comment': '',
            })
        self.assertRedirects(resp, reverse('order_success'))
        order = Order.objects.get()
        self.assertEqual(order.items.count(), 1)
        item = order.items.first()
        self.assertEqual(item.unit_price, 42000)
        self.assertEqual(item.selected_colors, {'Плетение': 'Графит'})
        self.assertEqual(order.total_price, 42000)
        self.assertTrue(order.telegram_notified)
        mock_notify.assert_called_once()
        self.assertFalse(self.client.session.get('cart'))

    def test_checkout_empty_cart_redirects(self):
        resp = self.client.get(reverse('checkout'))
        self.assertRedirects(resp, reverse('cart_detail'))


class ProductConfiguratorTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name='Кресла', slug='kresla')
        cls.product = Product.objects.create(
            name='Кресло Тест', slug='kreslo-test', description='Описание',
            category=cls.category, price=42000,
            length_cm=100, width_cm=90, height_cm=80, weight_kg=15,
        )
        cls.weave = ColorOption.objects.create(name='Графит', finish_type=ColorOption.WEAVE, hex='#3b3a36')
        cls.product.available_colors.set([cls.weave])

    def test_shows_colors_and_dimensions(self):
        resp = self.client.get(self.product.get_absolute_url())
        self.assertContains(resp, 'Плетение')
        self.assertContains(resp, 'swatch')
        self.assertContains(resp, 'Габариты')
        self.assertContains(resp, '100 × 90 × 80 см')

    def test_renders_model_viewer_when_model_present(self):
        self.product.model_3d.name = 'models/test.glb'
        self.product.save(update_fields=['model_3d'])
        resp = self.client.get(self.product.get_absolute_url())
        self.assertContains(resp, '<model-viewer')

    def test_colors_by_type_skips_empty_groups(self):
        # У товара только плетение — групп «Подушки»/«Каркас» быть не должно.
        groups = self.product.colors_by_type()
        self.assertEqual([g[1] for g in groups], [ColorOption.WEAVE])
