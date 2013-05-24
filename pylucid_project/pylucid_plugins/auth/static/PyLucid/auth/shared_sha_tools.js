/*
    PyLucid shared_sha_tools.js
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    A secure JavaScript SHA-1 AJAX Login.
    
    :copyleft: 2007-2013 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
*/


try {
    jQuery(document);
    log("jQuery loaded, ok.");
} catch (e) {
    alert("Error, jQuery JS not loaded!\n Original error was:" + e);
}


function _page_msg(msg){
    $("#js_page_msg").html(msg).slideDown().css("display", "block");
}
function page_msg_error(msg) {
    $("#js_page_msg").removeClass("page_msg_info page_msg_success").addClass("page_msg_error");
    _page_msg(msg);
}
function page_msg_success(msg) {
    $("#js_page_msg").removeClass("page_msg_info page_msg_success").addClass("page_msg_success");
    _page_msg(msg);    
}
function page_msg_info(msg) {
    $("#js_page_msg").removeClass("page_msg_success page_msg_error").addClass("page_msg_info");
    _page_msg(msg);    
}


function low_level_error(msg) {
    log(msg);
    $("#page_content").html("<"+"h2>" + msg + "<"+"/h2>");
    alert(msg);
    return false;
}


function assert_is_number(value, name) {
    if(value=="") {
        throw "Variable '"+name+"' from server is a empty string!";
    }
    if(isNaN(value)) {
        throw "Variable '"+name+"' from server is not a number! It's: ["+value+"]";
    }
    log("assert_is_number for '"+name+"', ok (value="+value+")");
}


function assert_only_ascii(data) {
    // Check if the given string contains only ASCII characters
    for (var i = 1; i <= data.length; i++) {
        var char_code=data.charCodeAt(i)
        if (char_code > 127) {
            throw "Error: non ASCII caracter '"+data.substr(i,1)+"' (unicode no. "+char_code+") in '"+data+"'!";
        }
    }
}


function assert_csrf_cookie() {
    // Check if Cross Site Request Forgery protection cookie exists
    if ((typeof document.cookie === 'undefined') || (document.cookie.indexOf("csrftoken") == -1)) {
        try {
            log("Cookies: " + document.cookie);
        } catch (e) {
            log("Error:" + e);
        }
        throw "Error: Cookies not set. Please enable cookies in your browser!";
    } else {
        log("cookie check, ok.");
    }
}


function assert_challenge() {
    // Check variable that set in sha_form.html via template variables
    if (typeof challenge === 'undefined') {
        throw "Error: 'challenge' not defined!";
    }
}


function assert_length(value, must_length, name) {
    if (value.length != must_length) {
        throw "Error: '"+name+"' has wrong length:" + value.length + "!=" + must_length;
    } else {
        log("assert length of '"+name+"', ok (length == "+value.length+")");
    }
}

function assert_min_length(value, min_length, name) {
    if (value.length < min_length) {
        var msg="Error: '"+name+"' is too short. It must be at least "+min_length+" characters long.";
        log(msg);
        throw msg;
    } else {
        log("assert min length of '"+name+"', ok (length == "+value.length+" < "+min_length+")");
    }    
}

function assert_salt_length(value) {
    var salt_length = value.length 
    if (salt_length == OLD_SALT_LEN) {
        log("WARNING: Salt '"+value+"' has old "+salt_length+" length.");
        return
    }
    if (salt_length != SALT_LEN) {
        throw "Error: Salt '"+value+"' has wrong length:" + salt_length;
    } else {
        log("assert length of salt '"+value+"', ok (length == "+salt_length+")");
    }
}

//-----------------------------------------------------------------------------

function generate_nonce(start_value) {
    // Generate new 'cnonce' a client side random value
    var cnonce = start_value;
    cnonce += new Date().getTime();
    cnonce += Math.random();
    cnonce += $(window).height();
    cnonce += $(window).width();
    //cnonce = "Always the same, test.";
    log("generated cnonce from:" + cnonce);
    cnonce = sha_hexdigest(cnonce);
    log("SHA cnonce:" + cnonce);
    return cnonce
}

function sha_hexdigest(txt) {
    /*
        build the SHA hexdigest from the given string. Return false is anything is wrong.
    */
    log("sha_hexdigest('" + txt + "'):");
    SHA_hexdigest = hex_sha1(txt); // from: sha.js
    assert_length(SHA_hexdigest, HASH_LEN, "SHA_hexdigest");
    log(SHA_hexdigest);
    return SHA_hexdigest;
}


