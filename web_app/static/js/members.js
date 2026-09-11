let members = [];
let deletingUserId = null;

const GET_USERS_URL = "/api/get_users";

function getRoleInfo(role) {
    switch (role) {
        case 2:
            return {
                icon: "🧑🏻‍💻",
                name: "Администратор"
            };

        case 1:
        default:
            return {
                icon: "👨🏻‍💼",
                name: "Сотрудник"
            };

        case 2:
            return {
                icon: "❓",
                name: "Не авторизирован"
            };
    }
}

function getMemberName(member) {
    return [
        member.first_name,
        member.last_name
    ]
        .filter(Boolean)
        .join(" ") || "Без имени";
}

function escapeHtml(value) {
    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function getBanStatus(member) {
    if (member.is_banned === true) {
        return `
            <span class="participant-banned">
                  Забанен
            </span>
        `;
    }

    return "";
}

function renderMembers() {
    const list =
        document.getElementById("membersList");

    if (!list) {
        return;
    }

    if (members.length === 0) {
        list.innerHTML = `
            <div class="placeholder">
                Список участников пуст.
            </div>
        `;

        return;
    }

    list.innerHTML = members.map(member => {
        const role =
            getRoleInfo(member.role);

        const name =
            getMemberName(member);

        const banStatus =
            getBanStatus(member);

        return `
            <div
                class="list-item"
                data-user-id="${escapeHtml(member.id)}"
            >
                <div class="list-item-content">
                    <div class="participant">
                        <div
                            class="participant-role-icon"
                            title="${escapeHtml(role.name)}"
                        >
                            ${role.icon}
                        </div>

                        <div class="participant-info">
                            <div class="participant-name">
                                ${escapeHtml(name)}
                            </div>

                            <div class="participant-meta">
                                <span class="participant-role">
                                    ${escapeHtml(role.name)}
                                </span>

                                ${banStatus}
                            </div>
                        </div>
                    </div>
                </div>

                <div class="actions">
                    <button
                        class="icon-button"
                        type="button"
                        title="Удалить участника"
                        aria-label="Удалить участника ${escapeHtml(name)}"
                        data-delete-user-tg-id="${escapeHtml(member.tg_id)}"
                    >
                        🗑️
                    </button>
                </div>
            </div>
        `;
    }).join("");
}

async function loadMembers() {
    const list =
        document.getElementById("membersList");

    if (list) {
        list.innerHTML = `
            <div class="placeholder">
                Загрузка участников...
            </div>
        `;
    }

    try {
        const response =
            await fetch(
                GET_USERS_URL,
                {
                    method: "GET",
                    headers: {
                        "Accept": "application/json"
                    }
                }
            );

        if (!response.ok) {
            throw new Error(
                `HTTP ${response.status}`
            );
        }

        const data =
            await response.json();

        if (!Array.isArray(data)) {
            throw new Error(
                "API /api/get_users должен вернуть массив пользователей."
            );
        }

        members = data;

        renderMembers();

    } catch (error) {
        console.error(
            "Ошибка загрузки участников:",
            error
        );

        if (list) {
            list.innerHTML = `
                <div class="placeholder error-message">
                    Не удалось загрузить список участников.
                </div>
            `;
        }
    }
}

function openDeleteModal(tgId) {
    deletingUserId = tgId;

    const modal =
        document.getElementById("deleteModal");

    if (!modal) {
        return;
    }

    modal.classList.add("show");

    modal.setAttribute(
        "aria-hidden",
        "false"
    );
}

function closeDeleteModal() {
    deletingUserId = null;

    const modal =
        document.getElementById("deleteModal");

    if (!modal) {
        return;
    }

    modal.classList.remove("show");

    modal.setAttribute(
        "aria-hidden",
        "true"
    );
}

async function confirmDelete() {
    if (
        deletingUserId === null ||
        deletingUserId === undefined
    ) {
        return;
    }

    const tgId =
        deletingUserId;

    const button =
        document.getElementById(
            "confirmDeleteButton"
        );

    if (button) {
        button.disabled = true;
    }

    try {
        const response =
            await fetch(
                `/api/delete_user/${encodeURIComponent(tgId)}`,
                {
                    method: "DELETE",
                    headers: {
                        "Accept": "application/json"
                    }
                }
            );

        if (!response.ok) {
            throw new Error(
                `HTTP ${response.status}`
            );
        }

        members =
            members.filter(
                member => member.tg_id !== tgId
            );

        closeDeleteModal();

        renderMembers();

    } catch (error) {
        console.error(
            "Ошибка удаления участника:",
            error
        );

        alert(
            "Не удалось удалить участника."
        );

    } finally {
        if (button) {
            button.disabled = false;
        }
    }
}

function handleMembersClick(event) {
    const deleteButton =
        event.target.closest(
            "[data-delete-user-tg-id]"
        );

    if (!deleteButton) {
        return;
    }

    const tgId =
        Number(
            deleteButton.dataset.deleteUserTgId
        );

    if (Number.isNaN(tgId)) {
        console.error(
            "Некорректный tg_id:",
            deleteButton.dataset.deleteUserTgId
        );

        return;
    }

    openDeleteModal(tgId);
}

function handleModalOverlayClick(event) {
    if (
        event.target.id === "deleteModal"
    ) {
        closeDeleteModal();
    }
}

function handleEscape(event) {
    if (event.key === "Escape") {
        closeDeleteModal();
    }
}

document.addEventListener(
    "DOMContentLoaded",
    () => {
        const membersList =
            document.getElementById(
                "membersList"
            );

        if (membersList) {
            membersList.addEventListener(
                "click",
                handleMembersClick
            );
        }

        const cancelButton =
            document.getElementById(
                "cancelDeleteButton"
            );

        if (cancelButton) {
            cancelButton.addEventListener(
                "click",
                closeDeleteModal
            );
        }

        const confirmButton =
            document.getElementById(
                "confirmDeleteButton"
            );

        if (confirmButton) {
            confirmButton.addEventListener(
                "click",
                confirmDelete
            );
        }

        const deleteModal =
            document.getElementById(
                "deleteModal"
            );

        if (deleteModal) {
            deleteModal.addEventListener(
                "click",
                handleModalOverlayClick
            );
        }

        document.addEventListener(
            "keydown",
            handleEscape
        );

        loadMembers();
    }
);

