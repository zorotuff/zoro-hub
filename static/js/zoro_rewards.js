/* ---------- Zoro Hub reward pipeline ----------
   Shared by every game page. Two calls:
     zoroStartSession(gameId)   -- call when a match/attempt begins
     zoroReportResult(gameId, tier) -- call when it ends with a real result
   Both hit the real backend; nothing here decides the reward amount --
   the server does, using the session token this file gets from it.
*/

let zoroSessionToken = null;

async function zoroStartSession(gameId) {
    try {
        const res = await fetch("/api/games/start", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ game_id: gameId })
        });
        const data = await res.json();
        zoroSessionToken = data.session_token || null;
    } catch (e) {
        console.warn("Zoro Hub: could not start a reward session", e);
        zoroSessionToken = null;
    }
}

async function zoroReportResult(gameId, tier) {
    if (!zoroSessionToken) return null;
    const tokenToRedeem = zoroSessionToken;
    zoroSessionToken = null; // one reward per session, always -- clear immediately
    try {
        const res = await fetch("/api/games/report-result", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ game_id: gameId, tier: tier, session_token: tokenToRedeem })
        });
        const data = await res.json();
        return res.ok ? data : null;
    } catch (e) {
        console.warn("Zoro Hub: could not report the result", e);
        return null;
    }
}
