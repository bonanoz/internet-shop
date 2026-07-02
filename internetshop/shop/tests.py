from unittest import mock

from django.test import TestCase
from django.urls import reverse

from .models import Category, Lead, Material, Order, Product


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

    def test_home_ok(self):
        self.assertEqual(self.client.get(reverse('home')).status_code, 200)

    def test_static_pages_ok(self):
        for name in ['catalog_list', 'b2b_page', 'designers_page', 'about_page',
                     'delivery_payment_page', 'warranty_page', 'faq_page', 'contacts_page']:
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

    @mock.patch('shop.views.notify_telegram', return_value=True)
    def test_order_create_saves_to_db(self, mock_notify):
        resp = self.client.post(reverse('order_create', args=[self.product.id]), {
            'customer_name': 'Иван',
            'customer_phone': '+7 900 123-45-67',
            'customer_email': '',
            'delivery_address': 'Тольятти',
            'comment': '',
        })
        self.assertEqual(resp.status_code, 302)
        order = Order.objects.get()
        self.assertEqual(order.customer_name, 'Иван')
        self.assertEqual(order.total_price, 42000)  # цена зафиксирована на момент заявки
        self.assertTrue(order.telegram_notified)
        mock_notify.assert_called_once()

    @mock.patch('shop.views.notify_telegram', return_value=True)
    def test_lead_form_saves(self, mock_notify):
        resp = self.client.post(reverse('b2b_page'), {
            'name': 'Отель Ромашка',
            'phone': '+7 900 123-45-67',
            'email': '',
            'lead_type': 'b2b',
            'message': 'Нужно 40 кресел',
        })
        self.assertEqual(resp.status_code, 302)
        lead = Lead.objects.get()
        self.assertEqual(lead.lead_type, 'b2b')

    def test_handler404(self):
        resp = self.client.get('/nesushchestvuyushchaya-stranica/')
        self.assertEqual(resp.status_code, 404)
