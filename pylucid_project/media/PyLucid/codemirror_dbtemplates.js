/*
 * activate CodeMirror editor for django-dbtemplates
 * But only if mimetype exist and supported.
 */
jQuery(document).ready(function($) {
  // don't init editor with 'var', because we must access it for the diff function.
	editor = CodeMirror.fromTextArea('id_content', {
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
});