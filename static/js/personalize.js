// =====================================
// Selected Values
// =====================================

console.log("PERSONALIZE JS LOADED");

let selectedAvatar = null;
let selectedBanner = null;
let selectedBorder = null;

// =====================================
// Wait until page loads
// =====================================

document.addEventListener("DOMContentLoaded", () => {

    const previewAvatar = document.getElementById("previewAvatar");
    const previewBanner = document.getElementById("previewBanner");
    const saveBtn = document.getElementById("saveBtn");

    // ==========================
    // Avatar
    // ==========================

    document.querySelectorAll(".avatar-card").forEach(card => {

        card.addEventListener("click", () => {

            document.querySelectorAll(".avatar-card")
                .forEach(c => c.classList.remove("active"));

            card.classList.add("active");

            selectedAvatar = card.dataset.avatar;

            if (previewAvatar) {

                previewAvatar.src =
                    `/static/img/avatars/${selectedAvatar}.png?${Date.now()}`;

            }

        });

    });

    // ==========================
    // Banner
    // ==========================

    document.querySelectorAll(".banner-card").forEach(card => {

        card.addEventListener("click", () => {

            document.querySelectorAll(".banner-card")
                .forEach(c => c.classList.remove("active"));

            card.classList.add("active");

            selectedBanner = card.dataset.banner;

            if (previewBanner) {

                previewBanner.src =
                    `/static/img/banners/${selectedBanner}.png?${Date.now()}`;

            }

        });

    });

    // ==========================
    // Border
    // ==========================

    document.querySelectorAll(".border-card").forEach(card => {

    card.addEventListener("click", () => {

        document.querySelectorAll(".border-card")
            .forEach(c => c.classList.remove("active"));

        card.classList.add("active");

        selectedBorder = card.dataset.border;

        const frame = document.getElementById("previewFrame");

        if(frame){

            frame.className =
                `avatar-frame border-${selectedBorder}`;

        }

    });

});

    // ==========================
    // Save
    // ==========================

    if (saveBtn) {

        saveBtn.addEventListener("click", async () => {

            saveBtn.disabled = true;
            saveBtn.textContent = "Saving...";

            try {

                const response = await fetch("/save_personalize", {

                    method: "POST",

                    headers: {

                        "Content-Type": "application/json"

                    },

                    body: JSON.stringify({

                        avatar: selectedAvatar,
                        banner: selectedBanner,
                        border: selectedBorder

                    })

                });

                const data = await response.json();

                if (data.success) {

                    showToast("Profile saved!");

                    saveBtn.textContent = "Saved ✓";

                } else {

                    showToast("Save failed!", true);

                    saveBtn.textContent = "Failed";

                }

            } catch (err) {

                console.error(err);

                showToast("Server Error!", true);

                saveBtn.textContent = "Error";

            }

            setTimeout(() => {

                saveBtn.disabled = false;
                saveBtn.textContent = "💾 Save Changes";

            }, 1500);

        });

    }

});

// =====================================
// Toast
// =====================================

function showToast(message, error = false) {

    const toast = document.createElement("div");

    toast.className = "hub-toast";

    if (error) {

        toast.classList.add("error");

    }

    toast.textContent = message;

    document.body.appendChild(toast);

    requestAnimationFrame(() => {

        toast.classList.add("show");

    });

    setTimeout(() => {

        toast.classList.remove("show");

        setTimeout(() => {

            toast.remove();

        }, 300);

    }, 2500);

}