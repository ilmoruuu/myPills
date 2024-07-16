function paginaLogin() {
    const loginButton = document.querySelector('[onclick="paginaLogin()"]');
    if (loginButton) {
        const url = loginButton.getAttribute('data-url');
        if (url) {
            window.location.href = url;
        }
    }
}