function calculate_hashes(password, salt, challenge) {
    log("calculate_hashes with salt '"+salt+"' (length:"+salt.length+") and challenge '"+challenge+"' (length:"+challenge.length+")");
    
    assert_salt_length(salt);
    assert_length(challenge, HASH_LEN, "challenge");
    
    log("shapass = sha_hexdigest(salt + password):");
    var shapass = sha_hexdigest(salt + password);
    if (shapass.length!=HASH_LEN) {
        var msg = gettext("Internal error: hex_sha salt error! shapass length:") + shapass.length;
        log(msg);
        throw msg;
    }

    // split SHA-Passwort
    sha_a = shapass.substr(0, HASH_LEN/2); // sha_a never send to the server
    sha_b = shapass.substr(HASH_LEN/2, HASH_LEN/2);
    log("substr: sha_a:|"+sha_a+"| sha_b:|"+sha_b+"|");   

    var cnonce = generate_nonce("PyLucid JS-SHA-Login");

    log("Build "+LOOP_COUNT+"x SHA1 from: sha_a + i + challenge + cnonce");
    for (i=0; i<LOOP_COUNT; i++)
    {
        //log("sha1 round: " + i);
        sha_a = sha_hexdigest(sha_a + i + challenge + cnonce);
    }
    
    return {
        "sha_a": sha_a,
        "sha_b": sha_b,
        "cnonce": cnonce,
    }
}

function calculate_salted_sha1(password) {
    /*
        Generate the Django password hash
        currently we only generated the salted SHA1 hash
        see: hashers.SHA1PasswordHasher()
        
        TODO:
        Use http://code.google.com/p/crypto-js/
        to support hashers.PBKDF2PasswordHasher() in JS Code
    */
    log("calculate_salted_sha1():");
   
    log("Generate salt with a length of:"+SALT_LEN);
   
    var cnonce = generate_nonce("django hash");
    var salt = cnonce.substr(0, SALT_LEN);
    log("salt to use: ["+salt+"] (length:"+salt.length+")");
    assert_length(salt, SALT_LEN, "salt");
    
    var sha1hash = sha_hexdigest(salt + password);
    log("salted SHA1 hash: ["+sha1hash+"] (length:"+sha1hash.length+")");
    assert_length(sha1hash, HASH_LEN, "sha1hash");

    return {
        "salt": salt,
        "sha1hash": sha1hash,
    }
}

//-----------------------------------------------------------------------------


function test_sha_js() {
    // Check the sha1 functions from external js files
    
    log("Check the sha1 functions...");
    
    if (typeof hex_sha1 === 'undefined') {
        throw "Error:\nsha.js not loaded.\n(hex_sha1 not defined)";
    }

    if (typeof sha_hexdigest === 'undefined') {
        throw "Error:\nWrong shared_sha_tools.js loaded! Please update your static files\n(sha_hexdigest not defined)";
    }
    
    var digits="0123456789";
    var ascii_lowercase = "abcdefghijklmnopqrstuvwxyz".toLowerCase();
    var ascii_uppercase = ascii_lowercase.toUpperCase();
    var test_string = " " + digits + ascii_lowercase + ascii_uppercase;
    var test_sha = sha_hexdigest(test_string);
    var should_be = "5b415e2e5421a30b798c9b46638fcd7b58ff4d53".toLowerCase();
    if (test_sha != should_be) {
        throw "sha.js test failed!\n'" + test_sha + "' != '" + should_be + "'";
    }
    log("Check the sha1 functions is ok.");
}


function precheck_sha_login() {
    assert_csrf_cookie() // Check if Cross Site Request Forgery protection cookie exists
    assert_challenge() // Check variable that set in sha_form.html by template variables
        
    assert_is_number(OLD_SALT_LEN, "OLD_SALT_LEN");
    assert_is_number(SALT_LEN, "SALT_LEN");
    assert_is_number(HASH_LEN, "HASH_LEN");
    assert_is_number(LOOP_COUNT, "LOOP_COUNT");
    
    assert_length(challenge, HASH_LEN, "challenge");
    
    test_sha_js(); // Check the sha1 functions from external js files
}


//-----------------------------------------------------------------------------


