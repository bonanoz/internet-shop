from django.shortcuts import render, redirect
from django.http import HttpResponse

from .models import Product, Review

import telebot

from .config import BOT_TOKEN, CHAT_ID


bot = telebot.TeleBot(BOT_TOKEN)


# Create your views here.
def home(request):
    search = request.GET.get('search')

    if search:
        products = Product.objects.filter(name__contains=search).all()
    else:
        products = Product.objects.all()
    return render(request, "index.html", {
        'products': products,
        'products_found': len(products) > 0,
        'search': search if search else '',
    })


def view_product(request, id):
    product = Product.objects.filter(id=id).first()
    return render(request, 'product.html', {
        'product': product
    })


def payment(request, id):
    product = Product.objects.filter(id=id).first()


    if request.method == "POST":
        name = request.POST.get('name')
        address = request.POST.get('address')
        # Send message to Telegram
        bot.send_message(CHAT_ID, f'''📦 Новый заказ: {product.name}
        💸 Цена: {product.price} рублей
ФИО покупателя: {name}
Адрес доставки: {address}
''')
        return redirect('/success')

    return render(request, "payment.html", {
        'product': product
    })

def success(request):
    return render(request, 'success.html')