if (!tinyMCE) {
    alert("Error: tinyMCE not loaded!");
} else {
    try {
        tinyMCE.init({
            apply_source_formatting : true,
            mode : "textareas",
            height : "450",
            plugins : "table,fullscreen",
            theme_advanced_buttons3_add : "tablecontrols,fullscreen",
            theme : "advanced",
        });
    } catch (e) {
        alert("tinyMCE.init() error:" + e);
    }
}