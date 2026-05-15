// Глобальная функция для показа модального окна с требованием авторизации
window.showAuthModal = function(message) {
    const modalElement = document.getElementById('authModal');
    if (!modalElement) {
        // Если модального окна нет на странице, перенаправляем на страницу входа
        window.location.href = '/accounts/login/?next=' + encodeURIComponent(window.location.pathname);
        return false;
    }

    const messageElement = document.getElementById('authModalMessage');
    if (messageElement && message) {
        messageElement.textContent = message;
    }

    const modal = new bootstrap.Modal(modalElement);
    modal.show();
    return false;
};

// Проверка аутентификации (устанавливается из шаблона)
window.isAuthenticated = window.isAuthenticated || false;

// Защита действий, требующих авторизации
document.addEventListener('DOMContentLoaded', function() {
    // Все элементы с классом require-auth требуют авторизации
    document.querySelectorAll('.require-auth').forEach(el => {
        el.addEventListener('click', function(e) {
            if (!window.isAuthenticated) {
                e.preventDefault();
                e.stopPropagation();
                const message = this.dataset.authMessage || 'Для выполнения этого действия необходимо войти или зарегистрироваться.';
                window.showAuthModal(message);
                return false;
            }
        });
    });
});