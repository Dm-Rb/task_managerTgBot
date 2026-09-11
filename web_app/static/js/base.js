
document.addEventListener("DOMContentLoaded", () => {

    const telegramButton =
        document.getElementById("telegramMenuButton");

    const telegramSubmenu =
        document.getElementById("telegramSubmenu");


    const telephonyButton =
        document.getElementById("telephonyMenuButton");

    const telephonySubmenu =
        document.getElementById("telephonySubmenu");


    const smsButton =
        document.getElementById("smsMenuButton");

    const smsSubmenu =
        document.getElementById("smsSubmenu");


    /*
     * Раскрытие Telegram
     */

    telegramButton?.addEventListener(
        "click",
        () => {

            telegramSubmenu.classList.toggle("hidden");

            telegramButton.classList.toggle(
                "collapsed"
            );

        }
    );


    /*
     * Раскрытие телефонии
     */

    telephonyButton?.addEventListener(
        "click",
        () => {

            telephonySubmenu.classList.toggle(
                "hidden"
            );

            telephonyButton.classList.toggle(
                "collapsed"
            );

        }
    );


    /*
     * Раскрытие SMS
     */

    smsButton?.addEventListener(
        "click",
        () => {

            smsSubmenu.classList.toggle(
                "hidden"
            );

            smsButton.classList.toggle(
                "collapsed"
            );

        }
    );


    /*
     * Навигация
     */

    document
        .querySelectorAll("[data-section]")
        .forEach(button => {

            button.addEventListener(
                "click",
                () => {

                    const section =
                        button.dataset.section;

                    navigateToSection(section);

                }
            );

        });


    /*
     * Устанавливаем активный пункт
     * в зависимости от текущего URL.
     */

    setActiveMenuItem();

});


function navigateToSection(section) {

    const routes = {

        "tasks":
            "/panel/task_tittles",

        "members":
            "/panel/users",

        "points":
            "/panel/points",

        "telephony-details":
            "/telephony/details",

        "telephony-settings":
            "/telephony/settings",

        "sms-details":
            "/sms/details",

        "sms-settings":
            "/sms/settings"

    };


    const url = routes[section];


    if (!url) {
        return;
    }


    window.location.href = url;
}


function setActiveMenuItem() {

    const path =
        window.location.pathname;


    const routes = {

        "/panel/task_tittles":
            "tasks",

        "/panel/users":
            "members",

        "/panel/points":
            "points",

        "/telephony/details":
            "telephony-details",

        "/telephony/settings":
            "telephony-settings",

        "/sms/details":
            "sms-details",

        "/sms/settings":
            "sms-settings"

    };


    const currentSection =
        routes[path];


    if (!currentSection) {
        return;
    }


    const currentButton =
        document.querySelector(
            `[data-section="${currentSection}"]`
        );


    if (!currentButton) {
        return;
    }


    currentButton.classList.add("active");


    /*
     * Открываем соответствующее
     * родительское меню.
     */

    if (
        currentSection === "tasks" ||
        currentSection === "members" ||
        currentSection === "points"
    ) {

        openMenu(
            "telegramMenuButton",
            "telegramSubmenu"
        );

    }


    if (
        currentSection === "telephony-details" ||
        currentSection === "telephony-settings"
    ) {

        openMenu(
            "telephonyMenuButton",
            "telephonySubmenu"
        );

    }


    if (
        currentSection === "sms-details" ||
        currentSection === "sms-settings"
    ) {

        openMenu(
            "smsMenuButton",
            "smsSubmenu"
        );

    }

}


function openMenu(
    buttonId,
    submenuId
) {

    const button =
        document.getElementById(buttonId);

    const submenu =
        document.getElementById(submenuId);


    if (!button || !submenu) {
        return;
    }


    submenu.classList.remove("hidden");

    button.classList.remove("collapsed");

    button.classList.add("active");
}