function init_pylucid_sha_login() {
    /*
        SHA-JS-Login
        init from auth/sha_form.html
    */
    log("shared_sha_login.js - init_pylucid_sha_login()");
    
    try {
        precheck_sha_login()
    } catch (e) {
        low_level_error(e);
        return false;
    }

    log("unhide form");
    $("#login_form").css("display", "block").slideDown();

    $("#id_username").focus();

    // remove old page_msg, if exist
    $("#page_msg").slideUp();

    $("#id_username").change(function() {
        // if the username change, we must get a new salt from server.
        $("#id_password").focus();
        $("#js_page_msg").slideUp();
        log("username changed, delete old salt.");
        salt="";
        return false;
    });

    $("input").change(function() {
        // hide old JS messages, if a input field changed
        $("#js_page_msg").slideUp(50);
    });

    $("#login_form").submit(function() {
        $("#js_page_msg").slideUp(50); // hide old JS messages
        log("check login form.");
        try {
            var username = $("#id_username").val();
            log("username:" + username);

            if (username.length<2) {
                log("username to short, current len:" + username.length);
                page_msg_error(gettext("Username is too short."));
                $("#id_username").focus();
                return false;
            }

            var password = $("#id_password").val();
            log("password:" + password);

            try {
                assert_min_length(password, 8, "password");
            } catch (e) {
                log(e);
                page_msg_error(gettext("Password is too short. It must be at least eight characters long."));
                $("#id_password").focus();
                return false;
            }
            
            try {
                assert_only_ascii(password)
            } catch (e) {
                log(e);
                page_msg_error(gettext("Only ASCII letters in password allowed!"));
                $("#id_password").focus();
                return false;
            }

            if (salt=="") {
                page_msg_info(gettext("Get the hash salt value from server..."));
                var post_data = {
                    "username": username
                };
                log("get user salt from server, send POST:" + $.param(post_data));
                response = $.ajax({
                    async: false,
                    type: "POST",
                    url: get_salt_url,
                    data: post_data,
                    dataType: "text",
                    success: function(data, textStatus, XMLHttpRequest){
                        log("get salt value via ajax: " + textStatus);
                    },
                    error: ajax_error_handler // from pylucid_js_tools.js
                });
                salt = response.responseText;
                log("salt value from server:" + salt);
            } else {
                log("use existing salt:" + salt);
            }
            try {
                assert_salt_length(salt);
            } catch (e) {
                log(e);
                alert("Internal error: Wrong salt length:" + salt.length + "!=" + SALT_LEN);
                return false;
            }

            try {
                var results=calculate_hashes(password, salt, challenge);
            } catch (e) {
                alert(e);
                return false;
            }
            var sha_a=results.sha_a;
            var sha_b=results.sha_b;
            var cnonce=results.cnonce;
            log("sha_a:"+sha_a);
            log("sha_b:"+sha_b);
            log("cnonce:"+cnonce);
            

            // display SHA values
            $("#password_block").slideUp(1).delay(500);
            $("#sha_values_block").css("display", "block").slideDown();
            $("#id_password").val(""); // 'delete' plaintext password
            $("#id_sha_a").val(sha_a);
            $("#id_sha_b").val(sha_b);
            $("#id_cnonce").val(cnonce);

            var post_data = {
                "username": username,
                "sha_a": sha_a, "sha_b": sha_b,
                "cnonce": cnonce
            }
            log("auth user, send POST:" + $.param(post_data));
            page_msg_info(gettext("Send SHA-1 values to the server..."));
            response = $.ajax({
                async: false,
                type: "POST",
                url: sha_auth_url,
                data: post_data,
                dataType: "text",
                success: function(data, textStatus, XMLHttpRequest){
                    log("post request via ajax: " + textStatus);
                },
                error: ajax_error_handler // from pylucid_js_tools.js
            });
            msg = response.responseText;
            log("responseText:" + msg);
            if (msg=="OK") {
                 // login was ok
                 page_msg_success(gettext("Login ok, loading..."));
                 $("#id_password").remove();
                 window.location.href = next_url;
                 return false;
            }
            if (msg.indexOf("<"+"head>") != -1) { // 'mask' tag, so it's not found by pylucid_js_tools.js / replace_page_content ;)
                log("It seems we get a complete html page: replace the complete page");
                $("html").html(msg);
//                replace_complete_page(msg); // from pylucid_js_tools.js
                return false;
            }
            if (msg.indexOf(";") == -1) {
                log("Wrong server reponse! No ';' found!");
                return false;
            }         

            // we get a new challenge and a error message from server
            challenge = msg.substr(0, msg.indexOf(";"));
            msg = msg.substr(msg.indexOf(";")+1);

            log("new challenge:" + challenge);
            page_msg_error(msg);

            $("#password_block").css("display", "block").slideDown();
            $("#sha_values_block").slideUp("slow");
            $("#id_sha_a").val("");
            $("#id_sha_b").val("");
            $("#id_cnonce").val("");
            $("#id_password").focus();
        } catch (e) {
            log("Error:" + e);
            alert("internal javascript error:" + e);
        }
        return false;
    });
    $("#load_info").slideUp();
}


