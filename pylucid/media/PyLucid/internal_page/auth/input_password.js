/* ___________________________________________________________________________
 *  password input
 */


function init() {
    init_debug() // from: shared_sha_tools.js

    debug("salt value from server:" + salt);
    if (salt.length != 5) {
        alert("salt from Server fail!"); return false;
    }

    debug("challenge value from server:" + challenge);
    if (challenge.length != 5) {
        alert("challenge from Server fail!"); return false;
    }

    set_focus(focus_id);

    check_ok = true;
}

function check() {
    if (check_ok != true) {
       alert("Internal error.");
       return False;
    }

    in_pass = document.getElementById("plaintext_pass").value;
    debug("in_pass:" + in_pass);
    if (in_pass.length<8) {
        alert("Password min len 8! - current len:" + in_pass.length);
        return false;
    }

    for (var i = 1; i <= in_pass.length; i++) {
       unicode_charcode = in_pass.charCodeAt(i);
       if (unicode_charcode > 127) {
           alert("Only ASCII letters are allowed!");
           return false;
       }
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
    document.getElementById("sha_a2").value = sha_a2;
    change_color("sha_a2", "lightgreen");
    document.getElementById("sha_b").value = sha_b;
    change_color("sha_b", "lightgreen");

    document.getElementById("plaintext_pass").value = "";
    change_color("plaintext_pass", "grey");

    document.login.action = submit_url;

    check_ok = true;
    debug_confirm();

    return true;
}


