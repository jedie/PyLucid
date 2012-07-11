try {
    jQuery(document);
    log("jQuery loaded, ok.");
} catch (e) {
    alert("Error, jQuery JS not loaded!\n Original error was:" + e);
}
function low_level_error(msg) {
    log(msg);
    $("#page_content").html("<"+"h2>" + msg + "<"+"/h2>");
    alert(msg);
    return false;
}
jQuery(document).ready(function($) {
    log("sha_login.js - document ready");
    
    // Check if Cross Site Request Forgery protection cookie exists
    if ((typeof document.cookie === 'undefined') || (document.cookie.indexOf("csrftoken") == -1)) {
        try {
            log("Cookies: " + document.cookie);
        } catch (e) {
            log("Error:" + e);
        }
        msg = "Error: Cookies not set. Please enable cookies in your browser!";
        low_level_error(msg);
        return false;
    } else {
        log("cookie check, ok.");
    }
    
    // Check variabled that set in sha_form.html by template variables:
    if (typeof challenge === 'undefined') {
        msg = "Error: 'challenge' not defined!";
        low_level_error(msg);
        return false;
    }
    log("challenge:" + challenge);
    log("SALT_LEN:" + SALT_LEN);
    log("HASH_LEN:" + HASH_LEN);
    if (challenge.length != SALT_LEN) {
        msg = "Wrong challenge from server length:" + challenge.length + "!=" + SALT_LEN;
        low_level_error(msg);
        return false;
    } else {
        log("salt length test, ok.");
    }

    // Check functions from shared_sha_tools.js and sha.js
    if (typeof hex_sha1 === 'undefined') {
        msg = "Error:\nsha.js not loaded.\n(hex_sha1 not defined)";
        low_level_error(msg);
        return false;
    } else {
        log("hey_sha1, ok.");
    }

    if (typeof sha_hexdigest === 'undefined') {
        msg = "Error:\nWrong shared_sha_tools.js loaded! Please update your static files\n(sha_hexdigest not defined)";
        low_level_error(msg);
        return false;
    } else {
        log("sha_hexdigest, ok.");
    }

    log("unhide form");
    $("#login_form").css("display", "block").slideDown();
    $("#load_info").slideUp();

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

    $("#id_password").change(function() {
        $("#js_page_msg").slideUp(); // hide old messages
    });

    $("#login_form").submit(function() {
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

            if (password.length<8) {
                log("password to short, current len:" + password.length);
                page_msg_error(gettext("Password is too short. It must be at least eight characters long."));
                $("#id_password").focus();
                return false;
            }
            if (is_only_ascii(password) != true) {
                page_msg_error(gettext("Only ASCII letters in password allowed!"));
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
            if (salt.length != SALT_LEN) {
                alert("Internal error: Wrong salt length:" + salt.length + "!=" + SALT_LEN);
                return false;
            }

            log("shapass = sha_hexdigest(salt + password):");
            shapass = sha_hexdigest(salt + password);
            if (shapass == false) { return false; }
            if (shapass.length!=HASH_LEN) {
                alert(gettext("Internal error: hex_sha salt error! shapass length:") + shapass.length);
                return false;
            }

            // split SHA-Passwort
            sha_a = shapass.substr(0, HASH_LEN/2); // sha_a never send to the server
            sha_b = shapass.substr(HASH_LEN/2, HASH_LEN/2);
            log("substr: sha_a:|"+sha_a+"| sha_b:|"+sha_b+"|");

//            // Generate 'cnonce' a client side random value
//            var cnonce = "";
//            cnonce += new Date().getTime();
//            cnonce += Math.random();
//            cnonce += $(window).height();
//            cnonce += $(window).width();
//            log("generated cnonce:");
//            cnonce = sha_hexdigest(cnonce);

            log("sha_a2 = sha_hexdigest(challenge + sha_a):");
            sha_a2 = sha_hexdigest(challenge + sha_a);
            if (sha_a2 == false) { return false; }

            // display SHA values
            $("#password_block").slideUp(1).delay(500);
            $("#sha_values_block").css("display", "block").slideDown();
            $("#id_password").val(""); // 'delete' plaintext password
            $("#id_sha_a2").val(sha_a2);
            $("#id_sha_b").val(sha_b);

            var post_data = {
                "username": username, "sha_a2": sha_a2, "sha_b": sha_b
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
            $("#id_sha_a2").val("");
            $("#id_sha_b").val("");
            $("#id_password").focus();

            return false;
        } catch (e) {
            log("Error:" + e);
            alert("internal javascript error:" + e);
            return false;
        }
    });
    log("test sha.js");
    var digits="0123456789";
    var ascii_lowercase = "abcdefghijklmnopqrstuvwxyz".toLowerCase();
    var ascii_uppercase = ascii_lowercase.toUpperCase();
    var test_string = " " + digits + ascii_lowercase + ascii_uppercase;
    var test_sha = sha_hexdigest(test_string);
    var should_be = "5b415e2e5421a30b798c9b46638fcd7b58ff4d53".toLowerCase();
    if (test_sha != should_be) {
        var msg = "sha.js test failed!\n'" + test_sha + "' != '" + should_be + "'";
        log(msg);
        alert("Internal Error:\n" + msg);
        return false;
    }
    log("sha.js is ok");
});