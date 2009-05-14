/* ___________________________________________________________________________
 *  password input
 *
 * some routines exist from {{ PyLucid_media_url }}/shared_sha_tools.js
 * and {{ PyLucid_media_url }}/sha.js
 */

function init() {
    /* The login form was hide via CSS. After JS loaded fine, we unhide it. */
    unhide_by_id("login_form"); // from: shared_sha_tools.js

    debug("salt value from server:" + salt);
    if (salt.length != SALT_LEN) {
        alert("salt from Server fail!");
        return false;
    }

    debug("challenge value from server:" + challenge);
    if (challenge.length != SALT_LEN) {
        alert("challenge from Server fail!");
        return false;
    }

    // The focus_id comes from the newforms fieldname
    set_focus(focus_id);

    check_ok = true; // initial set to false in shared_sha_tools.js
}

function check() {
    if (check_ok != true) {
       alert("Internal error.");
       return False;
    }

    in_pass = get_plaintext_pass("plaintext_pass");
    if (in_pass==false) {
        return false;
    }

    shapass = hex_sha1(salt + in_pass);
    debug("shapass - hex_sha(salt + in_pass):" + shapass);
    if (shapass.length!=HASH_LEN) {
        alert("hex_sha salt error! shapass length:" + shapass.length);
        return false;
    }

    // Passwort aufteilen
    sha_a = shapass.substr(0, HASH_LEN/2);
    sha_b = shapass.substr(HASH_LEN/2, HASH_LEN/2);
    debug("substr: sha_a:|"+sha_a+"| sha_b:|"+sha_b+"|");

    sha_a2 = hex_sha1(challenge + sha_a)
    debug("sha_a2 - hex_sha(challenge + sha_a): " + sha_a2);

    // hex_sha setzten
    set_value("sha_a2", sha_a2);
    change_color("sha_a2", "#90EE90");

    set_value("sha_b", sha_b);
    change_color("sha_b", "#90EE90");

    set_value("plaintext_pass", "");
    change_color("plaintext_pass", "#808080");

    document.login.action = submit_url;

    check_ok = true;
    debug_confirm();

    return true;
}


