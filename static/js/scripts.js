document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.btn-confirm-delete').forEach(function (button) {
        button.addEventListener('click', function (event) {
            if (!confirm('Tem certeza de que deseja realizar esta operação?')) {
                event.preventDefault();
            }
        });
    });
});
