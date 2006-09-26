// Skript zum größer und kleiner machen des Eingabefeldes
function init() {
    textarea = document.getElementById("edit_style");
}
function resize_big()   { textarea.rows = textarea.rows*1.5; }
function resize_small() { textarea.rows = textarea.rows/1.5; }
