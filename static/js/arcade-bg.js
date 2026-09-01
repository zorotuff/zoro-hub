// ==========================================
// ZORO ARCADE 3D BACKGROUND
// ==========================================

// Scene
const scene = new THREE.Scene();

// Camera
const camera = new THREE.PerspectiveCamera(

75,

window.innerWidth / window.innerHeight,

0.1,

1000

);

camera.position.z = 8;

// Renderer
const renderer = new THREE.WebGLRenderer({

canvas: document.getElementById("bg3d"),

alpha: true,

antialias: true

});

renderer.setSize(

window.innerWidth,

window.innerHeight

);

renderer.setPixelRatio(

window.devicePixelRatio

);

// ==========================================
// Resize
// ==========================================

window.addEventListener("resize",()=>{

camera.aspect =

window.innerWidth /

window.innerHeight;

camera.updateProjectionMatrix();

renderer.setSize(

window.innerWidth,

window.innerHeight

);

});

// ==========================================
// STARS
// ==========================================

const starGeometry = new THREE.BufferGeometry();

const starCount = 500;

const positions = [];

for(let i=0;i<starCount;i++){

positions.push(

(Math.random()-0.5)*120,

(Math.random()-0.5)*120,

(Math.random()-0.5)*120

);

}

starGeometry.setAttribute(

'position',

new THREE.Float32BufferAttribute(

positions,

3

)

);

const starMaterial = new THREE.PointsMaterial({

color:0xffffff,

size:0.18,

transparent:true,

opacity:0.9

});

const stars = new THREE.Points(

starGeometry,

starMaterial

);

scene.add(stars);

// ==========================================
// ANIMATION
// ==========================================

function animate(){

requestAnimationFrame(animate);

stars.rotation.y += 0.0004;

stars.rotation.x += 0.00015;

renderer.render(

scene,

camera

);

}

animate();