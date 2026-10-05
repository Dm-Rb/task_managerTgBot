document.addEventListener("DOMContentLoaded", () => {

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
