window.onload = function(){
	

  var chatContainer = document.createElement("article");
      chatContainer.className = "chat-container is-down";
      document.body.appendChild(chatContainer);

      chatContainer.innerHTML = `
      <div class = "show-hide-toggle one">Show chat</div>
      <iframe class = 'chat' src = 'https://minnit.chat/LNS?embed&&nickname='> </iframe`

var localStorage = window.localStorage;
;
if (typeof(localStorage!==undefined)||typeof(localStorage!==null)){
  Switch = "on";
  localStorage.setItem("switch", Switch)
}
if (typeof(localStorage!==undefined)||typeof(localStorage!==null)){
  var getSwitch = localStorage.getItem("switch");
}


  chat_container = document.querySelector(".chat-container");

 toggle_btn = document.querySelector(".show-hide-toggle");

 toggle_btn.addEventListener("click", toggle);
 
 function toggle(){


   if(chat_container.className == "chat-container is-down"){
   chat_container.className = "chat-container is-up";
   toggle_btn.innerHTML = "Hide chat";
   Switch = "off";
   localStorage.setItem("switch", Switch);

   toggle_btn.classList.remove("alert");

   toggle_btn.classList.remove("one")
   toggle_btn.classList.add("zero");



    }
    else {
      chat_container.className = "chat-container is-down";
      toggle_btn.innerHTML = "Show chat";
      toggle_btn.classList.remove("zero")
      toggle_btn.classList.add("one");
      Switch = "on";
      localStorage.setItem("switch", Switch);


    }
   // localStorage.setItem("switch", Switch);
   getSwitch = Switch;
         notify()


 }

var time = 1000*46;
var randomTime = Math.floor(Math.random()*time);

notify()
function notify(){
    console.log(getSwitch)
   if (window.localStorage.getItem("switch") == "off"){
   return;
}
else if (window.localStorage.getItem("switch") == "on"){
  //toggle_btn.classList.add("alert");
setInterval(function(){
  console.log(randomTime);
      toggle_btn.classList.remove("alert");

    setTimeout(function(){
        if (getSwitch == "on"){
     toggle_btn.classList.add("alert");
        }
    }, randomTime);

}, randomTime)
}
}

var style = document.createElement("style");
    style.textContent = `
.chat{
	height: 500px;
	width: 321px;
	background: white;
  border: none;
}


.chat-container{
  width: 321px;
  background: #067bff;;
  position: fixed;
  bottom: 1px;
  right: 1px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;


}

.is-down{
  transition: all 0.34s;
  transform: translateY(500px);
  width: 150px;
  overflow: hidden;
  border-radius: 30px;
}


.is-up{
  transition: all 0.34s;
  height: 540px;
  width: 321px;
  border-radius: 10px;
}




.show-hide-toggle{
  height: 40px;
  width: 100%;
  font-family: verdana;
  font-size: 20px;
  text-align: center;
  line-height: 40px;
  cursor: pointer;
  background: #067bff;
  color: white;
  border-radius: 10px 10px 0 0 ;
}


.alert{
  animation: flash 1s 3 forwards;
}

@keyframes flash{
  50% {
    background: red;
    transform: scale(1.1);
    color: red;
  }
  
}


`;
document.head.appendChild(style)


}