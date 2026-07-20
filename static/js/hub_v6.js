/* ==========================================================
                    ZORO HUB V6
                    CORE SYSTEM
========================================================== */

document.addEventListener("DOMContentLoaded", () => {

    console.log("Zoro Hub V6 Loaded.");

    initMouseGlow();

    initCardTilt();

    initXPBar();

});

/* ==========================================================
                    MOUSE GLOW
========================================================== */

function initMouseGlow(){

    const glow = document.getElementById("mouseGlow");

    if(!glow) return;

    document.addEventListener("mousemove",(e)=>{

        glow.style.left = e.clientX + "px";

        glow.style.top  = e.clientY + "px";

    });

}

/* ==========================================================
                    CARD TILT
========================================================== */

function initCardTilt(){

    const cards = document.querySelectorAll(

        ".launcher-card,.theme-card,.mission-card,.achievement-card,.dashboard-card,.news-card"

    );

    cards.forEach(card=>{

        card.addEventListener("mousemove",(e)=>{

            const rect = card.getBoundingClientRect();

            const x = e.clientX - rect.left;

            const y = e.clientY - rect.top;

            const rotateY = (x - rect.width / 2) / 28;

            const rotateX = -(y - rect.height / 2) / 28;

            card.style.transform =

                `perspective(900px)
                rotateX(${rotateX}deg)
                rotateY(${rotateY}deg)
                translateY(-6px)`;

        });

        card.addEventListener("mouseleave",()=>{

            card.style.transform =

                "perspective(900px) rotateX(0deg) rotateY(0deg) translateY(0px)";

        });

    });

}

/* ==========================================================
                    XP BAR
========================================================== */

function initXPBar(){

    const bar = document.querySelector(".xp-fill");

    if(!bar) return;

    const value = Number(bar.dataset.xp || 0);

    setTimeout(()=>{

        bar.style.width = value + "%";

    },300);

}

/* ==========================================================
                    LAUNCHER ENGINE
========================================================== */

const Launcher = {

    games:{

        minecraft:{
            installed:false,
            path:"",
            display:"Minecraft"
        },

        roblox:{
            installed:false,
            path:"",
            display:"Roblox"
        },

        guess:{
            installed:true,
            path:"/guess",
            display:"Guess The Number"
        }

    }

};

/* ==========================================================
                    GAME LAUNCH
========================================================== */

function launchGame(gameId){

    switch(gameId){

        case "minecraft":

            window.open("https://www.minecraft.net/en-us/download","_blank");
            break;

        case "roblox":

            window.open("https://www.roblox.com/download","_blank");
            break;

        case "guess":

            window.location.href="/guess";
            break;

        default:

            alert("Unknown game.");

    }

}

/* ==========================================================
                INSTALL POPUP
========================================================== */

let currentInstallGame = "";

function showInstallPopup(gameId){

    currentInstallGame = gameId;

    const game = Launcher.games[gameId];

    document.getElementById("installTitle").innerText =
        game.display;

    document.getElementById("installModal")
        .classList.add("show");

}

function closeInstallModal(){

    document.getElementById("installModal")
        .classList.remove("show");

}

window.addEventListener("DOMContentLoaded",()=>{

    const btn = document.getElementById("installConfirm");

    if(btn){

        btn.addEventListener("click",()=>{

            console.log("Installing:", currentInstallGame);

            installGame(currentInstallGame);

            closeInstallModal();

        });

    }

});

/* ==========================================================
                LOCATE GAME
========================================================== */

function locateGame(gameId){

    console.log("Locate",gameId);

    alert(

        "Later this will open a file picker to locate "

        + Launcher.games[gameId].display

    );

}

/* ==========================================================
                GAME DATABASE
========================================================== */

const STORAGE_KEY = "zoroHubGames";

/* ==========================================================
                LOAD SAVED GAMES
========================================================== */

