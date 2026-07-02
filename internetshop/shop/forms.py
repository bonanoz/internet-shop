from django import forms

from .models import Lead, Order
from .utils import clean_phone_number


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer_name', 'customer_phone', 'customer_email', 'delivery_address', 'comment']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ваше имя'}),
            'customer_phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+7 900 000-00-00'}),
            'customer_email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email (необязательно)'}),
            'delivery_address': forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'placeholder': 'Адрес доставки'}),
            'comment': forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'placeholder': 'Комментарий к заявке'}),
        }

    def clean_customer_phone(self):
        try:
            return clean_phone_number(self.cleaned_data['customer_phone'])
        except ValueError as exc:
            raise forms.ValidationError(str(exc))


class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ['name', 'phone', 'email', 'lead_type', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ваше имя'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+7 900 000-00-00'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email (необязательно)'}),
            'lead_type': forms.HiddenInput(),
            'message': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Расскажите о вашем проекте'}),
        }

    def clean_phone(self):
        try:
            return clean_phone_number(self.cleaned_data['phone'])
        except ValueError as exc:
            raise forms.ValidationError(str(exc))
