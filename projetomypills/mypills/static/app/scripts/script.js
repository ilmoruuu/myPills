function paginaLogin() {
    console.log("Deu certo");
    window.location.href = "{% url 'login' %}";
}