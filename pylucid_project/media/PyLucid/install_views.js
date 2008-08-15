/* ___________________________________________________________________________
 *  _install section login
 *
 * used in login and generate hash view!
 *
 * some routines exist from {{ PyLucid_media_url }}/shared_sha_tools.js
 * and {{ PyLucid_media_url }}/sha.js
 */

/* uncomment to activate the debug window */
//debug_msg = true;

function shared_init() {
    /* init stuff for both install views: install/generate hash */

    /* The login form was hide via CSS. After JS loaded fine, we unhide it. */
    unhide_by_id("password_form"); // from: shared_sha_tools.js

    set_focus("plaintext_pass");
}


function login_init() {
    shared_init();

    /* After generating the install hash, the form should be submit */
    submit_form = true;

    debug("salt value from server:" + salt);
    if (salt.length != SALT_LEN) {
        alert("salt from Server fail!");
        return false;
    }
    check_ok = true; // initial set to false in shared_sha_tools.js
}


function generate_hash_init() {
    shared_init();

    /* The form should not submit, after generating the install hash */
    submit_form = false;

    salt = generate_salt();
    debug("generated JS salt value:" + salt);
    if (salt==false) {
        return false;
    }
    check_ok = true; // initial set to false in shared_sha_tools.js
}


function make_hash(submit) {
    /*
    processing the form data for the both install views: login & generate hash
    The only difference here is:
        * The given salt value:
            * login view:
                The salt value was insert into the html page from the server
            * generate hash view:
                The salt value is a random JS number generated in init()
        * only the login view must submit the form.
    */
    if (check_ok != true) {
       alert("Internal error. (check_ok not 'true')");
       return false;
    }

    in_pass = get_plaintext_pass("plaintext_pass");
    if (in_pass==false) {
        return false;
    }

    sha = hex_sha1(salt + in_pass);
    hash = "sha1$" + salt + "$" + sha;

    set_value("hash", hash);
    change_color("hash", "#90EE90");

    set_value("plaintext_pass", "");
    change_color("plaintext_pass", "#808080");

    debug_confirm();
    if (submit_form==true) {
        /* Only in the login view, the form must be submit */
        document.login.submit();
    } else {
        /* The generate hash should never send the form back to the server! */
        return false;
    }
}


function generate_salt() {
    /* return a random string: six digit number */
    salt = Math.random();
    // convert to a string:
    salt = "" + salt;
    // get 5 decimal places after the comma:
    salt = salt.substring(2, 7);
    if (salt.length != SALT_LEN) {
        alert("generating a random salt fail!");
        return false;
    }
    return salt
}