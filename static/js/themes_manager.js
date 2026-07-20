/* ===========================================
            THEME ENGINE
=========================================== */

const THEMES = [

"obsidian",

"titanium",

"aurora",

"nova",

"eclipse"

];

function applyTheme(theme){

if(!THEMES.includes(theme))
theme="obsidian";

document.body.setAttribute(
"data-theme",
theme
);

localStorage.setItem(
"zoro-theme",
theme
);

}

function loadTheme(){

const saved =
localStorage.getItem("zoro-theme");

if(saved){

applyTheme(saved);

}else{

applyTheme("obsidian");

}

}

document.addEventListener(
"DOMContentLoaded",
loadTheme
);