function openNav() {
    document.getElementById("mySidenav").style.width = "250px";
    document.getElementById("main").style.marginLeft = "250px";
    document.getElementById("main").style.width = "79vw";
    document.getElementById("main").style.transition = "0.5s";
    document.body.style.backgroundColor = "rgba(0,0,0,0.1)";
    }
  
function closeNav() {
    document.getElementById("mySidenav").style.width = "0";
    document.getElementById("main").style.marginLeft= "0";
    document.getElementById("main").style.width = "100vw";
    document.getElementById("main").style.transition = "0.5s";
    document.body.style.backgroundColor = "white";
    }