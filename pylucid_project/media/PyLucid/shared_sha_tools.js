/* ___________________________________________________________________________
 *  Some needed stuff round the SHA-JS-Login
 */

check_ok = false;
debug_msg = false;

// length of a SHA1 hexdigest string:
HASH_LEN = 40;
// length of the salt and challenge value string:
SALT_LEN = 5;


if (!document.getElementById) {
    alert("Error: Your Browser is not supported!");
}

if (navigator.cookieEnabled) {
    if (navigator.cookieEnabled != true) {
        alert("You must enable Cookies in your Browser!");
    }
}

/* ___________________________________________________________________________
 *  needfull generic functions:
 */

function get_value(object_id) {
    // get a form value
    try {
        return document.getElementById(object_id).value;
    } catch (e) {
        alert("get_value('"+object_id+"') error! " + e);
    }
}

function set_value(object_id, value) {
    // set a form value
    try {
        obj = document.getElementById(object_id).value = value;
    } catch (e) {
        alert("set_value('"+object_id+"', '"+value+"') error! " + e);
    }
}

function set_focus(object_id) {
    try {
        debug("set focus on id:" + object_id);
        document.getElementById(object_id).focus();
    } catch (e) {
        alert("set_focus('"+object_id+"') error:" + e);
    }
}

function hide_by_id(object_id) {
    try {
        debug("hide_by_id: "+object_id);
        obj = document.getElementById(object_id);
        obj.style.display = 'none';
    } catch (e) {
        alert("hide_by_id('"+object_id+"') error:" + e);
    }
}
function unhide_by_id(object_id) {
    try {
        debug("unhide_by_id: "+object_id);
        obj = document.getElementById(object_id);
        obj.style.display = 'block';
    } catch (e) {
        alert("unhide_by_id('"+object_id+"') error:" + e);
    }
}

function change_color(object_id, color_name) {
    try {
        debug("change_color: "+object_id);
        obj = document.getElementById(object_id);
        obj.style.backgroundColor = color_name;
    } catch (e) {
        alert("change_color('"+object_id+"', '"+color_name+"') error:" + e);
    }
}

/* ___________________________________________________________________________
 *  special functions:
 */

function check_ascii_only(data) {
    for (var i = 1; i <= data.length; i++) {
       unicode_charcode = data.charCodeAt(i);
       if (unicode_charcode > 127) {
            alert("Only ASCII letters are allowed!");
            return false;
       }
    }
    return true;
 }

function get_plaintext_pass(object_id) {
    try {
        in_pass = get_value(object_id);
        debug("in_pass:" + in_pass);
        if (in_pass.length<8) {
            alert("Password min len 8! - current len:" + in_pass.length);
            set_focus(object_id)
            return false;
        }

        if (check_ascii_only(in_pass) == false) {
            set_focus(object_id)
            return false;
        }
        return in_pass;
    } catch (e) {
        alert("get_plaintext_pass() error:" + e);
        return false;
    }
}

function make_SHA(txt) {
    try {
        debug("make_SHA(" + txt + "):");
        SHA_hexdigest = hex_sha1(txt); // from: sha.js
        len = SHA_hexdigest.length;
        if (len != HASH_LEN) {
            alert("make_SHA() error! wrong length:" + len);
            return false;
        }
        debug(SHA_hexdigest);
        return SHA_hexdigest;
    } catch (e) {
        alert("make_SHA() error:" + e);
        return false;
    }
}


/* ___________________________________________________________________________
 *  debugging:
 */

function init_debug() {
    /* Create a debug window, if it's not exists */
    try {
        if (debug_msg != true) { return; }
        try {
            if (debug_window) {
                return;
            }
        } catch (e) {}
        debug_window = window.open("", "Debug", "dependent=yes, resizable=yes, scrollbars=yes, width=350, height=400, top=1, left=" + window.outerWidth);

        debug_win = debug_window.document;
        debug_win.writeln("<style>* { font-size: 0.85em; }</style>");

        var now = new Date();
        now = now.toLocaleString();

        debug_win.writeln("<h1>JS Debug - "+now+":</h1>");
        debug_win.writeln("---[DEBUG START]---");
        debug_win.writeln("cookie:" + document.cookie +"<br />");
    } catch (e) {
        alert("init_debug() error:" + e);
    }
}


function debug(msg) {
    try {
        if (debug_msg != true) { return; }
        init_debug();
        debug_win.writeln(msg + "<br />");
        debug_window.focus();
        // scroll to the last lines
        debug_window.scrollBy(0, 1000);
    } catch (e) {
        alert("debug('"+msg+"') error:" + e);
    }
}


function debug_confirm() {
    try {
       if (debug_msg != true) { return; }
       debug_window.focus();
       debug_win.writeln("---[DEBUG END]---");
       alert("OK for closing the debug window.");
       debug_window.close();
       debug_window = false;
    } catch (e) {
        alert("debug_confirm() error:" + e);
    }
}