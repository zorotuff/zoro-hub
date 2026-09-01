const switchBtn = document.getElementById("switchToV5");

if(switchBtn){

switchBtn.addEventListener("click", async ()=>{

await fetch("/api/change_hub",{

method:"POST",

headers:{
"Content-Type":"application/json"
},

body:JSON.stringify({

version:"v5"

})

});

window.location.href="/hub";

});

}