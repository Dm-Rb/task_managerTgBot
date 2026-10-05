document.addEventListener("DOMContentLoaded", () => {

    const PAGE_SIZE = 10;

    const listEl = document.getElementById("smsList");
    const emptyEl = document.getElementById("smsEmpty");
    const paginationEl = document.getElementById("smsPagination");
    const pageInfoEl = document.getElementById("smsPageInfo");
    const prevButton = document.getElementById("smsPrevPage");
    const nextButton = document.getElementById("smsNextPage");

    const deleteModal = document.getElementById("smsDeleteModal");
    const deleteCancel = document.getElementById("smsDeleteCancel");
    const deleteConfirm = document.getElementById("smsDeleteConfirm");

    let currentPage = 1;
    let totalPages = 1;
    let pendingDeleteId = null;

    // --- загрузка данных ---

    async function loadPage(page) {

        const response = await fetch(`/api/sms?page=${page}&limit=${PAGE_SIZE}`, {
            credentials: "same-origin",
        });

        if (!response.ok) {
            listEl.innerHTML = "";
            emptyEl.textContent = "Не удалось загрузить сообщения";
            emptyEl.classList.remove("hidden");
            paginationEl.classList.add("hidden");
            return;
        }

        const data = await response.json();
        // ожидаемый формат: { items: [...], total: number }

        currentPage = page;
        totalPages = Math.max(Math.ceil(data.total / PAGE_SIZE), 1);

        renderList(data.items);
        renderPagination();
    }

    // --- рендер списка ---

    function renderList(items) {

        listEl.innerHTML = "";

        if (!items || items.length === 0) {
            emptyEl.textContent = "Пока нет ни одного сообщения";
            emptyEl.classList.remove("hidden");
            return;
        }

        emptyEl.classList.add("hidden");

        for (const item of items) {
            listEl.appendChild(renderCard(item));
        }
    }

    function renderCard(item) {

        const card = document.createElement("div");
        card.className = "sms-card";
        card.dataset.id = item.id;

        const body = document.createElement("div");
        body.className = "sms-card-body";

        const date = document.createElement("div");
        date.className = "sms-date";
        date.textContent = formatDate(item.completed_at);

        const from = document.createElement("div");
        from.className = "sms-from";
        from.textContent = item.from_ ?? item.from ?? "";

        const text = document.createElement("div");
        text.className = "sms-text";
        text.textContent = item.text;

        const expandButton = document.createElement("button");
        expandButton.className = "sms-expand-button hidden";
        expandButton.type = "button";
        expandButton.textContent = "Показать полностью";

        expandButton.addEventListener("click", () => {
            const isExpanded = text.classList.toggle("expanded");
            expandButton.textContent = isExpanded ? "Свернуть" : "Показать полностью";
        });

        body.append(date, from, text, expandButton);

        const deleteButton = document.createElement("button");
        deleteButton.className = "sms-delete-button";
        deleteButton.type = "button";
        deleteButton.setAttribute("aria-label", "Удалить сообщение");
        deleteButton.textContent = "🗑";

        deleteButton.addEventListener("click", () => {
            pendingDeleteId = item.id;
            deleteModal.classList.add("show");
        });

        card.append(body, deleteButton);

        // проверяем, действительно ли текст обрезан (после вставки в DOM)
        requestAnimationFrame(() => {
            if (text.scrollHeight > text.clientHeight + 1) {
                expandButton.classList.remove("hidden");
            }
        });

        return card;
    }

    function formatDate(value) {
        const date = new Date(value);
        if (Number.isNaN(date.getTime())) {
            return value;
        }
        return date.toLocaleString("ru-RU", {
            day: "2-digit",
            month: "2-digit",
            year: "numeric",
            hour: "2-digit",
            minute: "2-digit",
        });
    }

    // --- пагинация ---

    function renderPagination() {

        if (totalPages <= 1) {
            paginationEl.classList.add("hidden");
            return;
        }

        paginationEl.classList.remove("hidden");
        pageInfoEl.textContent = `Страница ${currentPage} из ${totalPages}`;
        prevButton.disabled = currentPage <= 1;
        nextButton.disabled = currentPage >= totalPages;
    }

    prevButton.addEventListener("click", () => {
        if (currentPage > 1) {
            loadPage(currentPage - 1);
        }
    });

    nextButton.addEventListener("click", () => {
        if (currentPage < totalPages) {
            loadPage(currentPage + 1);
        }
    });

    // --- удаление ---

    deleteCancel.addEventListener("click", () => {
        pendingDeleteId = null;
        deleteModal.classList.remove("show");
    });

    deleteConfirm.addEventListener("click", async () => {

        if (pendingDeleteId === null) {
            return;
        }

        const response = await fetch(`/api/sms/${pendingDeleteId}`, {
            method: "DELETE",
            credentials: "same-origin",
        });

        deleteModal.classList.remove("show");

        if (!response.ok) {
            pendingDeleteId = null;
            return;
        }

        pendingDeleteId = null;

        // если удалили последнюю запись на странице (и страница не первая) — переходим на предыдущую
        const remainingOnPage = listEl.children.length - 1;
        if (remainingOnPage === 0 && currentPage > 1) {
            loadPage(currentPage - 1);
        } else {
            loadPage(currentPage);
        }
    });

    // --- старт ---

    loadPage(1);

});