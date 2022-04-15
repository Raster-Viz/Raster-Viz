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

// JD's drag-and-drop work:

//var toc_layer = document.getElementById("active_layer1"); // TESTING: For now we'll start with just this one layer but we'll need to figure out how to grab them dynamically since the names are made on the fly.
var draggable_layers = document.querySelectorAll('.draggable-layer'); // "Draggable-layer" is the class used in the HTML of the table row <tr> elements in the ToC (Table of Contents).
var layer_container = document.querySelectorAll('.layer'); // The class "layer" is the container in the html.

draggable_layers.forEach(draggable => {
    draggable.addEventListener('dragstart', () => {
        draggable.classList.add('dragging-layer')
        //console.log('drag test');
    });

    draggable.addEventListener('dragend', () => {
        draggable.classList.remove('dragging-layer')
    });
});

layer_container.forEach(container => {
    container.addEventListener('dragover', e => {
        e.preventDefault();
        const after_layer_elem = getDragAfterElement(container, e.clientY);
        console.log(after_layer_elem);
        const draggable = document.querySelector('.dragging-layer');
        if (after_layer_elem == null) {
            container.appendChild(draggable); // '.appendChild' is used to place the <tr> to the bottom of the rows it seems.
        } else {
            container.insertBefore(draggable, after_layer_elem);
        }
        //console.log('drag over test');
    });
});

function getDragAfterElement(container, y) {
    const draggable_layer_elem = [...container.querySelectorAll('.draggable-layer:not(.dragging-layer)')]; // The '[... ]' turn the '.querySelectorAll' into an array of layers and the 'not' excludes the one being drug.

    return draggable_layer_elem.reduce((closest, child) => {
        const box = child.getBoundingClientRect();
        const offset = y - box.top - box.height / 2; // This takes the top of the 'box' which is a row essentially, and calculates where to drop the dragged row.
        //console.log(box);
        if (offset < 0 && offset > closest.offset) {
            return { offset: offset, element: child};
        } else {
            return closest;
        }
    }, {offset: Number.NEGATIVE_INFINITY}).element;
}

/*toc_layer.ondragstart = function() {
    // TESTING: We have shown this will print something to the screen so we know it's reactive on drag even though it does nothing right now.
}*/

//////////


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

// Below JD is experimenting with draggable checkboxes

//$tr = $("#trLayer > tr:hover");

/*$(document).ready(function() {
    addDragAttr();
    //$tr.on("dragstart", layerCheckboxDragEvntHndlr);
});

function addDragAttr() {
    $("#trLayer > td", #trLayer2 > td"").attr("draggable", "true"); // For whatever reason this code refused to work.
}*/

/*function layerCheckboxDragEvntHndlr(event) {
    (event.originalEvent || event).dataTransfer.setData("text", $(this).text());
}*/
