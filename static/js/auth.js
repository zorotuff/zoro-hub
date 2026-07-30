console.log("AUTH JS LOADED 🔥");
const password=document.getElementById("password");
const eye=document.getElementById("togglePassword");

eye.onclick=()=>{

    if(password.type==="password"){

        password.type="text";
        eye.textContent="🙈";

    }else{

        password.type="password";
        eye.textContent="👁";

    }

};
const canvas = document.getElementById("bgCanvas");
const ctx = canvas.getContext("2d");

function resize() {
    canvas.width = innerWidth;
    canvas.height = innerHeight;
}

resize();
window.addEventListener("resize", resize);

const stars = [];

for (let i = 0; i < 150; i++) {
    stars.push({
        x: Math.random() * innerWidth,
        y: Math.random() * innerHeight,
        r: Math.random() * 2 + 0.5,
        speed: Math.random() * 0.4 + 0.1,
        alpha: Math.random()
    });
}

const trail = [];

window.addEventListener("mousemove", e => {

    trail.push({
        x: e.clientX,
        y: e.clientY,
        life: 1
    });

});

function draw() {

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Stars
    stars.forEach(s => {

        ctx.beginPath();

        ctx.fillStyle = `rgba(90,200,255,${s.alpha})`;

        ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);

        ctx.fill();

        s.y += s.speed;

        if (s.y > innerHeight) {

            s.y = -5;
            s.x = Math.random() * innerWidth;

        }

    });

    // Mouse trail
    for (let i = trail.length - 1; i >= 0; i--) {

        const p = trail[i];

        ctx.beginPath();

        ctx.fillStyle = `rgba(0,170,255,${p.life})`;

        ctx.arc(p.x, p.y, 6, 0, Math.PI * 2);

        ctx.fill();

        p.life -= 0.04;

        if (p.life <= 0)
            trail.splice(i, 1);

    }

    requestAnimationFrame(draw);

}

draw();