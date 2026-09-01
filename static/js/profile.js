// ==========================================================
// TABS
// ==========================================================

document.querySelectorAll(".pf-tab").forEach(tab => {
    tab.addEventListener("click", () => {
        document.querySelectorAll(".pf-tab").forEach(t => t.classList.remove("active"));
        document.querySelectorAll(".pf-panel").forEach(p => p.classList.remove("active"));
        tab.classList.add("active");
        document.getElementById("tab-" + tab.dataset.tab).classList.add("active");
    });
});

// ==========================================================
// TOAST
// ==========================================================

function pfToast(text, kind) {
    let el = document.getElementById("pf-toast");
    if (!el) {
        el = document.createElement("div");
        el.id = "pf-toast";
        el.className = "pf-toast";
        document.body.appendChild(el);
    }
    el.textContent = text;
    el.className = "pf-toast " + (kind || "info") + " visible";
    clearTimeout(el._t);
    el._t = setTimeout(() => el.classList.remove("visible"), 2800);
}

// ==========================================================
// BIO -- real endpoint this time (the old one, /api/save_profile,
// never existed, so Save never actually did anything before)
// ==========================================================

const bioInput = document.getElementById("bioInput");
const bioCount = document.getElementById("bioCount");
const saveBioBtn = document.getElementById("saveBioBtn");

if (bioInput) {
    const updateCount = () => { bioCount.textContent = bioInput.value.length; };
    bioInput.addEventListener("input", updateCount);
    updateCount();

    saveBioBtn.addEventListener("click", async () => {
        saveBioBtn.disabled = true;
        saveBioBtn.textContent = "Saving…";
        try {
            const res = await fetch("/api/profile/bio", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ bio: bioInput.value })
            });
            const data = await res.json();
            if (res.ok && data.success) {
                pfToast("Bio saved.", "success");
            } else {
                pfToast(data.detail || "Couldn't save your bio.", "error");
            }
        } catch (e) {
            pfToast("Couldn't save your bio.", "error");
        }
        saveBioBtn.disabled = false;
        saveBioBtn.textContent = "Save Bio";
    });
}

// ==========================================================
// EQUIP FROM PROFILE -- the exact same backend endpoint the
// Shop uses, not a second implementation
// ==========================================================

document.querySelectorAll(".equip-btn").forEach(btn => {
    btn.addEventListener("click", async () => {
        if (btn.disabled) return;
        const itemId = btn.dataset.itemId;
        btn.disabled = true;
        btn.textContent = "…";
        try {
            const res = await fetch("/shop/api/equip", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ item_id: itemId })
            });
            const data = await res.json();
            if (res.ok && data.success) {
                pfToast("Equipped — refreshing…", "success");
                setTimeout(() => window.location.reload(), 600);
            } else {
                pfToast(data.detail || "Couldn't equip that.", "error");
                btn.disabled = false;
                btn.textContent = "EQUIP";
            }
        } catch (e) {
            pfToast("Couldn't equip that.", "error");
            btn.disabled = false;
            btn.textContent = "EQUIP";
        }
    });
});
