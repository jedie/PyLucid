
// helper function for console logging
// set debug to true to enable debug logging
function log() {
	try {debug} catch (e) {debug=false};
    if (debug && window.console && window.console.log)
        window.console.log(Array.prototype.join.call(arguments,''));
}
log("pylucid_js_tools.js loaded.");


function OpenInWindow(link) {
    /*************************************************************************
	Open link in a new JavaScript window.
	Usage e.g.:
		<a href="/foobar/" onclick="return OpenInWindow(this);">foobar</a>
	Better usage:
		<a href="/foobar/" class="openinwindow">foobar</a>
	*************************************************************************/
    var url = $(link).attr("href");
    win = window.open(url, "", "width=900, height=760, dependent=yes, resizable=yes, scrollbars=yes");
    win.focus();
    return false;
}


function replace_complete_page(html) {
    // replace the complete page
    document.open() // no append available since it is closed
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
        replace_complete_page(data)
    } else {
        // log("put in #page_content:" + data);
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
        var org_title = $(this).attr("title");
		
        $(this).attr({
            onclick: "return OpenInWindow(this);",
            title: org_title + " (Opens in a new window)"
        });
    //$(this).append(" [^]")
    });
}




var MIN_ROWS = 5;
var MAX_ROWS = 25;
var MAX_LENGTH = 100;
var RESIZE_FACTOR = 1.3;

function activate_resize_textarea_buttons() {
    /*************************************************************************
     * textarea resize buttons
     */
    log("activate_resize_textarea_buttons()");
    $(".resize_textarea" ).click(function () {
        button_id = $(this).attr('id');
        //      log("Clicked on: " + button_id);
        var pos = button_id.indexOf("_");
        var action = button_id.slice(0, pos);
        var textarea_id = button_id.slice(pos+1, button_id.length);
        //      log("action:" + action);
        //      log("textarea id:" + textarea_id);
        var textarea = $("#"+textarea_id);
        var old_rows = textarea.attr("rows");
        
        var new_rows = false;
        if (action=="smaller") {
            if (old_rows<3) {
                log("no more smaller ;)")
                return;
            }
            new_rows = Math.floor(old_rows / RESIZE_FACTOR);
        }
        if (action=="bigger") {
            new_rows = Math.ceil(old_rows * RESIZE_FACTOR);
        }
        
        if (new_rows == false) {
            log("Error: Wrong textarea resize action:" + action);
            return;
        }
        //      log("old rows:" + old_rows + " - new rows:" + new_rows);
        textarea.animate({
            rows: new_rows
        }, 100 );
    });
}

jQuery(document).ready(function($) {
    activate_resize_textarea_buttons();
	
    /*************************************************************************
	 * replace the existing links with a "open in new window" link           */
    replace_openinwindow_links();
	
	
    /*************************************************************************
	 * Add a "open in new window" link after the existing normal link.
	 * usage:
	 * 		<a href="/foo" class="add_openinwindow">foo</a>
	 */
    $('a.add_openinwindow').each(function(){

        var url = $(this).attr("href");
        var org_title = $(this).attr("title");
		
        var new_link = ' <a href="'+url+'" onclick="return OpenInWindow(this);" title="'+org_title+' (Opens in a new window)">[^]</a>'
		
        $(this).after(new_link);
    })
    
    /*************************************************************************
	 * Resize all textareas
	 */
    $("textarea").each(function() {
        rows = this.value.split("\n").length;
        if (rows > MAX_ROWS) {
            rows = MAX_ROWS;
        }
        if (rows < MIN_ROWS) {
            rows = MIN_ROWS;
        }
        log("set textarea row to:" + rows)
        this.rows = rows;
    });
	
    /*************************************************************************
	 * resize input fields
	 */
    $(".pylucid_form input").each(function() {
        maxlength = $(this).attr("maxlength");
        if (maxlength<=0) {
            return;
        }
        if (maxlength > MAX_LENGTH) {
            maxlength = MAX_LENGTH;
        }
        this.size=maxlength;
    });

    /*************************************************************************
	 * hide/unhide form fieldset stuff.
	 */
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