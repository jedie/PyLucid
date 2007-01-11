// Skript zum größer und kleiner machen des Eingabefeldes
function init() {
    textarea = document.getElementById("edit_style");
}
function resize_big()   { textarea.rows = textarea.rows*1.5; }
function resize_small() { textarea.rows = textarea.rows/1.5; }

// tinyTextile help and TagList in a window
function OpenInWindow(URL) {
  win1 = window.open(URL, "", "width=1000, height=600, dependent=yes, resizable=yes, scrollbars=yes, location=no, menubar=no, status=no, toolbar=no");
  win1.focus();
}