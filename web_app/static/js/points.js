/* ========================================
   API ENDPOINTS
======================================== */

const API = {
    getPoints: "/api/get_points",        // GET: точки + адреса + города разом
    addPoint: "/api/add_point",          // POST: создать точку
    updatePoint: "/api/update_point",    // POST: обновить точку

    addCity: "/api/add_city",            // POST: создать город
    updateCity: "/api/update_city",      // POST: обновить город

    addAdress: "/api/add_adress",        // POST: создать адрес
    updateAdress: "/api/update_adress",  // POST: обновить адрес

    deleteCity: "/api/delete_city",       // DELETE: удалить город
    deleteAdress: "/api/delete_adress",   // DELETE: удалить адрес
    deletePoint: "/api/delete_point"      // DELETE: удалить точку
}

/* ========================================
   STATE
======================================== */

// points: { id, point, id_device, adress_id }
let points = [];

// cities: { id, city }
let cities = [];

// allAddresses: ВСЕ адреса, { id, adress, city_id }
let allAddresses = [];

// addresses: адреса ТОЛЬКО выбранного города (отфильтрованы из allAddresses)
let addresses = [];

let expandedCities = {};
let expandedAddresses = {};

let editingPointId = null;
let deletingId = null;
let deletingType = null;

let isCreatingCity = false;
let isCreatingAddress = false;
let isSavingPoint = false;
let isSavingCity = false;
let isSavingAddress = false;


/* ========================================
   INIT
======================================== */

document.addEventListener("DOMContentLoaded", () => {
    const citySelect = document.getElementById("citySelect");
    if (citySelect) {
        citySelect.addEventListener("change", function () {
            cancelNewAddress();

            if (!this.value) {
                document.getElementById("addressSelect").innerHTML =
                    `<option value="">Выберите адрес</option>`;
                updateAddressAddButtonState();
                return;
            }

            fillAddressSelect(this.value);
            updateAddressAddButtonState();
        });
    }

    loadPoints();
});


/* ========================================
   DATA LOADING
======================================== */

/**
 * Загружает точки + адреса + города одним запросом.
 * Ответ: { points: [...], adreses: [...], cities: [...] }
 */
async function loadPoints() {
    try {
        const response = await fetch(API.getPoints);
        if (!response.ok) {
            throw new Error("Не удалось загрузить точки");
        }

        const data = await response.json();

        points = data.points || [];
        allAddresses = data.adreses || [];
        cities = data.cities || [];

        renderPointsTree();
    } catch (error) {
        console.error(error);
        const tree = document.getElementById("pointsTree");
        if (tree) {
            tree.innerHTML = `
                <div class="placeholder">
                    Не удалось загрузить точки.
                </div>
            `;
        }
    }
}


/* ========================================
   LOOKUPS
======================================== */

function getAddressById(addressId) {
    return allAddresses.find(a => String(a.id) === String(addressId)) || null;
}


function getCityById(cityId) {
    return cities.find(c => String(c.id) === String(cityId)) || null;
}


/* ========================================
   RENDER TREE
======================================== */

function renderPointsTree() {
    const tree = document.getElementById("pointsTree");
    if (!tree) {
        return;
    }

    // Группировка: город → адрес → точки
    const cityMap = {};

    points.forEach(item => {
        const addressId = item.adress_id;
        const address = getAddressById(addressId) || { id: addressId, adress: "—", city_id: null };
        const cityId = address.city_id;
        const city = getCityById(cityId) || { id: cityId, city: "—" };

        if (!cityMap[cityId]) {
            cityMap[cityId] = {
                city: city,
                addresses: {}
            };
        }

        if (!cityMap[cityId].addresses[addressId]) {
            cityMap[cityId].addresses[addressId] = {
                address: address,
                points: []
            };
        }

        cityMap[cityId].addresses[addressId].points.push(item);
    });

    const cityList = Object.values(cityMap);

    if (cityList.length === 0) {
        tree.innerHTML = `
            <div class="placeholder">
                Точек пока нет.
            </div>
        `;
        return;
    }

    tree.innerHTML = cityList.map(cityGroup => {
        const cityId = cityGroup.city.id;
        const cityExpanded = expandedCities[cityId] !== false;
        const addressList = Object.values(cityGroup.addresses);

        return `
            <div class="tree-node">
                <div class="tree-row city-row">
                    <button
                        class="tree-toggle"
                        type="button"
                        onclick="toggleCity(${cityId})"
                    >
                        ${cityExpanded ? "▼" : "▶"}
                    </button>
                    <div class="tree-icon">📍</div>
                    <div class="tree-content">
                        <div class="tree-title city-title">
                            ${escapeHtml(cityGroup.city.city)}
                        </div>
                    </div>
                    <div class="tree-actions">
                        <button
                            class="tree-action"
                            type="button"
                            title="Редактировать город"
                            onclick="editCity(${cityId})"
                        >
                            ✏️
                        </button>
                        <button
                            class="tree-action"
                            type="button"
                            title="Удалить город"
                            onclick="openDeleteModal(${cityId}, 'city')"
                        >
                            🗑️
                        </button>
                    </div>
                </div>
                ${
                    cityExpanded
                        ? addressList.map(addressGroup =>
                              renderAddress(addressGroup)
                          ).join("")
                        : ""
                }
            </div>
        `;
    }).join("");
}


