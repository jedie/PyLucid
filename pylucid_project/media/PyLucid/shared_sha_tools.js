/* ___________________________________________________________________________
 *  Some needed stuff round the SHA-JS-Login
 */

function is_only_ascii(data) {
    // Check if the given string contains only ASCII characters
    for (var i = 1; i <= data.length; i++) {
       if (data.charCodeAt(i) > 127) {
            return false;
       }
    }
    return true;
}

function sha_hexdigest(txt) {
    // build the SHA hexdigest from the given string. Return false is anything is wrong.
    try {
        log("sha_hexdigest('" + txt + "'):");
        SHA_hexdigest = hex_sha1(txt); // from: sha.js
        len = SHA_hexdigest.length;
        if (len != HASH_LEN) {
            page_msg_error("sha_hexdigest() error! wrong length:" + len);
            return false;
        }
        log(SHA_hexdigest);
        return SHA_hexdigest;
    } catch (e) {
        page_msg_error("sha_hexdigest() error:" + e);
        return false;
    }
}

function _page_msg(msg){
    $("#js_page_msg").html(msg).css("display", "block").slideDown();
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