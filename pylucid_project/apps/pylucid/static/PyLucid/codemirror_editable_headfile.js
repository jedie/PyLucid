/*
 * activate CodeMirror editor for EditableHtmlHeadFile
 * But only if mimetype exist and supported.
 */
jQuery(document).ready(function($) {
    mimetype = $('#id_mimetype').val();
	log("mimetype:" + mimetype);
	
	var parserfile=null;
	if (mimetype == "text/css") {
		parserfile="parsecss.js";
	}
	if (mimetype == "text/javascript") {
		parserfile=["tokenizejavascript.js", "parsejavascript.js"];
	}
	if (parserfile!=null) {
		log("use parserfile:" + parserfile)
		var editor = CodeMirror.fromTextArea('id_content', {
			path: PyLucid_media_url + "codemirror/",
			basefiles: ["codemirror_base.js"],
			parserfile: parserfile,
			stylesheet: PyLucid_media_url + "codemirror/codemirror.css",
			continuousScanning: 500,
			//lineNumbers: true,
			tabMode: "shift",
			indentUnit: 3,
			height: "40em",
			autoMatchParens: true
		});	
		log("CoreMirror initialized.");		
	} else {
		log("No CodeMirror: mimetype not supported.")
	}
});