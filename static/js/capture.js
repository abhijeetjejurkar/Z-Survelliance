function opencap() {
    $.getJSON('/cap', { },
        function(data) { });  
    document.getElementById("capture").style.display = "block";
    // document.getElementById("capture").style.color = "#111";
    // document.getElementById("").style.marginLeft= "0";
    // document.getElementById("main").style.width = "100vw";
    document.getElementById("capture").style.transition = "1.0s";
    // document.body.style.backgroundColor = "white";
    // $.ajax({
    //     url: "cap.py",
    //    context: document.body
    //   }).done(function() {
    //    alert('finished python script');;
    //   });    
    }