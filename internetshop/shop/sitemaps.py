from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Product


class ProductSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Product.objects.filter(is_available=True)

    def location(self, item):
        return item.get_absolute_url()

    def lastmod(self, item):
        return item.updated_at


class StaticViewSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.5

    def items(self):
        return [
            'home', 'catalog_list', 'b2b_page', 'designers_page', 'about_page',
            'delivery_payment_page', 'warranty_page', 'faq_page', 'contacts_page',
        ]

    def location(self, item):
        return reverse(item)
