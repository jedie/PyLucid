

// helper function for console logging
// set debug to true to enable debug logging
function log() {
    if (debug && window.console && window.console.log)
    	window.console.log(Array.prototype.join.call(arguments,''));
};


function OpenInWindow(URL) {
    // Open links in a JavaScript window
    win = window.open(URL, "", "width=900, height=760, dependent=yes, resizable=yes, scrollbars=yes");
    win.focus();
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
        
        $("#page_content").html('<h2>loading...</h2>');
        $("#page_content").animate({opacity: 0.3}, 500 );

        var form = $(this);
        var form_data = form.serialize();
        log("form data:" + form_data);
        
        var url = encodeURI(form.attr('action'));
        log("send form to url:" + url);
        
        var load_normal_link = true;
        
        $.ajax({
        	async: false,
            type: "POST",
            url: url,
            data: form_data,
            dataType: "html",
            
            success: function(form_html){
        		log("ajax post response success.");
                $("#page_content").html(form_html);
                $("#page_content").animate({opacity: 1}, 500 );
                load_normal_link = false;
            },
            error: function(XMLHttpRequest){
            	log("ajax get response error!");
                // Display the complete Traceback html page
            	log(XMLHttpRequest);
            	var response_text = XMLHttpRequest.responseText;
            	log("response_text: '" + response_text + "'");
            	if (!response_text) {
            		document.write("<h1>ajax response error</h1>");
            	} else {
            		document.write(response_text);
            	}
            	load_normal_link = true;
            }
        });       
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
    $("#page_content").animate({opacity: 0.3}, 500 );

    var url = encodeURI(url);
    log("get:" + url);
    
    var load_normal_link = true;
    
    $.ajax({
    	async: false,
        type: "GET",
        url: url,
        dataType: "html",
        
        success: function(form_html){
    		log("ajax get success.");
            $("#page_content").html(form_html);
            $("#page_content").animate({opacity: 1}, 500 );
            load_normal_link = false;
        },
        error: function(XMLHttpRequest){
        	log("ajax get response error!");
            // Display the complete Traceback html page
        	log(XMLHttpRequest);
        	var response_text = XMLHttpRequest.responseText;
        	log("response_text: '" + response_text + "'");
        	if (!response_text) {
        		document.write("<h1>ajax response error</h1>");
        	} else {
        		document.write(response_text);
        	}
        	load_normal_link = true;
        }
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