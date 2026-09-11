document.addEventListener("DOMContentLoaded", async () => {

    let tasks = [];
    let editingTaskId = null;
    let deletingTaskId = null;

    const taskList =
        document.getElementById("taskList");

    const addTaskButton =
        document.getElementById("addTaskButton");

    const taskModal =
        document.getElementById("taskModal");

    const taskModalTitle =
        document.getElementById("taskModalTitle");

    const taskText =
        document.getElementById("taskText");

    const saveTaskButton =
        document.getElementById("saveTaskButton");

    const cancelTaskButton =
        document.getElementById("cancelTaskButton");

    const deleteModal =
        document.getElementById("deleteModal");

    const confirmDeleteButton =
        document.getElementById("confirmDeleteButton");

    const cancelDeleteButton =
        document.getElementById("cancelDeleteButton");


    async function loadTaskTitles() {

        try {

            const response =
                await fetch("/api/task_tittles");

            if (!response.ok) {

                throw new Error(
                    `Ошибка загрузки заголовков: ${response.status}`
                );
            }

            const data =
                await response.json();

            tasks = data.map(item => ({
                id: Number(item.id),
                text: item.tittle,
                type: item.is_sheduler
                    ? "cyclic"
                    : "once"
            }));

            renderTaskList();

        } catch (error) {

            console.error(
                "Не удалось загрузить заголовки задач:",
                error
            );

            taskList.innerHTML = `
                <div class="placeholder">
                    Не удалось загрузить заголовки задач.
                </div>
            `;
        }
    }


    function renderTaskList() {

        if (!taskList) {
            return;
        }

        if (tasks.length === 0) {

            taskList.innerHTML = `
                <div class="placeholder">
                    Заголовков задач пока нет.
                </div>
            `;

            return;
        }

        taskList.innerHTML = tasks
            .map(task => {

                const type =
                    task.type === "cyclic"
                        ? "Циклическая"
                        : "Разовая";

                return `
                    <div
                        class="list-item"
                        data-task-id="${task.id}"
                    >

                        <div class="list-item-content">

                            <div class="list-item-title">
                                ${escapeHtml(task.text)}
                            </div>

                            <div class="list-item-subtitle">
                                ${type}
                            </div>

                        </div>

                        <div class="actions">

                            <button
                                class="icon-button"
                                type="button"
                                data-action="edit"
                                data-id="${task.id}"
                                title="Редактировать"
                            >
                                ✏️
                            </button>

                            <button
                                class="icon-button"
                                type="button"
                                data-action="delete"
                                data-id="${task.id}"
                                title="Удалить"
                            >
                                🗑️
                            </button>

                        </div>

                    </div>
                `;
            })
            .join("");
    }


    function openCreateTask() {

        editingTaskId = null;

        taskModalTitle.textContent =
            "Создать заголовок задачи";

        taskText.value = "";

        setTaskType("once");

        openModal(taskModal);
    }


    function editTask(id) {

        const task =
            tasks.find(item => item.id === id);

        if (!task) {
            return;
        }

        editingTaskId = id;

        taskModalTitle.textContent =
            "Редактировать заголовок задачи";

        taskText.value = task.text;

        setTaskType(task.type);

        openModal(taskModal);
    }


    async function saveTask() {

        const text =
            taskText.value.trim();

        const selectedType =
            document.querySelector(
                'input[name="taskType"]:checked'
            );

        if (!text) {

            alert("Введите текст задачи.");

            taskText.focus();

            return;
        }

        if (!selectedType) {

            alert("Выберите тип задачи.");

            return;
        }

        const type =
            selectedType.value;


        /*
         * ========================================
         * СОЗДАНИЕ НОВОЙ ЗАДАЧИ
         * ========================================
         */

        if (editingTaskId === null) {

            saveTaskButton.disabled = true;

            try {

                const response =
                    await fetch(
                        "/api/create_tittle",
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body: JSON.stringify({
                                tittle: text,

                                is_sheduler:
                                    type === "cyclic"
                            })
                        }
                    );


                if (!response.ok) {

                    throw new Error(
                        `Ошибка создания заголовка: ${response.status}`
                    );
                }


                const data =
                    await response.json();


                if (
                    data.id === undefined ||
                    data.id === null
                ) {

                    throw new Error(
                        "Сервер не вернул id созданной записи"
                    );
                }


                tasks.push({
                    id: Number(data.id),
                    text: text,
                    type: type
                });


                renderTaskList();

                closeTaskForm();

            } catch (error) {

                console.error(
                    "Ошибка создания заголовка:",
                    error
                );

                alert(
                    "Не удалось создать заголовок задачи."
                );

            } finally {

                saveTaskButton.disabled = false;
            }

            return;
        }


        /*
         * ========================================
         * РЕДАКТИРОВАНИЕ СУЩЕСТВУЮЩЕЙ ЗАДАЧИ
         * ========================================
         */

        const task =
            tasks.find(
                item => item.id === editingTaskId
            );

        if (!task) {

            closeTaskForm();

            return;
        }


        const textChanged =
            text !== task.text;

        const typeChanged =
            type !== task.type;


        /*
         * Если ничего не изменилось —
         * запрос не отправляем.
         */

        if (!textChanged && !typeChanged) {

            closeTaskForm();

            return;
        }


        /*
         * Если данные изменились —
         * отправляем POST на сервер.
         */

        saveTaskButton.disabled = true;

        try {

            const response =
                await fetch(
                    "/api/update_task_tittle",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body: JSON.stringify({
                            id: Number(task.id),

                            tittle: text,

                            is_sheduler:
                                type === "cyclic"
                        })
                    }
                );


            if (!response.ok) {

                throw new Error(
                    `Ошибка обновления заголовка: ${response.status}`
                );
            }


            task.text = text;
            task.type = type;

            renderTaskList();

            closeTaskForm();

        } catch (error) {

            console.error(
                "Ошибка обновления заголовка:",
                error
            );

            alert(
                "Не удалось обновить заголовок задачи."
            );

        } finally {

            saveTaskButton.disabled = false;
        }
    }


    /*
     * ========================================
     * УДАЛЕНИЕ
     * ========================================
     */

    function openDeleteModal(id) {

        deletingTaskId = id;

        openModal(deleteModal);
    }


    async function confirmDelete() {

        if (deletingTaskId === null) {
            return;
        }

        const taskId =
            Number(deletingTaskId);

        confirmDeleteButton.disabled = true;

        try {

            const response =
                await fetch(
                    `/api/delete_tittle/${taskId}`,
                    {
                        method: "DELETE"
                    }
                );


            if (!response.ok) {

                throw new Error(
                    `Ошибка удаления заголовка: ${response.status}`
                );
            }


            /*
             * Удаляем элемент из локального массива
             * только после успешного ответа сервера.
             */

            tasks =
                tasks.filter(
                    task => task.id !== taskId
                );


            closeDeleteModal();

            renderTaskList();

        } catch (error) {

            console.error(
                "Ошибка удаления заголовка:",
                error
            );

            alert(
                "Не удалось удалить заголовок задачи."
            );

        } finally {

            confirmDeleteButton.disabled = false;
        }
    }


    function openModal(modal) {

        if (!modal) {
            return;
        }

        modal.classList.add("show");

        modal.setAttribute(
            "aria-hidden",
            "false"
        );
    }


    function closeModal(modal) {

        if (!modal) {
            return;
        }

        modal.classList.remove("show");

        modal.setAttribute(
            "aria-hidden",
            "true"
        );
    }


    function closeTaskForm() {

        closeModal(taskModal);

        editingTaskId = null;
    }


    function closeDeleteModal() {

        closeModal(deleteModal);

        deletingTaskId = null;
    }


    function setTaskType(type) {

        const radio =
            document.querySelector(
                `input[name="taskType"][value="${type}"]`
            );

        if (radio) {
            radio.checked = true;
        }
    }


    addTaskButton.addEventListener(
        "click",
        openCreateTask
    );


    saveTaskButton.addEventListener(
        "click",
        saveTask
    );


    cancelTaskButton.addEventListener(
        "click",
        closeTaskForm
    );


    cancelDeleteButton.addEventListener(
        "click",
        closeDeleteModal
    );


    confirmDeleteButton.addEventListener(
        "click",
        confirmDelete
    );


    taskList.addEventListener(
        "click",
        event => {

            const button =
                event.target.closest(
                    "[data-action]"
                );

            if (!button) {
                return;
            }

            const action =
                button.dataset.action;

            const id =
                Number(button.dataset.id);

            if (action === "edit") {
                editTask(id);
            }

            if (action === "delete") {
                openDeleteModal(id);
            }
        }
    );


    taskModal.addEventListener(
        "click",
        event => {

            if (event.target === taskModal) {
                closeTaskForm();
            }
        }
    );


    deleteModal.addEventListener(
        "click",
        event => {

            if (event.target === deleteModal) {
                closeDeleteModal();
            }
        }
    );


    document.addEventListener(
        "keydown",
        event => {

            if (event.key !== "Escape") {
                return;
            }

            if (
                taskModal.classList.contains("show")
            ) {
                closeTaskForm();
            }

            if (
                deleteModal.classList.contains("show")
            ) {
                closeDeleteModal();
            }
        }
    );


    function escapeHtml(value) {

        return String(value)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }


    await loadTaskTitles();

});

