document.addEventListener("DOMContentLoaded",()=>{

const greeting=document.getElementById("greeting");

if(greeting){

const hour=new Date().getHours();

let text="WELCOME BACK";

if(hour<12){

text="GOOD MORNING";

}

else if(hour<18){

text="GOOD AFTERNOON";

}

else{

text="GOOD EVENING";

}

greeting.textContent=text;

}

});