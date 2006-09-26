// Skript zum gr� und kleiner machen des Eingabefeldes
function init() {
    textarea = document.getElementById("edit_template");
}
function resize_big()   { textarea.rows = textarea.rows*1.5; }
function resize_small() { textarea.rows = textarea.rows/1.5; }
