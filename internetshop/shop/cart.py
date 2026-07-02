"""Корзина на сессии.

Регистрации/логина на сайте нет, поэтому корзина живёт в ``request.session``.
Позиция уникальна по комбинации товара и выбранных цветов отделки — один и
тот же товар с разными цветами попадает в корзину как две отдельные позиции.
"""

from .models import ColorOption, Product

CART_SESSION_ID = 'cart'


def _line_id(product_id, colors):
    """Детерминированный ключ позиции: товар + выбранные цвета.

    Один товар с одинаковым набором цветов всегда даёт один ключ (повторное
    добавление увеличивает количество), а другой набор цветов — новую позицию.
    """
    parts = [f'{ft}={cid}' for ft, cid in sorted(colors.items())]
    return f'{product_id}:' + '-'.join(parts)


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_ID)
        if cart is None:
            cart = self.session[CART_SESSION_ID] = {}
        self._cart = cart

    def add(self, product, colors=None, quantity=1):
        """Добавить товар с выбранными цветами (``{finish_type: color_id}``)."""
        colors = colors or {}
        line_id = _line_id(product.id, colors)
        if line_id in self._cart:
            self._cart[line_id]['quantity'] += quantity
        else:
            self._cart[line_id] = {
                'product_id': product.id,
                'quantity': quantity,
                'colors': colors,
            }
        self.save()
        return line_id

    def set_quantity(self, line_id, quantity):
        if line_id in self._cart:
            if quantity > 0:
                self._cart[line_id]['quantity'] = quantity
            else:
                del self._cart[line_id]
            self.save()

    def remove(self, line_id):
        if line_id in self._cart:
            del self._cart[line_id]
            self.save()

    def clear(self):
        self.session[CART_SESSION_ID] = self._cart = {}
        self.save()

    def save(self):
        self.session.modified = True

    def __iter__(self):
        """Позиции корзины с подгруженными товарами и названиями цветов.

        Позиции с удалённым из БД товаром молча пропускаются.
        """
        product_ids = [item['product_id'] for item in self._cart.values()]
        products = Product.objects.in_bulk(product_ids)

        color_ids = set()
        for item in self._cart.values():
            color_ids.update(item.get('colors', {}).values())
        colors = ColorOption.objects.in_bulk(list(color_ids)) if color_ids else {}

        for line_id, item in self._cart.items():
            product = products.get(item['product_id'])
            if product is None:
                continue
            colors_map = item.get('colors', {})
            colors_display = []
            for finish_type, label in ColorOption.FINISH_TYPE_CHOICES:
                color_id = colors_map.get(finish_type)
                color = colors.get(color_id)
                if color is not None:
                    colors_display.append((label, color.name))
            quantity = item['quantity']
            yield {
                'line_id': line_id,
                'product': product,
                'quantity': quantity,
                'colors': colors_map,
                'colors_display': colors_display,
                'unit_price': product.price,
                'line_total': product.price * quantity,
            }

    def __len__(self):
        return sum(item['quantity'] for item in self._cart.values())

    @property
    def count(self):
        return len(self)

    @property
    def total_price(self):
        return sum(item['line_total'] for item in self)

    @property
    def is_empty(self):
        return not self._cart