//-----------------------------------------------------------------------------

function change_password_submit() {
    /*
    calculate the hashes from the passwords and insert only them into
    the form and remove the plaintext passwords.
    */
    log("check change password form.");
    
    var old_password = $("#id_old_password").val();
    log("old_password:" + old_password);
    
    var new_password1 = $("#id_new_password1").val();
    log("new_password1:" + new_password1);
    
    var new_password2 = $("#id_new_password2").val();
    log("new_password2:" + new_password2);
    
    try {
        assert_min_length(old_password, 8, "old password");
    } catch (e) {
        page_msg_error(e);
        $("#id_old_password").focus();
        return false;
    }
    
    try {
        assert_min_length(new_password1, 8, "new password");
    } catch (e) {
        page_msg_error(e);
        $("#id_new_password1").focus();
        return false;
    }
    
    try {
        assert_only_ascii(old_password)
    } catch (e) {
        log(e);
        page_msg_error(gettext("Error: Old password contains non ASCII letters!"));
        $("#id_old_password").focus();
        return false;
    }
    
    try {
        assert_only_ascii(new_password1)
    } catch (e) {
        log(e);
        page_msg_error(gettext("Error: New password contains non ASCII letters!"));
        $("#id_new_password2").val("");
        $("#id_new_password1").focus();
        return false;
    }
    
    if (new_password1 != new_password2) {
        msg = gettext("The two password fields didn't match.")
        log(msg + " -> " + new_password1 + " != " + new_password2);
        page_msg_error(msg);
        $("#id_new_password2").focus();
        return false;
    }
    
    if (new_password1 == old_password) {
        var result=confirm("The new password is the same as the old password.");
        if (result != true) {
            return false
        }
    }
    
    // display SHA values
    $("#password_block").slideUp(1).delay(500);
    $("#sha_values_block").css("display", "block").slideDown();
    
    try {
        var results=calculate_hashes(old_password, sha_login_salt, challenge);
    } catch (e) {
        alert(e);
        return false;
    }
    var sha_a=results.sha_a;
    var sha_b=results.sha_b;
    var cnonce=results.cnonce;
    log("sha_a:"+sha_a);
    log("sha_b:"+sha_b);
    log("cnonce:"+cnonce);
   
    // old password "JS-SHA1" values for pre-verification
    $("#id_sha_a").val(sha_a);
    $("#id_sha_b").val(sha_b);
    $("#id_cnonce").val(cnonce);
            
    $("#id_old_password").val(""); // 'delete' plaintext password
    $("#id_old_password").remove();
    
    var salted_hash=calculate_salted_sha1(new_password1);
    var salt=salted_hash.salt;
    var sha1hash=salted_hash.sha1hash;
    log("new salted hash:");
    log("salt: "+salt+" (length:"+salt.length+")");
    log("sha1hash: "+sha1hash+" (length:"+sha1hash.length+")");
   
    // new password as salted SHA1 hash:
    $("#id_salt").val(salt);
    $("#id_sha1hash").val(sha1hash);

    $("#id_new_password1").val(""); // 'delete' plaintext password
    $("#id_new_password1").remove();
    $("#id_new_password2").val(""); // 'delete' plaintext password
    $("#id_new_password2").remove();

}

function init_JS_password_change() {
    /*
        change user password
        init from auth/JS_password_change.html
    */
    log("shared_sha_login.js - init_JS_password_change()");
    
    try {
        precheck_sha_login();
        
        // unlike normal login, we have the salt directly, set in template
        assert_salt_length(sha_login_salt)
    } catch (e) {
        log(e);
        alert("Error:" + e);
        return false;
    }
    
    $("#id_old_password").focus();
    
    $("input").change(function() {
        // hide old JS messages, if a input field changed
        $("#js_page_msg").slideUp(50);
    });
    
    $("#change_password_form").submit(function() {
        $("#js_page_msg").slideUp(50); // hide old JS messages
        try {
            return change_password_submit();
        } catch (e) {
            log(e);
            alert("Error:" + e);
            return false;
        }
        //return confirm("Send?");
    });
    $("#load_info").slideUp();
}
