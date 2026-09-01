/* ==========================================================
                    ZORO HUB LOGIN
========================================================== */

const loginTab =
document.getElementById("loginTab");

const registerTab =
document.getElementById("registerTab");

const loginForm =
document.getElementById("loginForm");

const registerForm =
document.getElementById("registerForm");

/* ==========================================================
                SWITCH TO LOGIN
========================================================== */

loginTab.addEventListener("click",()=>{

    loginTab.classList.add("active");

    registerTab.classList.remove("active");

    loginForm.style.display="flex";

    registerForm.style.display="none";

});

/* ==========================================================
                SWITCH TO REGISTER
========================================================== */

registerTab.addEventListener("click",()=>{

    registerTab.classList.add("active");

    loginTab.classList.remove("active");

    registerForm.style.display="flex";

    loginForm.style.display="none";

});

/* ==========================================================
                    INPUT EFFECT
========================================================== */

document.querySelectorAll("input").forEach(input=>{

    input.addEventListener("focus",()=>{

        input.parentElement?.classList.add("focus");

    });

    input.addEventListener("blur",()=>{

        input.parentElement?.classList.remove("focus");

    });

});

/* ==========================================================
                BUTTON LOADING
========================================================== */

document.querySelectorAll("form").forEach(form=>{

    form.addEventListener("submit",()=>{

        const btn =
        form.querySelector(".main-btn");

        btn.innerText="Loading...";

        btn.disabled=true;

    });

});