/* ==========================================================
                ZORO HUB THEME MANAGER
                 CLEAN / MODERN SYSTEM
========================================================== */

"use strict";


/* ==========================================================
                    THEME DEFINITIONS
========================================================== */

const ZORO_THEMES = {

    common: {
        id: "common",
        className: "theme-common",
        name: "Common",
        rarity: "COMMON"
    },

    uncommon: {
        id: "uncommon",
        className: "theme-uncommon",
        name: "Uncommon",
        rarity: "UNCOMMON"
    },

    rare: {
        id: "rare",
        className: "theme-rare",
        name: "Rare",
        rarity: "RARE"
    },

    epic: {
        id: "epic",
        className: "theme-epic",
        name: "Epic",
        rarity: "EPIC"
    },

    legendary: {
        id: "legendary",
        className: "theme-legendary",
        name: "Legendary",
        rarity: "LEGENDARY"
    },

    mythic: {
        id: "mythic",
        className: "theme-mythic",
        name: "Mythic",
        rarity: "MYTHIC"
    }

};


/* ==========================================================
                    CONSTANTS
========================================================== */

const THEME_STORAGE_KEY =
    "zoroHubTheme";


const THEME_CLASSES =
    Object.values(ZORO_THEMES)
        .map(theme => theme.className);


/* ==========================================================
                    NORMALIZE THEME
========================================================== */

function normalizeTheme(value) {

    if (!value) {

        return "common";

    }


    let normalized =
        String(value)
            .trim()
            .toLowerCase();


    /*
        Accept:

        common
        theme-common
        COMMON
        Theme-Common
    */

    normalized =
        normalized.replace(
            /^theme-/,
            ""
        );


    if (
        Object.prototype.hasOwnProperty.call(
            ZORO_THEMES,
            normalized
        )
    ) {

        return normalized;

    }


    return "common";

}


/* ==========================================================
                    GET THEME
========================================================== */

function getCurrentTheme() {

    const body =
        document.body;


    if (!body) {

        return "common";

    }


    for (
        const theme
        of Object.values(ZORO_THEMES)
    ) {

        if (
            body.classList.contains(
                theme.className
            )
        ) {

            return theme.id;

        }

    }


    /*
        Fall back to saved browser value.
    */

    try {

        const saved =
            localStorage.getItem(
                THEME_STORAGE_KEY
            );


        if (saved) {

            return normalizeTheme(
                saved
            );

        }

    }

    catch (error) {

        console.warn(
            "Could not read saved Zoro theme."
        );

    }


    return "common";

}


/* ==========================================================
                    REMOVE OLD THEMES
========================================================== */

function clearThemeClasses() {

    if (!document.body) {

        return;

    }


    document.body.classList.remove(
        ...THEME_CLASSES
    );

}


/* ==========================================================
                    APPLY THEME
========================================================== */

function applyTheme(themeValue, options = {}) {

    if (!document.body) {

        return false;

    }


    const themeId =
        normalizeTheme(
            themeValue
        );


    const theme =
        ZORO_THEMES[themeId];


    if (!theme) {

        return false;

    }


    clearThemeClasses();


    document.body.classList.add(
        theme.className
    );


    /*
        data-theme is useful for newer Hub CSS
        and future UI components.
    */

    document.body.dataset.theme =
        themeId;


    /*
        Save locally unless explicitly disabled.
    */

    if (
        options.save !== false
    ) {

        try {

            localStorage.setItem(
                THEME_STORAGE_KEY,
                themeId
            );

        }

        catch (error) {

            console.warn(
                "Could not save Zoro theme."
            );

        }

    }


    /*
        Let the rest of Zoro Hub know that
        the visual theme changed.
    */

    window.dispatchEvent(
        new CustomEvent(
            "zoroThemeChanged",
            {
                detail: {
                    id: theme.id,
                    className: theme.className,
                    name: theme.name,
                    rarity: theme.rarity
                }
            }
        )
    );


    return true;

}


/* ==========================================================
                APPLY SERVER / PAGE THEME
========================================================== */

function initializeTheme() {

    if (!document.body) {

        return;

    }


    /*
        The Hub template already places
        profile_theme on <body>.

        Example:

        <body class="theme-legendary">
    */

    const bodyClasses =
        Array.from(
            document.body.classList
        );


    const serverTheme =
        bodyClasses.find(
            className =>
                THEME_CLASSES.includes(
                    className
                )
        );


    if (serverTheme) {

        /*
            Server value wins over local cache.

            This is important because the Shop
            may eventually equip a theme through
            the backend.
        */

        applyTheme(
            serverTheme,
            {
                save: true
            }
        );

        return;

    }


    /*
        No server theme?

        Use previously saved frontend theme.
    */

    try {

        const saved =
            localStorage.getItem(
                THEME_STORAGE_KEY
            );


        if (saved) {

            applyTheme(
                saved,
                {
                    save: false
                }
            );

            return;

        }

    }

    catch (error) {

        console.warn(
            "Could not access saved Zoro theme."
        );

    }


    /*
        Final fallback.
    */

    applyTheme(
        "common",
        {
            save: false
        }
    );

}


/* ==========================================================
                    THEME INFO
========================================================== */

function getThemeInfo(themeValue) {

    const themeId =
        normalizeTheme(
            themeValue
        );


    return (
        ZORO_THEMES[themeId]
        ||
        ZORO_THEMES.common
    );

}


/* ==========================================================
                    THEME CHECK
========================================================== */

function isValidTheme(themeValue) {

    const themeId =
        normalizeTheme(
            themeValue
        );


    return Boolean(
        ZORO_THEMES[themeId]
    );

}


/* ==========================================================
                    RESET THEME
========================================================== */

function resetTheme() {

    return applyTheme(
        "common"
    );

}


/* ==========================================================
                    INITIALIZATION
========================================================== */

document.addEventListener(
    "DOMContentLoaded",
    () => {

        initializeTheme();

        console.log(
            "Zoro Hub theme manager loaded:",
            getCurrentTheme()
        );

    }
);


/* ==========================================================
                    PUBLIC API
========================================================== */

window.ZoroThemes = {

    themes: ZORO_THEMES,

    apply: applyTheme,

    getCurrent: getCurrentTheme,

    getInfo: getThemeInfo,

    isValid: isValidTheme,

    reset: resetTheme,

    clear: clearThemeClasses

};