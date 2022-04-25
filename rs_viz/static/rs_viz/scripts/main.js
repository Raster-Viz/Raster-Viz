// Get main modal and content modals
var modal = document.getElementById("mainModal");
var modal_import = document.getElementById("modal_import");
var modal_openENV = document.getElementById("modal_openENV");
var modal_remove = document.getElementById("modal_remove");
var modal_properties = document.getElementById("modal_properties");

var add_layer_submit = document.getElementById("add_layer_submit");
var rm_layer_submit = document.getElementById("rm_layer_submit");
openENV_submit = document.getElementById("openENV_submit");

// Get the buttons that open the modal
var btn_addLayer = document.getElementById("btn_addLayer");
var btn_openENV = document.getElementById("btn_openENV");
var btn_remove = document.getElementById("btn_remove");
var btn_properties = document.getElementById("btn_properties");

// Get the <span> element that closes the modal
var spans = document.getElementsByClassName("close");

// When the user clicks the button, show correct modal
btn_addLayer.onclick = function () {
    modal.style.display = "block";
    modal_import.style.display = "block";
    modal_openENV.style.display = "none";
    modal_remove.style.display = "none";
    modal_properties.style.display = "none";
}

btn_openENV.onclick = function () {
    modal.style.display = "block";
    modal_openENV.style.display = "block";
    modal_import.style.display = "none";
    modal_remove.style.display = "none";
    modal_properties.style.display = "none";
}

btn_remove.onclick = function () {
    modal.style.display = "block";
    modal_remove.style.display = "block";
    modal_import.style.display = "none";
    modal_openENV.style.display = "none";
    modal_properties.style.display = "none";
}

btn_properties.onclick = function () {
    modal.style.display = "block";
    modal_properties.style.display = "block";
    modal_import.style.display = "none";
    modal_openENV.style.display = "none";
    modal_remove.style.display = "none";
}

// When the user clicks on <span> (x), close the modal
window.onload = function () {
    for (var i = 0; i < spans.length; i++) {
        var span = spans[i];
        span.onclick = function () {
            modal.style.display = "none";
            modal_import.style.display = "none";
            modal_openENV.style.display = "none";
            modal_properties.style.display = "none";
        }
    }
}

// When the user clicks anywhere outside the modal, close it
window.onclick = function (event) {
    if (event.target == modal) {
        modal.style.display = "none";
        modal_import.style.display = "none";
        modal_openENV.style.display = "none";
        modal_properties.style.display = "none";
    }
}

// Modals close on submit
add_layer_submit.onclick = function () {
    modal.style.display = "none";
}
openENV_submit.onclick = function () {
    modal.style.display = "none";
}
rm_layer_submit.onclick = function () {
    modal.style.display = "none";
}


function changefunction(i) {
    if (i == "print") {
        window.print()
    }
    if (i == "save") {
        window.location.href = "index.html"
    }
}

// Switch between Map and Image
function toggle_visibility(id, separate) {
    var e = document.getElementById(id);
    var v = document.getElementById(separate);
    e.style.display = 'block';
    v.style.display = 'none';
}

// Layer Collapsable
var coll = document.getElementsByClassName("collapsible");

for (let i = 0; i < coll.length; i++) {
    coll[i].addEventListener("click", function() {
        this.classList.toggle("active");
        var content = this.nextElementSibling;
        if (content.style.display === "block") {
            content.style.display = "none";
        } else {
            content.style.display = "block";
        }
    });
}