/* ___________________________________________________________________________
 *  password input
 */


function init() {
    init_debug(); // from: shared_sha_tools.js

    debug("salt_1 value from server:" + salt_1);
    if (salt_1.length != 5) {
        alert("salt_1 from Server fail! len:" + salt_1.length); return false;
    }

    debug("salt_2 value from server:" + salt_2);
    if (salt_2.length != 5) {
        alert("salt_2 from Server fail!"); return false;
    }
    if (salt_2 == salt_1) {
        alert("wrong salt values. Both are the same!"); return false;
    }

    set_focus(focus_id);

    check_ok = true;
}

function check() {
    if (check_ok != true) {
       alert("Internal error.");
       return False;
    }

    in_pass = get_plaintext_pass("id_raw_password");
    if (in_pass == false) { return false; } // Error occurred

    set_value("id_raw_password", "", "grey");

    // Importent: Must be the same sha result as the django routine!
    sha_1 = make_SHA(salt_1 + in_pass);
    if (sha_1 == false) { return false; } // Error occurred

    sha_2 = make_SHA(salt_2 + in_pass);
    if (sha_2 == false) { return false; } // Error occurred

    // set the values and change the css color:
    set_value("id_sha_1", sha_1, "lightgreen");
    set_value("id_sha_2", sha_2, "lightgreen");

    check_ok = true;
    debug_confirm();

    return true;
}


