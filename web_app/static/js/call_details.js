document.addEventListener("DOMContentLoaded", () => {

    const PAGE_SIZE = 10;

    const listEl = document.getElementById("callList");
    const emptyEl = document.getElementById("callEmpty");
    const paginationEl = document.getElementById("callPagination");
    const pageInfoEl = document.getElementById("callPageInfo");
    const prevButton = document.getElementById("callPrevPage");
    const nextButton = document.getElementById("callNextPage");

    const deleteModal = document.getElementById("callDeleteModal");
    const deleteCancel = document.getElementById("callDeleteCancel");
    const deleteConfirm = document.getElementById("callDeleteConfirm");

    let currentPage = 1;
    let totalPages = 1;
    let pendingDeleteId = null;

    // --- загрузка данных ---

    async function loadPage(page) {

        const response = await fetch(`/api/calls?page=${page}&limit=${PAGE_SIZE}`, {
            credentials: "same-origin",
        });

        if (!response.ok) {
            listEl.innerHTML = "";
            emptyEl.textContent = "Не удалось загрузить звонки";
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
            emptyEl.textContent = "Пока нет ни одного звонка";
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
        card.className = "call-card";
        card.dataset.id = item.id;

        const body = document.createElement("div");
        body.className = "call-card-body";

        const date = document.createElement("div");
        date.className = "call-date";
        date.textContent = formatDate(item.completed_at);

        body.append(date);

        // исходящий номер — отображается всегда
        const fromNumber = item.from_ ?? item.from ?? "";
        body.append(renderNumberRow(fromNumber, "outgoing"));

        // входящий номер — только если он есть
        const toNumber = item.to_ ?? item.to ?? null;
        if (toNumber) {
            body.append(renderNumberRow(toNumber, "incoming"));
        }

        const shortText = document.createElement("div");
        shortText.className = "call-short-text";
        shortText.textContent = item.short_text ?? "";
        body.append(shortText);

        if (item.text) {
            const text = document.createElement("div");
            text.className = "call-text";
            text.textContent = item.text;

            const expandButton = document.createElement("button");
            expandButton.className = "call-expand-button";
            expandButton.type = "button";
            expandButton.textContent = "Показать полностью";

            expandButton.addEventListener("click", () => {
                const isExpanded = text.classList.toggle("expanded");
                expandButton.textContent = isExpanded ? "Свернуть" : "Показать полностью";
            });

            body.append(text, expandButton);
        }

        const deleteButton = document.createElement("button");
        deleteButton.className = "call-delete-button";
        deleteButton.type = "button";
        deleteButton.setAttribute("aria-label", "Удалить запись");
        deleteButton.textContent = "🗑";

        deleteButton.addEventListener("click", () => {
            pendingDeleteId = item.id;
            deleteModal.classList.add("show");
        });

        card.append(body, deleteButton);

        return card;
    }

    function renderNumberRow(number, direction) {

        const row = document.createElement("div");
        row.className = "call-number";

        const icon = document.createElement("span");
        icon.className = `call-number-icon ${direction}`;
        icon.textContent = direction === "outgoing" ? "↗" : "↙";
        icon.setAttribute(
            "aria-label",
            direction === "outgoing" ? "Исходящий номер" : "Входящий номер"
        );

        const numberText = document.createElement("span");
        numberText.textContent = number;

        row.append(icon, numberText);

        return row;
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

        const response = await fetch(`/api/calls/${pendingDeleteId}`, {
            method: "DELETE",
            credentials: "same-origin",
        });

        deleteModal.classList.remove("show");

        if (!response.ok) {
            pendingDeleteId = null;
            return;
        }

        pendingDeleteId = null;

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
