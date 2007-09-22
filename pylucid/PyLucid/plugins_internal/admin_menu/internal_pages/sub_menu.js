// Open the django admin panel links in a seperat window
function OpenInWindow(URL) {
  win1 = window.open(URL, "", "width=1000, height=600, dependent=yes, resizable=yes, scrollbars=yes");
  win1.focus();
}