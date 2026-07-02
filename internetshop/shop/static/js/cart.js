// Корзина: AJAX добавление/изменение/удаление без перезагрузки.
// Прогрессивное улучшение — если fetch падает, форма отправляется обычным POST.
(function () {
    function getCsrf(form) {
        var el = form.querySelector('[name=csrfmiddlewaretoken]');
        return el ? el.value : '';
    }

    function fmt(n) {
        return n + ' ₽';
    }

    function updateTotals(data) {
        document.querySelectorAll('[data-cart-count]').forEach(function (el) {
            el.textContent = data.count;
            if (el.classList.contains('header-cart__count')) {
                el.hidden = !data.count;
            }
        });
        document.querySelectorAll('[data-cart-total]').forEach(function (el) {
            el.textContent = fmt(data.total_price);
        });
    }

    function flash(form) {
        var btn = form.querySelector('[type=submit]');
        if (!btn) return;
        var original = btn.dataset.label || btn.textContent;
        btn.dataset.label = original;
        btn.textContent = 'Добавлено ✓';
        btn.disabled = true;
        setTimeout(function () {
            btn.textContent = original;
            btn.disabled = false;
        }, 1600);
    }

    function afterEmpty() {
        if (!document.querySelector('.cart-item')) {
            window.location.reload();
        }
    }

    function submitForm(form) {
        var action = form.dataset.cartAction;
        var body = new FormData(form);
        fetch(form.action, {
            method: 'POST',
            headers: { 'X-Requested-With': 'XMLHttpRequest', 'X-CSRFToken': getCsrf(form) },
            body: body,
        })
            .then(function (r) { return r.ok ? r.json() : Promise.reject(r); })
            .then(function (res) {
                updateTotals(res);
                var row = form.closest('[data-line]');
                if (action === 'remove' || (action === 'update' && res.removed)) {
                    if (row) row.remove();
                    afterEmpty();
                } else if (action === 'update' && row) {
                    var qty = parseInt(body.get('quantity'), 10) || 1;
                    var unit = parseInt(row.dataset.unitPrice, 10) || 0;
                    var totalEl = row.querySelector('[data-line-total]');
                    if (totalEl) totalEl.textContent = fmt(unit * qty);
                } else if (action === 'add') {
                    flash(form);
                }
            })
            .catch(function () { form.submit(); });
    }

    document.addEventListener('submit', function (e) {
        var form = e.target.closest('.js-cart-form');
        if (!form) return;
        // Кнопка с data-no-ajax («Оформить заявку») отправляется обычным POST,
        // чтобы сервер добавил товар в корзину и сделал redirect на checkout.
        if (e.submitter && e.submitter.hasAttribute('data-no-ajax')) return;
        e.preventDefault();
        submitForm(form);
    });

    document.addEventListener('click', function (e) {
        var dec = e.target.closest('[data-qty-dec]');
        var inc = e.target.closest('[data-qty-inc]');
        if (!dec && !inc) return;
        var form = e.target.closest('form');
        var input = form.querySelector('.qty__input');
        var value = parseInt(input.value, 10) || 1;
        value = inc ? value + 1 : Math.max(1, value - 1);
        input.value = value;
        submitForm(form);
    });
})();
