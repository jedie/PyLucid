/*
 * activate CodeMirror editor for django-dbtemplates
 * But only if mimetype exist and supported.
 */
jQuery(document).ready(function($) {
	var editor = CodeMirror.fromTextArea('id_content', {
		path: PyLucid_media_url + "codemirror/",
		basefiles: ["codemirror_base.js"],
		parserfile: "parsedjango.js",
		stylesheet: PyLucid_media_url + "codemirror/codemirror.css",
		continuousScanning: 500,
		//lineNumbers: true,
		tabMode: "shift",
		indentUnit: 3,
		height: "40em",
		autoMatchParens: true
	});	
	log("CoreMirror initialized.");
    // FIXME: How can we add jquery.textarearesizer.js to the iframe?		
});