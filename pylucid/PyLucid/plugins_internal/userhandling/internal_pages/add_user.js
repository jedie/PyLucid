function add_new_user_check() {
    add_new_user_username = document.getElementById("add_new_user_username").value;
    if (add_new_user_username.length<3) {
        alert("No username/too short (min 3 letters)");
        return false;
    }

    add_new_user_email = document.getElementById("add_new_user_email").value;
    if (add_new_user_email.length<9 || add_new_user_email.indexOf("@") == -1) {
        alert("The email address seems to be wrong!");
        return false;
    }

    add_new_user_realname = document.getElementById("add_new_user_realname").value;
    if (add_new_user_realname.length<3) {
        alert("No realname/too short (min 3 letters)");
        return false;
    }

    return true;
}