function renderAddress(addressGroup) {
    const addressId = addressGroup.address.id;
    const addressExpanded = expandedAddresses[addressId] !== false;

    return `
        <div class="address-node">
            <div class="tree-row address-row">
                <button
                    class="tree-toggle"
                    type="button"
                    onclick="toggleAddress(${addressId})"
                >
                    ${addressExpanded ? "▼" : "▶"}
                </button>
                <div class="tree-icon">🏢</div>
                <div class="tree-content">
                    <div class="tree-title address-title">
                        ${escapeHtml(addressGroup.address.adress)}
                    </div>
                </div>
                <div class="tree-actions">
                    <button
                        class="tree-action"
                        type="button"
                        title="Редактировать адрес"
                        onclick="editAddress(${addressId})"
                    >
                        ✏️
                    </button>
                    <button
                        class="tree-action"
                        type="button"
                        title="Удалить адрес"
                        onclick="openDeleteModal(${addressId}, 'address')"
                    >
                        🗑️
                    </button>
                </div>
            </div>
            ${
                addressExpanded
                    ? addressGroup.points
                          .map(point => renderPointNode(point))
                          .join("")
                    : ""
            }
        </div>
    `;
}


/**
 * Одно звено: название точки + ID аппарата
 */
function renderPointNode(item) {
    return `
        <div class="point-node">
            <div class="tree-row point-row">
                <div class="tree-toggle empty"></div>
                <div class="tree-icon">☕</div>
                <div class="tree-content">
                    <div class="tree-title point-title">
                        ${escapeHtml(item.point)}
                    </div>
                    <div class="point-machine">
                        Аппарат
                        <span class="point-machine-id">
                            №${escapeHtml(item.id_device)}
                        </span>
                    </div>
                </div>
                <div class="tree-actions">
                    <button
                        class="tree-action"
                        type="button"
                        title="Редактировать"
                        onclick="editPoint(${item.id})"
                    >
                        ✏️
                    </button>
                    <button
                        class="tree-action"
                        type="button"
                        title="Удалить"
                        onclick="openDeleteModal(${item.id}, 'point')"
                    >
                        🗑️
                    </button>
                </div>
            </div>
        </div>
    `;
}


/* ========================================
   TREE TOGGLES
======================================== */

function toggleCity(id) {
    expandedCities[id] = expandedCities[id] === false;
    renderPointsTree();
}


function toggleAddress(id) {
    expandedAddresses[id] = expandedAddresses[id] === false;
    renderPointsTree();
}


/* ========================================
   CREATE / EDIT POINT
======================================== */

function openCreatePoint() {
    editingPointId = null;

    document.getElementById("pointModalTitle").textContent = "Добавить точку";
    document.getElementById("citySelect").value = "";
    document.getElementById("addressSelect").innerHTML =
        `<option value="">Выберите адрес</option>`;
    document.getElementById("pointName").value = "";
    document.getElementById("machineId").value = "";

    cancelNewCity();
    cancelNewAddress();

    fillCitySelect();
    updateAddressAddButtonState();

    document.getElementById("pointModal").classList.add("show");
}


