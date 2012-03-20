
// helper function for console logging
// set debug to true to enable debug logging
function log() {
    if (typeof debug === 'undefined') {
        // debug variable is undefined -> no debugging.
        debug=false;
    }
    if (debug && window.console && window.console.log)
        window.console.log(Array.prototype.join.call(arguments,''));
}
log("pylucid_js_tools.js loaded.");


var load_normal_link=false; // global return value


function OpenInWindow(link) {
    /*************************************************************************
    Open link in a new JavaScript window.
    Usage e.g.:
        <a href="/foobar/" onclick="return OpenInWindow(this);">foobar</a>
    Better usage:
        <a href="/foobar/" class="openinwindow">foobar</a>
	  *************************************************************************/
    log("OpenInWindow()");
    var url = $(link).attr("href");
    log("url:" + url);
    
    window_name=url;
    window_name = window_name.indexOf('?') > -1 ? window_name.substr(0, window_name.indexOf('?')) : window_name;
    window_name = window_name.indexOf('#') > -1 ? window_name.substr(0, window_name.indexOf('#')) : window_name;
    log("window name:" + window_name);
    
    win = window.open(url, window_name, "width=900, height=760, dependent=yes, resizable=yes, scrollbars=yes");
    win.focus();
    return false;
}


function replace_complete_page(html) {
    // replace the complete page
    document.open(); // no append available since it is closed
    document.write(html);
    document.close();
}

function replace_page_content(data, textStatus) {
    /*************************************************************************
	ajax success "handler".
	replace the "#page_content" with the new html response data
	*************************************************************************/
    log("ajax post response success.");
    log("status:" + textStatus);
    if (data.indexOf("</body>") != -1) {
        // FIXME: We should find a way to handle a
        // redirect directly. But we always get the
        // html data of the redirected page.
		
        log("redirect work-a-round: replace the complete page");
		log(data);
        log("</body> index:" + data.indexOf("</body>"));
        replace_complete_page(data);
    } else {
        // log("put in #page_content:" + data);
		if ($("#page_content").length == 0) {
			msg = 'ajax view error:\n\n';
			msg += 'There is no CSS id="page_content" in your page template!\n\n';
			msg += 'more info at: http://www.pylucid.org/permalink/320/auth-plugin';
			log(msg);
		    alert(msg);
			$("body").html(data);
			return;
		}
        $("#page_content").html(data);
        $("#page_content").animate({
            opacity: 1
        }, 500 );
    }
    load_normal_link = false;
}


function ajax_error_handler(XMLHttpRequest, textStatus, errorThrown) {
    /*************************************************************************
	ajax error "handler".
	replace the complete page with the error text (django html traceback page)
	*************************************************************************/
    log("ajax get response error!");
    log(XMLHttpRequest);
    var response_text = XMLHttpRequest.responseText;
    log("response_text: '" + response_text + "'");
    if (!response_text) {
        response_text = "<h1>Ajax response error without any response text.</h1>";
		response_text += "<p>textStatus:" + textStatus + "</p>"
		response_text += "<p>errorThrown:" + errorThrown + "</p>"
		replace_page_content(response_text, textStatus);
		return
    }
    replace_complete_page(response_text);
    load_normal_link = true;
}



function pylucid_ajax_form_view(form_id) {
    /*************************************************************************
    PyLucid ajax form view.
    
    Don't send the form and get a complete new rendered page. Send the form
    via ajax post and replace the #page_content with the html response.
    
    usage e.g.:
    ----------------------------------------------------------------------
	    $(document).ready(function(){
	    	// simply bind the form with the id:
	        pylucid_ajax_form_view('#form_id');
	    });
    ----------------------------------------------------------------------
    *************************************************************************/
    $(form_id).bind('submit', function() {
        var form = $(this);
        log("pylucid_ajax_form_view submit form:" + form);
        
        $("#page_content").html('<h2>send...</h2>');
        $("#page_content").animate({
            opacity: 0.3
        }, 500 );
    
        var form_data = form.serialize();
        log("form data:" + form_data);
        
        var url = encodeURI(form.attr('action'));
        log("send form to url:" + url);
        
        load_normal_link = true;
        
        XMLHttpRequest = $.ajax({
            async: false,
            type: "POST",
            url: url,
            data: form_data,
            dataType: "html",
            
            success: replace_page_content,
            complete: function(XMLHttpRequest, textStatus){
                // Handle redirects
                log("complete:" + XMLHttpRequest);
                log("text:" + textStatus);
                log("complete:" + XMLHttpRequest.status);
                log("complete:" + XMLHttpRequest.getResponseHeader('Location'));
                
                if(XMLHttpRequest.status.toString()[0]=='3'){
                    top.location.href = XMLHttpRequest.getResponseHeader('Location');
                }
            },
            error: ajax_error_handler
        });
        log("ajax done:" + XMLHttpRequest);
        log("ajax done:" + XMLHttpRequest.status);
        log("ajax done:" + XMLHttpRequest.getResponseHeader('Location'));
        return load_normal_link; // <-- important: Don't send the form in normal way.
    });
}

