// Get main modal and content modals
var modal = document.getElementById("mainModal");
var modal_import = document.getElementById("modal_import");
var modal_openENV = document.getElementById("modal_openENV");
var modal_remove = document.getElementById("modal_remove");
var modal_properties = document.getElementById("modal_properties");

// Get the buttons that open the modal
var btn_import = document.getElementById("btn_import");
var btn_openENV = document.getElementById("btn_openENV");
var btn_remove = document.getElementById("btn_remove");
var btn_properties = document.getElementById("btn_properties");

// Get the <span> element that closes the modal
var spans = document.getElementsByClassName("close");

// When the user clicks the button, show correct modal
btn_import.onclick = function() {
    modal.style.display = "block";
    modal_import.style.display = "block";
    modal_openENV.style.display = "none";
    modal_remove.style.display = "none";
    modal_properties.style.display = "none";
}

btn_openENV.onclick = function() {
    modal.style.display = "block";
    modal_openENV.style.display = "block";
    modal_import.style.display = "none";
    modal_remove.style.display = "none";
    modal_properties.style.display = "none";
}

btn_remove.onclick = function() {
    modal.style.display = "block";
    modal_remove.style.display = "block";
    modal_import.style.display = "none";
    modal_openENV.style.display = "none";
    modal_properties.style.display = "none";
}

btn_properties.onclick = function() {
    modal.style.display = "block";
    modal_properties.style.display = "block";
    modal_import.style.display = "none";
    modal_openENV.style.display = "none";
    modal_remove.style.display = "none";
}

// When the user clicks on <span> (x), close the modal
window.onload = function() {
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
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
        modal_import.style.display = "none";
        modal_openENV.style.display = "none";
        modal_properties.style.display = "none";
    }
}

function changefunction(i) {
    if (i == "print") {
        window.print()
    }
    if (i == "save") {
        window.location.href = "index.html"
    }
}

function toggle_visibility(id, separate) {
    var e = document.getElementById(id);
    var v = document.getElementById(separate);
    e.style.display = 'block';
    v.style.display = 'none';
}