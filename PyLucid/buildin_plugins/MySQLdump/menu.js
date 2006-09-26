function set_all( value ) {
    form = document.getElementById("sqldump_form");
    for (i = 0; i < form.length; i++) {
        if (form[i].value == value) {
            form[i].checked = true;
        }
    }
}
