/* ==========================================================
                    ZORO HUB THEME ENGINE
========================================================== */

/* -------------------------
        Global State
-------------------------- */

let selectedTheme = null;
let selectedThemeName = "";
let selectedThemePrice = 0;

/* -------------------------
        Popup
-------------------------- */

function openThemePurchase(theme, name, price){

    selectedTheme = theme;
    selectedThemeName = name;
    selectedThemePrice = price;

    document.getElementById("themeName").textContent = name;
    document.getElementById("themePrice").textContent = price + " Coins";

    document
        .getElementById("themePurchaseModal")
        .classList.add("show");

}

function closeThemePurchase(){

    document
        .getElementById("themePurchaseModal")
        .classList.remove("show");

}

/* -------------------------
        Apply Theme
-------------------------- */

function applyTheme(theme){

    document.body.dataset.theme = theme;

}

/* -------------------------
        Equip Theme
-------------------------- */

async function equipTheme(theme){

    try{

        const response = await fetch("/api/equip_theme",{

            method:"POST",

            headers:{
                "Content-Type":"application/json"
            },

            body:JSON.stringify({

                theme:theme

            })

        });

        const data = await response.json();

        if(data.success){

            applyTheme(theme);

        }

        else{

            alert(data.message || "Couldn't equip theme.");

        }

    }

    catch(err){

        console.error(err);

        alert("Equip failed.");

    }

}

/* -------------------------
        Startup
-------------------------- */

window.onload = function(){

    const currentTheme = document.body.dataset.theme;

    if(currentTheme){

        applyTheme(currentTheme);

    }

};