function editPoint(id) {
    const item = points.find(p => String(p.id) === String(id));
    if (!item) {
        return;
    }

    editingPointId = id;

    const address = getAddressById(item.adress_id);
    const cityId = address ? address.city_id : "";

    document.getElementById("pointModalTitle").textContent = "Редактировать точку";

    cancelNewCity();
    cancelNewAddress();

    fillCitySelect();
    document.getElementById("citySelect").value = cityId;

    fillAddressSelect(cityId);
    document.getElementById("addressSelect").value = item.adress_id;

    document.getElementById("pointName").value = item.point;
    document.getElementById("machineId").value = item.id_device;

    updateAddressAddButtonState();

    document.getElementById("pointModal").classList.add("show");
}


function fillCitySelect() {
    const select = document.getElementById("citySelect");

    select.innerHTML = `
        <option value="">Выберите город</option>
        ${cities
            .map(
                c => `<option value="${c.id}">${escapeHtml(c.city)}</option>`
            )
            .join("")}
    `;
}


/**
 * Фильтрует адреса конкретного города из уже загруженного allAddresses.
 */
function fillAddressSelect(cityId) {
    const select = document.getElementById("addressSelect");

    addresses = allAddresses.filter(
        a => String(a.city_id) === String(cityId)
    );

    select.innerHTML = `
        <option value="">Выберите адрес</option>
        ${addresses
            .map(
                a => `<option value="${a.id}">${escapeHtml(a.adress)}</option>`
            )
            .join("")}
    `;
}


function closePointForm() {
    document.getElementById("pointModal").classList.remove("show");
    editingPointId = null;
    cancelNewCity();
    cancelNewAddress();
}


/**
 * Создание точки: POST /api/add_point
 * Редактирование точки: POST /api/update_point
 */
async function savePoint() {
    if (isSavingPoint) {
        return;
    }

    const cityId = document.getElementById("citySelect").value;
    const addressId = document.getElementById("addressSelect").value;
    const pointName = document.getElementById("pointName").value.trim();
    const deviceId = document.getElementById("machineId").value.trim();

    if (!cityId || !addressId || !pointName || !deviceId) {
        alert("Заполните все поля.");
        return;
    }

    isSavingPoint = true;

    try {
        let response;
        let savedPoint;

        if (editingPointId === null) {
            const payload = {
                city_id: Number(cityId),
                adress_id: Number(addressId),
                point: pointName,
                id_device: deviceId
            };

            response = await fetch(API.addPoint, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error("Ошибка создания точки");
            }

            savedPoint = await response.json();
            points.push(savedPoint);
        } else {
            const payload = {
                id: Number(editingPointId),
                point: pointName,
                id_device: deviceId,
                adress_id: Number(addressId),
                city_id: Number(cityId)
            };

            response = await fetch(API.updatePoint, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error("Ошибка обновления точки");
            }

            savedPoint = await response.json();

            const index = points.findIndex(
                p => String(p.id) === String(editingPointId)
            );
            if (index !== -1) {
                points[index] = savedPoint;
            }
        }

        closePointForm();
        renderPointsTree();
    } catch (error) {
        console.error(error);
        alert("Произошла ошибка при сохранении точки. Попробуйте ещё раз.");
    } finally {
        isSavingPoint = false;
    }
}


/* ========================================
   EDIT CITY
======================================== */

function editCity(cityId) {
    const city = getCityById(cityId);
    if (!city) {
        return;
    }

    document.getElementById("editCityId").value = city.id;
    document.getElementById("editCityName").value = city.city;

    document.getElementById("editCityModal").classList.add("show");
}


function closeEditCityModal() {
    document.getElementById("editCityModal").classList.remove("show");
}


/**
 * POST /api/update_city, тело: { id, city }
 * Ответ: обновлённый объект города
 */
async function saveCityEdit() {
    if (isSavingCity) {
        return;
    }

    const id = document.getElementById("editCityId").value;
    const name = document.getElementById("editCityName").value.trim();

    if (!name) {
        alert("Введите название города.");
        return;
    }

    isSavingCity = true;

    try {
        const response = await fetch(API.updateCity, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ id: Number(id), city: name })
        });

        if (!response.ok) {
            throw new Error("Ошибка обновления города");
        }

        const updatedCity = await response.json();

        const index = cities.findIndex(c => String(c.id) === String(updatedCity.id));
        if (index !== -1) {
            cities[index] = updatedCity;
        }

        closeEditCityModal();
        renderPointsTree();
    } catch (error) {
        console.error(error);
        alert("Произошла ошибка при обновлении города. Попробуйте ещё раз.");
    } finally {
        isSavingCity = false;
    }
}

/* ========================================
   EDIT ADDRESS
======================================== */

