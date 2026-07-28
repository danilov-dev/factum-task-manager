// ============================================
// User dropdown menu (только если пользователь авторизован)
// ============================================
const userMenu = document.getElementById('userMenu');
const dropdownMenu = document.getElementById('dropdownMenu');

if (userMenu && dropdownMenu) {
    const userAvatar = userMenu.querySelector('.user-avatar');

    if (userAvatar) {
        userAvatar.addEventListener('click', (e) => {
            e.stopPropagation();
            dropdownMenu.classList.toggle('show');
        });
    }

    // Close dropdown when clicking outside
    document.addEventListener('click', (e) => {
        if (!userMenu.contains(e.target)) {
            dropdownMenu.classList.remove('show');
        }
    });

    // Close dropdown on escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            dropdownMenu.classList.remove('show');
        }
    });
}

document.addEventListener('DOMContentLoaded', function () {
    const messages = document.querySelectorAll('.message');

    messages.forEach(message => {
        setTimeout(() => {
            message.remove();

            // Если контейнер messages стал пустым, удаляем и его
            const messagesContainer = document.getElementById('messages');
            if (messagesContainer && messagesContainer.children.length === 0) {
                messagesContainer.remove();
            }
        }, 3000); // Скрыть через 3 секунды
    });
});