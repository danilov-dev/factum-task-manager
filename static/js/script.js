document.addEventListener('DOMContentLoaded', function () {
    const toasts = document.querySelectorAll('.toast');
    toasts.forEach(toast => {
        setTimeout(() => {
            toast.classList.add('hiding');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    });
});

// Открывает и закрывает текстовый блок
document.addEventListener('click', function (e) {
    if (e.target.classList.contains('expandable-text')) {
        e.target.classList.toggle('expanded');
    }
});