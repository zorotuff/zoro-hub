// ==========================================================
// ZORO HUB PERSONALIZE
// ==========================================================

// ---------- Preview ----------

const previewAvatar = document.getElementById("previewAvatar");

const saveBtn = document.getElementById("saveBtn");

// ---------- Inventory ----------

const avatarInventory =
document.getElementById("avatarInventory");

const borderInventory =
document.getElementById("borderInventory");

const bannerInventory =
document.getElementById("bannerInventory");

const themeInventory =
document.getElementById("themeInventory");

// ==========================================================
// CURRENT EQUIPPED
// ==========================================================

const current = {

avatar:null,

border:null,

banner:null,

theme:null

};

// ==========================================================
// BUILT-IN COSMETICS
// ==========================================================

const avatars = [

"avatar1.png",
"avatar2.png",
"avatar3.png",
"avatar4.png",
"avatar5.png",
"avatar6.png"

];

const borders = [

"default",
"cyan",
"gold",
"mythic"

];

const banners = [

"banner1.jpg",
"banner2.jpg",
"banner3.jpg"

];

const themes = [

"dark",
"cyber",
"midnight"

];

// ==========================================================
// CREATE INVENTORY CARD
// ==========================================================

function createAvatarCard(file){

    const card = document.createElement("div");

    card.className = "inventory-item";

    card.dataset.avatar = file;

    card.innerHTML = `
        <img
        src="/static/img/avatars/${file}"
        alt="${file}">
    `;

    // Click event
    card.addEventListener("click", () => {
        selectAvatar(card);
    });

    avatarInventory.appendChild(card);

}

// ==========================================================
// LOAD AVATARS
// ==========================================================

avatars.forEach(file=>{

    createAvatarCard(file);

});

// ==========================================================
// CLICK TO EQUIP AVATAR
// ==========================================================

function selectAvatar(card){

    // Remove previous selection

    document
    .querySelectorAll("#avatarInventory .inventory-item")
    .forEach(item=>{

        item.classList.remove("active");

    });

    // Highlight selected

    card.classList.add("active");

    // Save selected filename

    current.avatar = card.dataset.avatar;

    // Update preview

    previewAvatar.src = `/static/img/avatars/${current.avatar}`;

}

// ==========================================================
// AUTO SELECT FIRST AVATAR
// ==========================================================

if(avatarInventory.firstElementChild){

    selectAvatar(avatarInventory.firstElementChild);

}

// ==========================================================
// SAVE TO FLASK
// ==========================================================

saveBtn.addEventListener("click", async ()=>{

    if(!current.avatar){

        alert("Select an avatar first!");

        return;

    }

    saveBtn.disabled = true;

    saveBtn.innerHTML = "Saving...";

    try{

        const response = await fetch("/api/save_avatar",{

            method:"POST",

            headers:{
                "Content-Type":"application/json"
            },

            body:JSON.stringify({

                avatar:current.avatar

            })

        });

        const result = await response.json();

        if(result.success){

            saveBtn.innerHTML = "✔ Saved";

        }else{

            saveBtn.innerHTML = "❌ Failed";

        }

    }catch(err){

        console.error(err);

        saveBtn.innerHTML = "❌ Error";

    }

    setTimeout(()=>{

        saveBtn.innerHTML = "💾 Save Changes";

        saveBtn.disabled = false;

    },1500);

});