function push_state(url, title) {
    /*************************************************************************
    try to add a history entry with HTML5
    
    see also:
    https://developer.mozilla.org/en/DOM/Manipulating_the_browser_history#The_pushState%28%29.C2.A0method
    *************************************************************************/
    if (typeof(title) === 'undefined') var title = "";
    
    if (window.history && window.history.pushState) {
        try {
            history.pushState(null, title, url);
        } catch (e) {
            log("Can't use history.pushState:" + e);
        }
    } else {
        log("No window.history.pushState :(");
        //document.location.href = url; // <<-- would load the page as ajax and normal!!!
    }
}

function get_pylucid_ajax_view(url) {
    /*************************************************************************
    PyLucid ajax get view replace.
    
    Don't render the complete page again. Simply get the new content via ajax
    and replace #page_content with it.
    
    usage e.g.:
    ----------------------------------------------------------------------
        $(document).ready(function(){
            $("#link_id").click(function(){
                return get_pylucid_ajax_view("{{ ajax_get_view_url }}");
            });
        });
    ----------------------------------------------------------------------
    or:
    ----------------------------------------------------------------------
    <a href="{{ url }}" onclick="return get_pylucid_ajax_view('{{ ajax_url }}');">foo</a>
    ----------------------------------------------------------------------
    *************************************************************************/
    $("#page_content").html('<h2>loading...</h2>');
    $("#page_content").animate({
        opacity: 0.3
    }, 500 );

    var url = encodeURI(url);
    log("get:" + url);

    load_normal_link = true;
    
    $.ajax({
        async: false,
        type: "GET",
        url: url,
        dataType: "html",
        
        success: replace_page_content,
        error: ajax_error_handler
    });
    if (debug) {
        // never fall back in debug mode.
        log("return: " + load_normal_link);
        return false;
    } else {
        // fall back to normal view, if ajax request failed.
        return load_normal_link; // The browser follow the link, if true
    }    
}


function replace_openinwindow_links() {
    /*************************************************************************
    * replace the existing links with a "open in new window" link
    * usage:
    * 		<a href="/foo" class="openinwindow">foo</a>
    */
    $('a.openinwindow').each(function(){
        var url = $(this).attr("href");
        log("replace openinwindow for:" + url);
        var org_title = $(this).attr("title");
        
        $(this).attr('target', '_blank'); // fall-back
        
        $(this).click(function() {
           return OpenInWindow(this);
        });
    });
}
function add_openinwindow_links() {
    /*************************************************************************
     * Add a "open in new window" link after the existing normal link.
     * usage:
     *      <a href="/foo" class="add_openinwindow">foo</a>
     */
    $('a.add_openinwindow').each(function(){

        var url = $(this).attr("href");
        var org_title = $(this).attr("title");
        
        var new_link = ' <a href="'+url+'" onclick="return OpenInWindow(this);" target="_blank" title="'+org_title+' (Opens in a new window)">[^]</a>'
        
        $(this).after(new_link);
    })
}

/*****************************************************************************
* content/markup stuff
*/
var wysiwyg_used = false;
function process_markup() {
  markup_id = $('#id_markup').val();
  log("markup:" + markup_id);
  if (wysiwyg_used == false && markup_id == "1") {
    log("init wysiwyg");
    try {
        $('#id_content').wysiwyg({controls: {html: { visible : true }}});
    } catch (e) {
        log("Error:" + e);
        log("Info: The page template must include jquery.wysiwyg.js!")
    }
    wysiwyg_used = true;
    
  }
  if (wysiwyg_used == true && markup_id != "1") {
    log("destroy wysiwyg");
    try {
        $('#id_content').wysiwyg('destroy');
    } catch (e) {
        log("error on destroy:" + e);
        log("See: http://github.com/akzhan/jwysiwyg/issues#issue/11");
    }
    wysiwyg_used = false;
  }

  // markup_help_url was set in apps/pylucid/templates/admin/base_site.html
  $("a.markuphelp").each(function(index) {
      // update the markup help button, to display the right help page
      if (markup_id) {
          $(this).attr("href", markup_help_url+"?markup_id="+markup_id);
      } else {
          $(this).attr("href", markup_help_url);
      }    
      log("set markup help url " + index + ' to: ' + $(this).attr("href"));
  });
  

}
function setup_markup() {
    log("setup_markup()");   
    process_markup();
    $('#id_markup').change(process_markup);
}


