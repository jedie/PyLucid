function init_tinyMCE() {
    tinyMCE.init({
        apply_source_formatting : true,
        mode : "textareas",
        plugins : "table,fullscreen",
        theme_advanced_buttons3_add : "tablecontrols,fullscreen",
        height : "480",
        auto_focus : "mce_editor_0",
        theme : "advanced",
    });
}

page_content_changed = 0;

// resize the textarea
function resize_big() {
    textarea = document.getElementsByTagName("textarea")[0]
    textarea.rows = textarea.rows*1.2;
}
function resize_small() {
    textarea = document.getElementsByTagName("textarea")[0]
    textarea.rows = textarea.rows/1.2;
}

// tinyTextile help and TagList in a window
function OpenInWindow(URL) {
  win1 = window.open(URL, "", "width=1000, height=600, dependent=yes, resizable=yes, scrollbars=yes, location=no, menubar=no, status=no, toolbar=no");
  win1.focus();
}

// encode from db warning
function encoding_warning() {
  if (page_content_changed == 1) {
    return confirm('Made changes are lost! Continue?');
  }
}