function editAddress(addressId) {
    const address = getAddressById(addressId);
    if (!address) {
        return;
    }

    document.getElementById("editAddressId").value = address.id;
    document.getElementById("editAddressCityId").value = address.city_id;
    document.getElementById("editAddressName").value = address.adress;

    document.getElementById("editAddressModal").classList.add("show");
}


function closeEditAddressModal() {
    document.getElementById("editAddressModal").classList.remove("show");
}


/**
 * POST /api/update_adress, тело: { id, adress, city_id }
 * Ответ: обновлённый объект адреса
 */
async function saveAddressEdit() {
    if (isSavingAddress) {
        return;
    }

    const id = document.getElementById("editAddressId").value;
    const cityId = document.getElementById("editAddressCityId").value;
    const name = document.getElementById("editAddressName").value.trim();

    if (!name) {
        alert("Введите название адреса.");
        return;
    }

    isSavingAddress = true;

    try {
        const response = await fetch(API.updateAdress, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                id: Number(id),
                adress: name,
                city_id: Number(cityId)
            })
        });

        if (!response.ok) {
            throw new Error("Ошибка обновления адреса");
        }

        const updatedAddress = await response.json();

        const index = allAddresses.findIndex(
            a => String(a.id) === String(updatedAddress.id)
        );
        if (index !== -1) {
            allAddresses[index] = updatedAddress;
        }

        closeEditAddressModal();
        renderPointsTree();
    } catch (error) {
        console.error(error);
        alert("Произошла ошибка при обновлении адреса. Попробуйте ещё раз.");
    } finally {
        isSavingAddress = false;
    }
}


/* ========================================
   INLINE CREATE: CITY
======================================== */

function showNewCityInput() {
    document.getElementById("citySelectRow").style.display = "none";
    document.getElementById("cityCreateRow").style.display = "flex";

    const input = document.getElementById("newCityInput");
    input.value = "";
    input.focus();
}


function cancelNewCity() {
    const createRow = document.getElementById("cityCreateRow");
    const selectRow = document.getElementById("citySelectRow");

    if (createRow) {
        createRow.style.display = "none";
    }
    if (selectRow) {
        selectRow.style.display = "flex";
    }

    const input = document.getElementById("newCityInput");
    if (input) {
        input.value = "";
    }
}


/**
 * POST /api/add_city, тело: { city }
 * Ответ: { id, city }
 */
async function createCity() {
    if (isCreatingCity) {
        return;
    }

    const input = document.getElementById("newCityInput");
    const name = input.value.trim();

    if (!name) {
        alert("Введите название города.");
        return;
    }

    isCreatingCity = true;

    try {
        const response = await fetch(API.addCity, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ city: name })
        });

        if (!response.ok) {
            throw new Error("Ошибка создания города");
        }

        const newCity = await response.json();

        cities.push(newCity);

        fillCitySelect();
        document.getElementById("citySelect").value = newCity.id;

        addresses = [];
        document.getElementById("addressSelect").innerHTML =
            `<option value="">Выберите адрес</option>`;

        cancelNewCity();
        updateAddressAddButtonState();
    } catch (error) {
        console.error(error);
        alert("Не удалось создать город.");
    } finally {
        isCreatingCity = false;
    }
}


/* ========================================
   INLINE CREATE: ADDRESS
======================================== */

function updateAddressAddButtonState() {
    const addBtn = document.getElementById("addressAddBtn");
    if (!addBtn) {
        return;
    }

    const cityId = document.getElementById("citySelect").value;
    addBtn.disabled = !cityId;
}


function showNewAddressInput() {
    const cityId = document.getElementById("citySelect").value;

    if (!cityId) {
        alert("Сначала выберите город.");
        return;
    }

    document.getElementById("addressSelectRow").style.display = "none";
    document.getElementById("addressCreateRow").style.display = "flex";

    const input = document.getElementById("newAddressInput");
    input.value = "";
    input.focus();
}


function cancelNewAddress() {
    const createRow = document.getElementById("addressCreateRow");
    const selectRow = document.getElementById("addressSelectRow");

    if (createRow) {
        createRow.style.display = "none";
    }
    if (selectRow) {
        selectRow.style.display = "flex";
    }

    const input = document.getElementById("newAddressInput");
    if (input) {
        input.value = "";
    }
}


