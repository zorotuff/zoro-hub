const isOwner = window.ZORO_ADMIN_ROLE === "owner";

// ==========================================================
// TABS
// ==========================================================

document.querySelectorAll(".adm-tab").forEach(tab => {
    tab.addEventListener("click", () => {
        document.querySelectorAll(".adm-tab").forEach(t => t.classList.remove("active"));
        document.querySelectorAll(".adm-panel").forEach(p => p.classList.remove("active"));
        tab.classList.add("active");
        document.getElementById("panel-" + tab.dataset.tab).classList.add("active");

        if (tab.dataset.tab === "users" && !usersLoadedOnce) loadUsers();
        if (tab.dataset.tab === "log" && !logLoadedOnce) loadAuditLog();
    });
});

let usersLoadedOnce = false;
let logLoadedOnce = false;

// ==========================================================
// TOAST
// ==========================================================

function toast(text, kind) {
    let el = document.getElementById("adm-toast");
    if (!el) {
        el = document.createElement("div");
        el.id = "adm-toast";
        el.className = "adm-toast";
        document.body.appendChild(el);
    }
    el.textContent = text;
    el.className = "adm-toast " + (kind || "info") + " visible";
    clearTimeout(el._t);
    el._t = setTimeout(() => el.classList.remove("visible"), 3000);
}

