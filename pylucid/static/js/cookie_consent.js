$(document).ready(function () {

    if (document.cookie.indexOf('hidecookieconsent=1') != -1){
        $('#cookies-consent').hide();
    } else {
        $('#cookies-consent').show();
    }

    $('.cookies-ok').click(function(e){
        document.cookie = 'hidecookieconsent=1;path=/';
        $('#cookies-consent').slideUp();
    });

});
