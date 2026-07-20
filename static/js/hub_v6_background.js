const bg=document.createElement("div");
bg.id="background";

document.body.prepend(bg);

// stars

for(let i=0;i<120;i++){

    const s=document.createElement("div");

    s.className="star";

    s.style.left=Math.random()*100+"vw";
    s.style.top=Math.random()*100+"vh";

    const size=Math.random()*4+1;

    s.style.width=size+"px";
    s.style.height=size+"px";

    s.style.animationDelay=Math.random()*4+"s";

    bg.appendChild(s);

}

// particles

for(let i=0;i<45;i++){

    const p=document.createElement("div");

    p.className="particle";

    p.style.left=Math.random()*100+"vw";
    p.style.bottom="-20px";

    p.style.animationDuration=(12+Math.random()*12)+"s";
    p.style.animationDelay=Math.random()*8+"s";

    bg.appendChild(p);

}

const aurora=document.createElement("div");
aurora.className="aurora";
bg.appendChild(aurora);