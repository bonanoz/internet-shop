// Переключение основного фото товара по клику на миниатюру
(function () {
    'use strict';
    var main = document.querySelector('.gallery__main img');
    var thumbs = document.querySelectorAll('.gallery__thumbs img');
    if (!main || !thumbs.length) return;

    thumbs.forEach(function (thumb) {
        thumb.addEventListener('click', function () {
            main.src = thumb.dataset.full || thumb.src;
            thumbs.forEach(function (t) { t.classList.remove('active'); });
            thumb.classList.add('active');
        });
    });
})();
