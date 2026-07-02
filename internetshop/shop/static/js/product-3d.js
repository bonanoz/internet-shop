// Конфигуратор цвета на странице товара.
// 1) Обновляет подпись выбранного цвета в каждой группе (работает всегда).
// 2) Если на странице есть <model-viewer>, перекрашивает материал .glb-модели.
//    Соглашение: материалы в модели называются weave / cushion / frame —
//    ровно как finish_type в поле name="color_<finish_type>".
(function () {
    function hexToRgb(hex) {
        hex = (hex || '').replace('#', '');
        if (hex.length === 3) {
            hex = hex.split('').map(function (c) { return c + c; }).join('');
        }
        var n = parseInt(hex, 16);
        if (isNaN(n)) return [0.8, 0.8, 0.8, 1];
        return [((n >> 16) & 255) / 255, ((n >> 8) & 255) / 255, (n & 255) / 255, 1];
    }

    var viewer = document.querySelector('[data-model-3d] model-viewer');

    function paint(finishType, hex) {
        if (!viewer || !viewer.model) return;
        var material = viewer.model.materials.find(function (m) { return m.name === finishType; });
        if (material) {
            material.pbrMetallicRoughness.setBaseColorFactor(hexToRgb(hex));
        }
    }

    function finishOf(input) {
        return input.name.replace('color_', '');
    }

    function onSelect(input) {
        var group = input.closest('.color-group');
        var valueEl = group ? group.querySelector('.color-group__value') : null;
        if (valueEl) valueEl.textContent = input.dataset.name || '';
        paint(finishOf(input), input.dataset.hex);
    }

    document.addEventListener('change', function (e) {
        var input = e.target.closest('.color-group input[type=radio]');
        if (input && input.checked) onSelect(input);
    });

    // Когда модель загрузилась — применяем уже выбранные (по умолчанию первые) цвета.
    if (viewer) {
        viewer.addEventListener('load', function () {
            document.querySelectorAll('.color-group input[type=radio]:checked').forEach(function (input) {
                paint(finishOf(input), input.dataset.hex);
            });
        });
    }
})();