async function api(path, opts) {
    const res = await fetch(path, {
        headers: { "Content-Type": "application/json" },
        ...opts,
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok || data.success === false) {
        toast(data.detail || data.error || "Something went wrong.", "error");
        throw new Error(data.detail || data.error || `HTTP ${res.status}`);
    }
    return data;
}

// ==========================================================
// OVERVIEW
// ==========================================================

async function loadStats() {
    try {
        const data = await api("/admin/api/stats");
        const s = data.stats;
        const cards = [
            [s.total_users, "Total Users"],
            [s.total_suspended, "Suspended"],
            [s.total_moderators, "Moderators"],
            [s.total_coins_in_circulation.toLocaleString(), "Coins in Circulation"],
            [s.total_purchases, "Shop Purchases"],
            [s.total_game_results, "Games Completed"],
        ];
        document.getElementById("stats-grid").innerHTML = cards.map(([v, l]) => `
            <div class="adm-stat-card">
                <div class="adm-stat-value">${v}</div>
                <div class="adm-stat-label">${l}</div>
            </div>
        `).join("");
    } catch (e) { /* toast already shown */ }
}

// ==========================================================
// USERS
// ==========================================================

async function loadUsers(search) {
    usersLoadedOnce = true;
    const tbody = document.getElementById("users-tbody");
    tbody.innerHTML = `<tr><td colspan="7" style="color:var(--adm-muted);">Loading…</td></tr>`;
    try {
        const q = search ? `?search=${encodeURIComponent(search)}` : "";
        const data = await api("/admin/api/users" + q);
        if (!data.users.length) {
            tbody.innerHTML = `<tr><td colspan="7" style="color:var(--adm-muted);">No users found.</td></tr>`;
            return;
        }
        tbody.innerHTML = data.users.map(u => `
            <tr data-username="${escapeHtml(u.username)}">
                <td><strong>${escapeHtml(u.username)}</strong></td>
                <td><span class="adm-pill role-${u.role}">${u.role}</span></td>
                <td>${u.level}</td>
                <td>${u.coins.toLocaleString()}</td>
                <td>${escapeHtml((u.account_creation_date || "").split(" ")[0])}</td>
                <td>
                    ${u.suspended ? '<span class="adm-pill suspended">Suspended</span>' : ""}
                    ${!u.leaderboard_visible ? '<span class="adm-pill hidden-lb">Hidden from LB</span>' : ""}
                </td>
                <td><button class="adm-btn small view-user-btn">View</button></td>
            </tr>
        `).join("");
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="7" style="color:var(--adm-muted);">Couldn't load users.</td></tr>`;
    }
}

document.getElementById("user-search-btn").addEventListener("click", () => {
    loadUsers(document.getElementById("user-search").value.trim());
});
document.getElementById("user-search").addEventListener("keydown", (e) => {
    if (e.key === "Enter") loadUsers(e.target.value.trim());
});

document.getElementById("users-tbody").addEventListener("click", (e) => {
    if (!e.target.classList.contains("view-user-btn")) return;
    const username = e.target.closest("tr").dataset.username;
    openUserDrawer(username);
});

// ==========================================================
// USER DETAIL DRAWER
// ==========================================================

async function openUserDrawer(username) {
    document.getElementById("drawer-backdrop").classList.remove("hidden");
    document.getElementById("user-drawer").classList.remove("hidden");
    document.getElementById("drawer-content").innerHTML = "Loading…";

    try {
        const data = await api(`/admin/api/users/${encodeURIComponent(username)}`);
        renderDrawer(data.user);
    } catch (e) {
        document.getElementById("drawer-content").innerHTML = "Couldn't load this user.";
    }
}

function closeDrawer() {
    document.getElementById("drawer-backdrop").classList.add("hidden");
    document.getElementById("user-drawer").classList.add("hidden");
}
document.getElementById("drawer-close").addEventListener("click", closeDrawer);
document.getElementById("drawer-backdrop").addEventListener("click", closeDrawer);

function renderDrawer(u) {
    const canModerate = u.role === "user" || isOwner;

    document.getElementById("drawer-content").innerHTML = `
        <h2 style="margin:8px 0 2px;">${escapeHtml(u.username)}</h2>
        <p style="color:var(--adm-muted); font-size:12px; margin:0 0 18px;">${escapeHtml(u.uid)} · joined ${escapeHtml((u.account_creation_date||"").split(" ")[0])}</p>

        <div class="adm-row">
            <span class="adm-pill role-${u.role}">${u.role}</span>
            ${u.suspended ? '<span class="adm-pill suspended">Suspended</span>' : ""}
            ${!u.leaderboard_visible ? '<span class="adm-pill hidden-lb">Hidden from leaderboard</span>' : ""}
        </div>

        <div class="adm-card" style="padding:14px;">
            <div class="adm-row" style="margin-bottom:0;">
                <div><div class="adm-stat-value" style="font-size:18px;">${u.level}</div><div class="adm-stat-label">Level</div></div>
                <div><div class="adm-stat-value" style="font-size:18px;">${u.xp}</div><div class="adm-stat-label">XP</div></div>
                <div><div class="adm-stat-value" style="font-size:18px;">${u.coins.toLocaleString()}</div><div class="adm-stat-label">Coins</div></div>
                <div><div class="adm-stat-value" style="font-size:18px;">${u.games_won}/${u.games_played}</div><div class="adm-stat-label">Won/Played</div></div>
            </div>
        </div>

        <h3 style="font-size:13px; margin:18px 0 8px;">Inventory (${u.inventory.length})</h3>
        <p style="font-size:12px; color:var(--adm-muted);">${u.inventory.map(i => escapeHtml(i.item_id)).join(", ") || "Nothing owned yet."}</p>

        <h3 style="font-size:13px; margin:18px 0 8px;">Recent Transactions</h3>
        <div class="adm-tx-list">
            ${u.recent_transactions.slice(0,8).map(t => `
                <div class="adm-tx-row">
                    <span>${escapeHtml(t.type)}${t.related_item ? " · " + escapeHtml(t.related_item) : ""}</span>
                    <span>${t.amount > 0 ? "+" : ""}${t.amount.toLocaleString()}</span>
                </div>
            `).join("") || "<p style='color:var(--adm-muted);font-size:12px;'>No transactions yet.</p>"}
        </div>

        <h3 style="font-size:13px; margin:18px 0 8px;">Moderation</h3>
        ${!canModerate ? `<p class="adm-hint">This account outranks your role — only an owner can act on it.</p>` : ""}

        <div class="adm-row">
            ${u.suspended
                ? `<button class="adm-btn" id="btn-restore" ${!canModerate?"disabled":""}>Restore</button>`
                : `<button class="adm-btn danger" id="btn-suspend" ${!canModerate?"disabled":""}>Suspend</button>`
            }
            <button class="adm-btn" id="btn-toggle-lb" ${!canModerate?"disabled":""}>
                ${u.leaderboard_visible ? "Hide from Leaderboard" : "Unhide from Leaderboard"}
            </button>
        </div>

        ${isOwner ? `
        <h3 style="font-size:13px; margin:18px 0 8px;">Role (owner only)</h3>
        <div class="adm-row">
            <select class="adm-select" id="role-select" ${u.role === "owner" ? "disabled" : ""}>
                <option value="user" ${u.role==="user"?"selected":""}>User</option>
                <option value="moderator" ${u.role==="moderator"?"selected":""}>Moderator (small admin)</option>
            </select>
            <button class="adm-btn primary" id="btn-set-role" ${u.role === "owner" ? "disabled" : ""}>Apply</button>
        </div>
        <p class="adm-hint">Owner status can't be granted here — that's intentional.</p>

        <h3 style="font-size:13px; margin:18px 0 8px;">Adjust Coins / XP (owner only)</h3>
        <div class="adm-row">
            <input class="adm-input" type="number" id="coins-amount" placeholder="±amount" style="width:110px;">
            <button class="adm-btn" id="btn-coins">Apply to Coins</button>
        </div>
        <div class="adm-row">
            <input class="adm-input" type="number" id="xp-amount" placeholder="±amount" style="width:110px;">
            <button class="adm-btn" id="btn-xp">Apply to XP</button>
        </div>
        <input class="adm-input" id="adjust-reason" placeholder="reason (required)" style="width:100%; margin-bottom:14px;">
        ` : ""}
    `;

    wireDrawerActions(u.username, canModerate);
}

function wireDrawerActions(username, canModerate) {
    const suspendBtn = document.getElementById("btn-suspend");
    if (suspendBtn) suspendBtn.addEventListener("click", async () => {
        const reason = prompt("Reason for suspending this account?");
        if (!reason) return;
        try {
            await api(`/admin/api/users/${encodeURIComponent(username)}/suspend`, {
                method: "POST", body: JSON.stringify({ reason })
            });
            toast("Account suspended.", "success");
            openUserDrawer(username); loadUsers();
        } catch (e) {}
    });

    const restoreBtn = document.getElementById("btn-restore");
    if (restoreBtn) restoreBtn.addEventListener("click", async () => {
        try {
            await api(`/admin/api/users/${encodeURIComponent(username)}/restore`, { method: "POST" });
            toast("Account restored.", "success");
            openUserDrawer(username); loadUsers();
        } catch (e) {}
    });

    const lbBtn = document.getElementById("btn-toggle-lb");
    if (lbBtn) lbBtn.addEventListener("click", async () => {
        const wantVisible = lbBtn.textContent.includes("Unhide");
        try {
            await api(`/admin/api/users/${encodeURIComponent(username)}/leaderboard-visibility`, {
                method: "POST", body: JSON.stringify({ visible: wantVisible, reason: "admin panel toggle" })
            });
            toast(wantVisible ? "Unhidden from leaderboard." : "Hidden from leaderboard.", "success");
            openUserDrawer(username); loadUsers();
        } catch (e) {}
    });

    const roleBtn = document.getElementById("btn-set-role");
    if (roleBtn) roleBtn.addEventListener("click", async () => {
        const role = document.getElementById("role-select").value;
        const reason = prompt(`Reason for changing ${username}'s role to ${role}?`);
        if (!reason) return;
        try {
            await api(`/admin/api/users/${encodeURIComponent(username)}/role`, {
                method: "POST", body: JSON.stringify({ role, reason })
            });
            toast("Role updated.", "success");
            openUserDrawer(username); loadUsers();
        } catch (e) {}
    });

    const coinsBtn = document.getElementById("btn-coins");
    if (coinsBtn) coinsBtn.addEventListener("click", async () => {
        const amount = parseInt(document.getElementById("coins-amount").value, 10);
        const reason = document.getElementById("adjust-reason").value.trim();
        if (!amount || !reason) { toast("Amount and reason are both required.", "error"); return; }
        try {
            await api(`/admin/api/users/${encodeURIComponent(username)}/coins`, {
                method: "POST", body: JSON.stringify({ amount, reason })
            });
            toast(`Coins adjusted by ${amount}.`, "success");
            openUserDrawer(username); loadUsers();
        } catch (e) {}
    });

    const xpBtn = document.getElementById("btn-xp");
    if (xpBtn) xpBtn.addEventListener("click", async () => {
        const amount = parseInt(document.getElementById("xp-amount").value, 10);
        const reason = document.getElementById("adjust-reason").value.trim();
        if (!amount || !reason) { toast("Amount and reason are both required.", "error"); return; }
        try {
            await api(`/admin/api/users/${encodeURIComponent(username)}/xp`, {
                method: "POST", body: JSON.stringify({ amount, reason })
            });
            toast(`XP adjusted by ${amount}.`, "success");
            openUserDrawer(username); loadUsers();
        } catch (e) {}
    });
}

// ==========================================================
// ACCOUNTS CREATED BETWEEN DATES
// ==========================================================

document.getElementById("created-search-btn").addEventListener("click", async () => {
    const from = document.getElementById("created-from").value;
    const to = document.getElementById("created-to").value;
    const tbody = document.getElementById("created-tbody");
    const summary = document.getElementById("created-summary");

    if (!from || !to) { toast("Pick both a from and to date.", "error"); return; }

    tbody.innerHTML = `<tr><td colspan="4" style="color:var(--adm-muted);">Loading…</td></tr>`;
    try {
        const data = await api(`/admin/api/users/created-between?from=${from}&to=${to}`);
        summary.textContent = `${data.count} account(s) created from ${data.from} to ${data.to}.`;
        if (!data.accounts.length) {
            tbody.innerHTML = `<tr><td colspan="4" style="color:var(--adm-muted);">None in this range.</td></tr>`;
            return;
        }
        tbody.innerHTML = data.accounts.map(a => `
            <tr>
                <td><strong>${escapeHtml(a.username)}</strong></td>
                <td>${escapeHtml(a.uid)}</td>
                <td><span class="adm-pill role-${a.role}">${a.role}</span></td>
                <td>${escapeHtml(a.account_creation_date)}</td>
            </tr>
        `).join("");
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="4" style="color:var(--adm-muted);">Couldn't load that range.</td></tr>`;
    }
});

// ==========================================================
// AUDIT LOG
// ==========================================================

async function loadAuditLog() {
    logLoadedOnce = true;
    const el = document.getElementById("log-list");
    el.innerHTML = `<p style="color:var(--adm-muted);">Loading…</p>`;
    try {
        const data = await api("/admin/api/audit-log?limit=100");
        if (!data.entries.length) {
            el.innerHTML = `<p style="color:var(--adm-muted);">No actions logged yet.</p>`;
            return;
        }
        el.innerHTML = data.entries.map(e => `
            <div class="adm-log-row">
                <span class="adm-log-meta">${escapeHtml(e.created_at)}</span>
                <span>
                    <span class="adm-log-action">${escapeHtml(e.action)}</span>
                    on <strong>${escapeHtml(e.target_id || "—")}</strong>
                    ${e.reason ? " — " + escapeHtml(e.reason) : ""}
                    <br><span class="adm-log-meta">by ${escapeHtml(e.admin_username)} (${escapeHtml(e.admin_role)})</span>
                </span>
                <span class="adm-log-meta">${escapeHtml(e.target_type)}</span>
            </div>
        `).join("");
    } catch (e) {
        el.innerHTML = `<p style="color:var(--adm-muted);">Couldn't load the audit log.</p>`;
    }
}

// ==========================================================
// UTIL
// ==========================================================

function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

// ==========================================================
// START
// ==========================================================

loadStats();