/*****************************************************************************
* PyLucid comments stuff
*/
var pylucid_comments_preview = false;
function submit_comments_form() {
    log("submit: comment form");
    
    $("#comments_commit_status").slideDown();
    $("#comment_form_div").fadeTo(0.5);
    
    var form_data = $("#comment_form").serialize();
    if (pylucid_comments_preview == true) {
      form_data += "&preview=On";
    }
    log("form data:" + form_data);
    
    $.ajax({
        type: "POST",
        url: "?pylucid_comments=submit",
        data: form_data,
        dataType: "html",
        success: function(data, textStatus) {
            log("Success");
            log("textStatus:" + textStatus);
            //log("data:" + data);
            if (data=="reload") {
                // Reload the current page, after the comment was saved
                log("should reload.");
                log("Cookie:"+document.cookie);
                location.reload();
            }
            log("replace old form");
            insert_comments_form(data);
            $("#comment_form_div").fadeTo(1);
        },
        error: ajax_error_handler // from pylucid_js_tools.js
    });
}
function insert_comments_form(html) {
    log("insert_comments_form()");
    $("#comment_form_div").html(html);
    $("#comments_commit_status").slideUp();
    
    pylucid_comments_preview = false;
    $("#comment_form").bind('submit', submit_comments_form);
    $("input[name=preview]").click(function() {
        log("preview clicked.");
        pylucid_comments_preview = true;
    });
}
function get_pylucid_comments_form() {
    log("get_pylucid_comments_form()");
    
    $("#leave_comment_link").slideUp();
    $("#comments_commit_status").slideDown();
    
    var post_data = "content_type=";
    post_data += $("input#id_content_type").val();
    post_data += "&object_pk="
    post_data += $("input#id_object_pk").val();
    log("post_data:"+post_data);

    $.ajax({
        async: false,
        type: "GET",
        url: "?pylucid_comments=get_form",
        data: post_data,
        dataType: "html",
        success: function(data, textStatus) {
            log("Success");
            log("textStatus:" + textStatus);
            insert_comments_form(data);
            $("#comment_form_div").slideDown();
        },
        error: ajax_error_handler
    });

}


/*****************************************************************************
* Django CSRF exception for AJAX requests
* code from: http://docs.djangoproject.com/en/dev/ref/contrib/csrf/#ajax
* see also: http://docs.djangoproject.com/en/dev/releases/1.3/#csrf-exception-for-ajax-requests
*/
jQuery(document).ajaxSend(function(event, xhr, settings) {
    log("ajax send...");
    
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    function sameOrigin(url) {
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }
    function safeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
        log("set X-CSRFToken to:"+ getCookie('csrftoken'));
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    }
});


/****************************************************************************/

var MIN_ROWS = 1;
var MAX_ROWS = 25;

function set_textarea_size(textarea) {
    rows = textarea.attr("value").split("\n").length;
    
    if (rows > MAX_ROWS) { rows = MAX_ROWS; }
    if (rows < MIN_ROWS) { rows = MIN_ROWS; }

    log("set textarea "+textarea.id+" row to:" + rows);
    
    textarea.css("height", "auto");
    textarea.attr("rows", rows);
}

/****************************************************************************/


var MAX_LENGTH = 255;


jQuery(document).ready(function($) {
    log("run pylucid_js_tools.js init...");
    /************************************************************************
	 * replace the existing links with a "open in new window" link          */
    replace_openinwindow_links();
	
    /************************************************************************
	 * Add a "open in new window" link after the existing normal link.      */
    add_openinwindow_links()
    
    /************************************************************************
     * setup markup choice field and markup help                            */
    if ( $('#id_markup').length ) { setup_markup() }
    
    /************************************************************************
	 * Resize all textareas                                                 */
    $("textarea").each(function() {
		set_textarea_size($(this));
		
		$(this).bind("keyup", function(event) {
			var k = event.keyCode 
			//log("key code: " + k);
			/*
			 * 13 == Enter
			 * 8  == backspace
			 * 46 == delete
			 * 17 == Control (for copy&paste: ctrl-c, ctrl-v)
			 */
			if (k==13 || k==8 || k==46 || k==17) {
				set_textarea_size($(this));
			}
		});
    });
	
    /************************************************************************
	 * resize input fields                                                  */
    $(".pylucid_form input").each(function() {
        maxlength = $(this).attr("maxlength");
        if (maxlength == undefined || maxlength<=0) {
            return;
        }
        if (maxlength > MAX_LENGTH) {
            maxlength = MAX_LENGTH;
        }
        try {
            this.size=maxlength;
        } catch (e) {
            log("Can't resize input field to '"+maxlength+"':" + e);
        }
    });

    /************************************************************************
	 * hide/unhide form fieldset stuff.                                     */
    $(".pylucid_form .form_hide").nextAll().hide();
    $(".pylucid_form .form_collapse").each(function() {
        $(this).css("cursor","n-resize");
    });
    $(".pylucid_form .form_collapse").click(function () {
        if ($(this).css("cursor") == "n-resize") {
            $(this).css("cursor","s-resize");
        } else {
            $(this).css("cursor","n-resize");
        }
        $(this).nextAll().slideToggle("fast");
    });
	
});