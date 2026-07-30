// =========================================
// PROFILE.JS
// =========================================

// ---------- Elements ----------
const avatarBtn = document.getElementById("avatarBtn");
const avatarModal = document.getElementById("avatarModal");
const closeAvatarModal = document.getElementById("closeAvatarModal");

const avatarPreview = document.getElementById("avatarPreview");
const bioInput = document.getElementById("bioInput");
const saveBtn = document.getElementById("saveBtn");

const avatarImages = document.querySelectorAll("#avatarGrid img");

// ---------- Current ----------
let currentAvatar = avatarPreview.src.split("/").pop();

// OPEN
avatarBtn.onclick = () => {
    avatarModal.style.display = "flex";
};

// CLOSE BUTTON
closeAvatarModal.onclick = () => {
    avatarModal.style.display = "none";
};

// CLICK OUTSIDE
avatarModal.onclick = (e) => {
    if (e.target === avatarModal) {
        avatarModal.style.display = "none";
    }
};

// ---------- Select Avatar ----------
avatarImages.forEach(img=>{

    if(img.dataset.avatar===currentAvatar){

        img.classList.add("selected");

    }

    img.addEventListener("click",()=>{

        avatarImages.forEach(i=>i.classList.remove("selected"));

        img.classList.add("selected");

        currentAvatar=img.dataset.avatar;

        avatarPreview.src="/static/img/avatars/"+currentAvatar;

    });

});

// ---------- Save ----------
saveBtn.addEventListener("click",async()=>{

    saveBtn.disabled=true;
    saveBtn.innerText="Saving...";

    try{

        const response=await fetch("/api/save_profile", {

            method:"POST",

            headers:{
                "Content-Type":"application/json"
            },

            body:JSON.stringify({

                avatar:currentAvatar,

                bio:bioInput.value

            })

        });

        const data=await response.json();

        if(data.success){

            saveBtn.innerText="✔ Saved";

            avatarModal.classList.add("hidden");

        }else{

            saveBtn.innerText="❌ Failed";

        }

    }

    catch(err){

        console.error(err);

        saveBtn.innerText="❌ Error";

    }

    setTimeout(()=>{

        saveBtn.innerText="💾 Save Profile";

        saveBtn.disabled=false;

    },1500);

});