

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



function get_pylucid_ajax_view(url) {
    /*************************************************************************
        PyLucid ajax replace function
        
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