const form = document.getElementById("login-form");
const loginInput = document.getElementById("login");
const passwordInput = document.getElementById("password");

const errorMessage = document.getElementById("error-message");
const loginButton = document.getElementById("login-button");


form.addEventListener("submit", async (event) => {
    event.preventDefault();

    errorMessage.textContent = "";
    loginButton.disabled = true;

    const login = loginInput.value.trim();
    const password = passwordInput.value;

    try {
        const response = await fetch("/api/auth/login", {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            credentials: "same-origin",

            body: JSON.stringify({
                login: login,
                password: password
            })
        });

        if (response.ok) {
            window.location.href = "/";
            return;
        }

        if (response.status === 401) {
            errorMessage.textContent = "Неверный логин или пароль";
            return;
        }

        errorMessage.textContent = "Ошибка авторизации";

    } catch (error) {
        console.error(error);
        errorMessage.textContent = "Не удалось связаться с сервером";

    } finally {
        loginButton.disabled = false;
    }
});