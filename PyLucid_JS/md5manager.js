
notchecked = true;

function plaintextlogin() {
    check = confirm("!!!WARNING!!!\n\nSend Password in Plain-Text???\n\n(For security: Use md5-LogIn!)");
    if (check == true) {
        document.login.submit();
    }
}

function md5login() {
    if (!document.getElementsByName) { alert("Your Browser is not supported!"); return; }

    rnd = document.getElementsByName("rnd")[0].value;
    if ( rnd=="" ) { alert("rnd from Server fail!"); return; }

    in_pass = document.getElementsByName("pass")[0].value;
    if (in_pass.length<8) { alert("Password min len 8!"); return; }

    pass1 = in_pass.slice(0, 4);
    pass2 = in_pass.slice(4, in_pass.length) + rnd;

    pass1 = MD5( pass1 );
    if ( pass1.length != 32 ) { alert("MD5js error!"); return; }

    pass2 = MD5( pass2 );
    if ( pass2.length != 32 ) { alert("MD5js error!"); return; }

    document.getElementsByName("md5pass1")[0].value = pass1;
    document.getElementsByName("md5pass2")[0].value = pass2;

    document.getElementsByName("pass")[0].value = "";

    if ( in_pass == document.getElementsByName("pass")[0].value ) {
        alert("JavaScipt error!");
        return;
    }

    document.getElementsByName("use_md5login")[0].value = "1";

    document.login.submit();
}