function loadGames(){

    const saved = localStorage.getItem(STORAGE_KEY);

    if(!saved) return;

    try{

        const data = JSON.parse(saved);

        Object.keys(data).forEach(id=>{

            if(Launcher.games[id]){

                Launcher.games[id].installed = data[id].installed;
                Launcher.games[id].path = data[id].path;

            }

        });

    }

    catch(err){

        console.error("Failed to load launcher data.");

    }

}

/* ==========================================================
                SAVE GAMES
========================================================== */

function saveGames(){

    localStorage.setItem(

        STORAGE_KEY,

        JSON.stringify(Launcher.games)

    );

}

/* ==========================================================
                FAKE INSTALL
========================================================== */

function installGame(gameId){

    const game = Launcher.games[gameId];

    game.installed = true;

    game.path = "installed://" + gameId;

    saveGames();

    refreshLauncherButtons();

}

/* ==========================================================
                REFRESH BUTTONS
========================================================== */

function refreshLauncherButtons(){

    document.querySelectorAll("[data-game]").forEach(btn=>{

        const id = btn.dataset.game;

        const game = Launcher.games[id];

        if(!game) return;

        if(game.installed){

            btn.textContent = "Launch";

            btn.classList.add("installed");

        }

        else{

            btn.textContent = "Install";

            btn.classList.remove("installed");

        }

    });

}

/* ==========================================================
                STARTUP
========================================================== */

document.addEventListener("DOMContentLoaded",()=>{

    loadGames();

    refreshLauncherButtons();

});

/* ==========================================================
                XP SYSTEM
========================================================== */

const PLAYER_KEY = "zoroHubPlayer";

let Player = {

    level:1,

    xp:0,

    xpNeeded:100

};

/* -----------------------
        LOAD
------------------------ */

function loadPlayer(){

    const save = localStorage.getItem(PLAYER_KEY);

    if(save){

        Player = JSON.parse(save);

    }

}

/* -----------------------
        SAVE
------------------------ */

function savePlayer(){

    localStorage.setItem(

        PLAYER_KEY,

        JSON.stringify(Player)

    );

}

/* -----------------------
        ADD XP
------------------------ */

function addXP(amount){

    Player.xp += amount;

    while(Player.xp >= Player.xpNeeded){

        Player.xp -= Player.xpNeeded;

        Player.level++;

        Player.xpNeeded += 50;

        levelUp();

    }

    savePlayer();

    updateXP();

}

/* -----------------------
        UPDATE UI
------------------------ */

function updateXP(){

    const levelText =
    document.getElementById("playerLevel");

    const xpBar =
    document.querySelector(".xp-fill");

    const xpText =
    document.getElementById("xpText");

    if(levelText){

        levelText.innerText =
        "Level " + Player.level;

    }

    if(xpBar){

        xpBar.style.width =

        (Player.xp / Player.xpNeeded) * 100 + "%";

    }

    if(xpText){

        xpText.innerText =

        Player.xp +

        " / " +

        Player.xpNeeded +

        " XP";

    }

}

/* -----------------------
        LEVEL UP
------------------------ */

function levelUp(){

    alert(

        "🎉 LEVEL UP!\n\nYou reached Level "

        + Player.level

    );

}

/* -----------------------
        START
------------------------ */

window.addEventListener("DOMContentLoaded",()=>{

    loadPlayer();

    updateXP();

});

/* ==========================================
        MYTHIC UNLOCK
========================================== */

const equipGalaxyBtn = document.getElementById("equipGalaxyBtn");

if (equipGalaxyBtn) {

    equipGalaxyBtn.addEventListener("click", async () => {

        const res = await fetch("/equip_border", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                border: "galaxy"

            })

        });

        const data = await res.json();

        if (data.success) {

            const frame = document.getElementById("avatarFrame");

            if (frame) {

                frame.className =
                    "avatar-frame border-galaxy";

            }

            document.getElementById("unlockPopup").remove();

        }

    });

}