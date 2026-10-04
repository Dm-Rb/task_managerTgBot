document.addEventListener("DOMContentLoaded", () => {

    const copyButton = document.getElementById("copyWebhookButton");
    const feedback = document.getElementById("copyFeedback");

    if (!copyButton) {
        return;
    }

    copyButton.addEventListener("click", async () => {

        const targetId = copyButton.dataset.copyTarget;
        const target = document.getElementById(targetId);

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

        copyButton.textContent = "Скопировано";
        copyButton.classList.add("copied");
        feedback.textContent = "Адрес скопирован в буфер обмена";
        feedback.classList.add("show");

        setTimeout(() => {
            copyButton.textContent = "Скопировать";
            copyButton.classList.remove("copied");
            feedback.classList.remove("show");
        }, 2000);
    });

});
