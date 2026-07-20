// ==========================================================
// ZORO ARCADE V3
// ==========================================================

const slides = document.querySelectorAll(".featured-slide");

const nextBtn = document.getElementById("nextFeatured");

const prevBtn = document.getElementById("prevFeatured");

let currentSlide = 0;

let autoSlide;


// ==========================================================
// SHOW SLIDE
// ==========================================================

function showSlide(index){

slides.forEach((slide)=>{

slide.classList.remove("active");

});

slides[index].classList.add("active");

}


// ==========================================================
// NEXT
// ==========================================================

function nextSlide(){

currentSlide++;

if(currentSlide >= slides.length){

currentSlide = 0;

}

showSlide(currentSlide);

}


// ==========================================================
// PREVIOUS
// ==========================================================

function previousSlide(){

currentSlide--;

if(currentSlide < 0){

currentSlide = slides.length - 1;

}

showSlide(currentSlide);

}


// ==========================================================
// BUTTON EVENTS
// ==========================================================

if(nextBtn){

nextBtn.addEventListener("click",nextSlide);

}

if(prevBtn){

prevBtn.addEventListener("click",previousSlide);

}


// ==========================================================
// AUTO SLIDER
// ==========================================================

function startSlider(){

autoSlide = setInterval(()=>{

nextSlide();

},5000);

}

function stopSlider(){

clearInterval(autoSlide);

}


// ==========================================================
// PAUSE ON HOVER
// ==========================================================

const featured = document.getElementById("featuredContainer");

if(featured){

featured.addEventListener(

"mouseenter",

stopSlider

);

featured.addEventListener(

"mouseleave",

startSlider

);

}


// ==========================================================
// KEYBOARD SUPPORT
// ==========================================================

document.addEventListener("keydown",(e)=>{

if(e.key==="ArrowRight"){

nextSlide();

}

if(e.key==="ArrowLeft"){

previousSlide();

}

});


// ==========================================================
// START
// ==========================================================

showSlide(currentSlide);

startSlider();

// ==========================================
// 3D CARD TILT
// ==========================================

document.querySelectorAll(".game-card").forEach(card=>{

card.addEventListener("mousemove",(e)=>{

const rect=card.getBoundingClientRect();

const x=e.clientX-rect.left;

const y=e.clientY-rect.top;

const rotateY=((x/rect.width)-0.5)*18;

const rotateX=((y/rect.height)-0.5)*-18;

card.style.transform=
`rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-10px)`;

});

card.addEventListener("mouseleave",()=>{

card.style.transform=
"rotateX(0deg) rotateY(0deg) translateY(0px)";

});

});