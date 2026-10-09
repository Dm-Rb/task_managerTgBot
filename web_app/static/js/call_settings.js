document.addEventListener("DOMContentLoaded", () => {

    // --- системный промпт ---

    const promptTextarea = document.getElementById("promptTextarea");
    const savePromptButton = document.getElementById("savePromptButton");
    const promptStatus = document.getElementById("promptStatus");

    function showPromptStatus(text, isError = false) {
        promptStatus.textContent = text;
        promptStatus.classList.toggle("error", isError);
        promptStatus.classList.add("show");

        setTimeout(() => {
            promptStatus.classList.remove("show");
        }, 2000);
    }

    async function loadPrompt() {

        try {
            const response = await fetch("/api/calls/prompt", {
                credentials: "same-origin",
            });

            if (!response.ok) {
                throw new Error("Не удалось загрузить промпт");
            }

            const data = await response.json();
            promptTextarea.value = data.prompt ?? "";
            promptTextarea.placeholder = "";

        } catch (err) {
            promptTextarea.placeholder = "Не удалось загрузить промпт";
        } finally {
            promptTextarea.disabled = false;
            savePromptButton.disabled = false;
        }
    }

    async function savePrompt() {

        savePromptButton.disabled = true;
        savePromptButton.textContent = "Сохранение...";

        try {
            const response = await fetch("/api/calls/prompt", {
                method: "POST",
                credentials: "same-origin",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ prompt: promptTextarea.value }),
            });

            if (!response.ok) {
                throw new Error("Не удалось сохранить промпт");
            }

            showPromptStatus("Сохранено");

        } catch (err) {
            showPromptStatus("Ошибка сохранения", true);
        } finally {
            savePromptButton.disabled = false;
            savePromptButton.textContent = "Сохранить";
        }
    }

    if (promptTextarea && savePromptButton) {
        loadPrompt();
        savePromptButton.addEventListener("click", savePrompt);
    }

    // --- копирование полей ---

    const copyButtons = document.querySelectorAll(".copy-button[data-copy-target]");

    copyButtons.forEach((button) => {

        button.addEventListener("click", async () => {

            const targetId = button.dataset.copyTarget;
            const target = document.getElementById(targetId);
            const feedback = document.querySelector(`[data-feedback-for="${targetId}"]`);

            if (!target) {
                return;
            }

            const text = target.textContent.trim();

            try {
                await navigator.clipboard.writeText(text);
            } catch (err) {
                // запасной вариант для браузеров без Clipboard API (например, http без TLS)
                const range = document.createRange();
                range.selectNode(target);
                window.getSelection().removeAllRanges();
                window.getSelection().addRange(range);
                document.execCommand("copy");
                window.getSelection().removeAllRanges();
            }

            const originalLabel = button.textContent;
            button.textContent = "Скопировано";
            button.classList.add("copied");

            if (feedback) {
                feedback.textContent = "Скопировано в буфер обмена";
                feedback.classList.add("show");
            }

            setTimeout(() => {
                button.textContent = originalLabel;
                button.classList.remove("copied");
                if (feedback) {
                    feedback.classList.remove("show");
                }
            }, 2000);
        });

    });

});
