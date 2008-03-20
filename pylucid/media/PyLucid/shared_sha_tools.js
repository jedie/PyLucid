/* ___________________________________________________________________________
 *  Some needed stuff round the SHA-JS-Login
 */

check_ok = false;
debug_msg = false;

// length of a SHA1 hexdigest string:
HASH_LEN = 40;


if (!document.getElementById) {
    alert("Error: Your Browser is not supported!");
}

if (navigator.cookieEnabled) {
    if (navigator.cookieEnabled != true) {
        alert("You must enable Cookies in your Browser!");
    }
}

/* ___________________________________________________________________________
 *  needfull functions:
 */

function set_focus(object_id) {
    try {
        debug("set focus on id:" + object_id);
        document.getElementById(object_id).focus();
    } catch (e) {
        alert("set_focus() error:" + e);
    }
}

function hide_by_id(object_id) {
    try {
        obj = document.getElementById(object_id);
        obj.style.display = 'none';
    } catch (e) {
        alert("hide_by_id() error:" + e);
    }
}
function unhide_by_id(object_id) {
    try {
        obj = document.getElementById(object_id);
        obj.style.display = 'block';
    } catch (e) {
        alert("unhide_by_id() error:" + e);
    }
}

function change_color(id_name, color_name) {
    try {
        obj = document.getElementById(id_name);
    } catch (e) {
        alert("change_color() error can't get object:" + e);
    }
    try {
        obj.style.backgroundColor = color_name;
    } catch (e) {
        alert("change_color() error can't change background color:" + e);
    }
}

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
        in_pass = document.getElementById(object_id).value;
        debug("in_pass:" + in_pass);
        if (in_pass.length<8) {
            alert("Password min len 8! - current len:" + in_pass.length);
            return false;
        }

        if (check_ascii_only(in_pass) == false) {
            return false
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

function set_value(object_id, value, color_name) {
    try {
        // set the value and change the css color.
        document.getElementById(object_id).value = value;
        change_color(object_id, color_name);
    } catch (e) {
        alert("set_value("+object_id+", "+value+", "+color_name+") error:" + e);
    }
}

/* ___________________________________________________________________________
 *  debugging:
 */

function init_debug() {
    try {
        if (debug_msg != true) { return; }
        property = "dependent=yes,resizable=yes,width=350,height=400,top=1,left=" + window.outerWidth;
        debug_window = window.open("about:blank", "Debug", property);
        debug_window.focus();
        debug_win = debug_window.document;
        debug_win.writeln("<style>* { font-size: 0.85em; }</style>");
        debug_win.writeln("<h1>JS Debug:</h1>");
        debug_win.writeln("---[DEBUG START]---");
        debug_win.writeln("cookie:" + document.cookie +"<br />");

        document.body.onunload = "debug_window.close();";
    } catch (e) {
        alert("init_debug() error:" + e);
    }
}
function debug(msg) {
    try {
        if (debug_msg != true) { return; }
        debug_win.writeln(msg + "<br />");
    } catch (e) {
        alert("debug() error:" + e);
    }
}
function debug_confirm() {
    try {
       if (debug_msg != true) { return; }
       debug_window.focus();
       debug_win.writeln("---[DEBUG END]---");
       alert('OK for submit.');
       debug_window.close();
    } catch (e) {
        alert("debug_confirm() error:" + e);
    }
}