/**
 * POST /api/add_adress, тело: { adress, city_id }
 * Ответ: { id, adress, city_id }
 */
async function createAddress() {
    if (isCreatingAddress) {
        return;
    }

    const cityId = document.getElementById("citySelect").value;
    if (!cityId) {
        alert("Сначала выберите город.");
        return;
    }

    const input = document.getElementById("newAddressInput");
    const name = input.value.trim();

    if (!name) {
        alert("Введите название адреса.");
        return;
    }

    isCreatingAddress = true;

    try {
        const response = await fetch(API.addAdress, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                adress: name,
                city_id: Number(cityId)
            })
        });

        if (!response.ok) {
            throw new Error("Ошибка создания адреса");
        }

        const newAddress = await response.json();

        allAddresses.push(newAddress);

        fillAddressSelect(cityId);
        document.getElementById("addressSelect").value = newAddress.id;

        cancelNewAddress();
    } catch (error) {
        console.error(error);
        alert("Не удалось создать адрес.");
    } finally {
        isCreatingAddress = false;
    }
}


/* ========================================
   DELETE CITY / ADDRESS / POINT
======================================== */

function openDeleteModal(id, type) {
    deletingId = id;
    deletingType = type;

    document.getElementById("deleteModal").classList.add("show");
}


function closeDeleteModal() {
    document.getElementById("deleteModal").classList.remove("show");

    deletingId = null;
    deletingType = null;
}


async function confirmDelete() {
    if (deletingId === null || deletingType === null) {
        return;
    }

    const id = deletingId;
    const type = deletingType;

    const endpoints = {
        city: API.deleteCity,
        address: API.deleteAdress,
        point: API.deletePoint
    };

    const endpoint = endpoints[type];

    if (!endpoint) {
        closeDeleteModal();
        return;
    }

    try {
        const response = await fetch(
            `${endpoint}/${encodeURIComponent(id)}`,
            {
                method: "DELETE"
            }
        );

        if (!response.ok) {
            throw new Error(
                `Ошибка удаления объекта: ${response.status}`
            );
        }

        /*
         * Сервер успешно удалил объект.
         * Теперь обновляем локальное состояние JavaScript.
         */

        if (type === "city") {
            /*
             * Сначала получаем ID всех адресов этого города.
             * Они понадобятся, чтобы удалить связанные точки.
             */
            const addressIds = allAddresses
                .filter(
                    address =>
                        String(address.city_id) === String(id)
                )
                .map(address => String(address.id));

            // Удаляем город.
            cities = cities.filter(
                city => String(city.id) !== String(id)
            );

            // Удаляем все адреса этого города.
            allAddresses = allAddresses.filter(
                address =>
                    String(address.city_id) !== String(id)
            );

            // Удаляем все точки адресов этого города.
            points = points.filter(
                point =>
                    !addressIds.includes(
                        String(point.adress_id)
                    )
            );

            // Очищаем состояние раскрытия.
            delete expandedCities[id];

            addressIds.forEach(addressId => {
                delete expandedAddresses[addressId];
            });

        } else if (type === "address") {
            /*
             * Удаляем адрес.
             */
            allAddresses = allAddresses.filter(
                address =>
                    String(address.id) !== String(id)
            );

            /*
             * Удаляем все точки этого адреса.
             */
            points = points.filter(
                point =>
                    String(point.adress_id) !== String(id)
            );

            // Очищаем состояние раскрытия.
            delete expandedAddresses[id];

        } else if (type === "point") {
            /*
             * Удаляем только точку.
             */
            points = points.filter(
                point =>
                    String(point.id) !== String(id)
            );
        }

        /*
         * Закрываем окно подтверждения
         * и перерисовываем дерево.
         */
        closeDeleteModal();
        renderPointsTree();

    } catch (error) {
        console.error(error);

        alert(
            "Не удалось удалить объект. Попробуйте ещё раз."
        );
    }
}

/* ========================================
   MODAL OVERLAY
======================================== */

function closeModalOnOverlay(event, modalId) {
    if (event.target.id !== modalId) {
        return;
    }

    document.getElementById(modalId).classList.remove("show");

    if (modalId === "pointModal") {
        editingPointId = null;
        cancelNewCity();
        cancelNewAddress();
    }

    if (modalId === "deleteModal") {
        deletingId = null;
        deletingType = null;
    }
}


/* ========================================
   HELPERS
======================================== */

function escapeHtml(value) {
    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}