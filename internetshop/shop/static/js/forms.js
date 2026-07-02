// UX форм: простая маска телефона + защита от двойной отправки
(function () {
    'use strict';

    // ---- Маска телефона ----
    document.querySelectorAll('input[name="phone"], input[name="customer_phone"]').forEach(function (input) {
        input.addEventListener('input', function () {
            var digits = input.value.replace(/\D/g, '');
            if (digits.startsWith('8')) digits = '7' + digits.slice(1);
            if (!digits.startsWith('7')) digits = '7' + digits;
            digits = digits.slice(0, 11);

            var out = '+7';
            if (digits.length > 1) out += ' ' + digits.slice(1, 4);
            if (digits.length >= 5) out += ' ' + digits.slice(4, 7);
            if (digits.length >= 8) out += '-' + digits.slice(7, 9);
            if (digits.length >= 10) out += '-' + digits.slice(9, 11);
            input.value = out;
        });
    });

    // ---- Защита от двойной отправки ----
    document.querySelectorAll('form[data-once]').forEach(function (form) {
        form.addEventListener('submit', function () {
            var btn = form.querySelector('button[type="submit"], .btn[type="submit"]');
            if (btn) {
                setTimeout(function () { btn.disabled = true; btn.textContent = 'Отправка…'; }, 0);
            }
        });
    });
})();
