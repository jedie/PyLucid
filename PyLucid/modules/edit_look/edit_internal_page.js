function show_html() {
    hover('html_toggle');
    show("ipage_details", focus=true);
    show('ipage_html', focus=false);
}
function show_css() {
    hover('css_toggle');
    show('ipage_css', focus=true);
    hide("ipage_details");
}
function show_js() {
    hover('js_toggle');
    show('ipage_js', focus=true);
    hide("ipage_details");
}
function show(obj_name, focus) {
    obj = document.getElementById(obj_name);
    obj.style.display = "";
    if (focus) obj.focus();
    if (obj_name != 'ipage_html') {hide('ipage_html')};
    if (obj_name != 'ipage_css') {hide('ipage_css')};
    if (obj_name != 'ipage_js') {hide('ipage_js')};
}
function hide(obj_name) {
    obj = document.getElementById(obj_name);
    obj.style.display = "none";
}
function hover(obj_name) {
    obj = document.getElementById(obj_name);
    obj.style.borderColor = "#555 #ddd #ddd #555";
    obj.style.backgroundColor = "#fff";
    if (obj_name != 'html_toggle') {normal('html_toggle')};
    if (obj_name != 'css_toggle') {normal('css_toggle')};
    if (obj_name != 'js_toggle') {normal('js_toggle')};
}
function normal(obj_name) {
    obj = document.getElementById(obj_name);
    obj.style.borderColor = "";
    obj.style.backgroundColor = "";
}

function resize_big()   {
    bigger("ipage_html");
    bigger("ipage_css");
    bigger("ipage_js");
}
function bigger(obj_name)   {
    textarea = document.getElementById(obj_name);
    textarea.rows = textarea.rows*1.5;
}
function resize_small() {
    smaller("ipage_html");
    smaller("ipage_css");
    smaller("ipage_js");
}
function smaller(obj_name) {
    textarea = document.getElementById(obj_name);
    textarea.rows = textarea.rows/1.5;
}