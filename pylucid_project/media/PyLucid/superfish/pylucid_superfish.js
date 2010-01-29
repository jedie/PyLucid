jQuery(document).ready(function($) {
  //
  // Initialize Superfish menu
  // 
  $('ul.sf-menu').superfish({ 
      delay:       300,                             // delay on mouseout 
      animation:   {opacity:'show',height:'show'},  // fade-in and slide-down animation 
      speed:       100                              // faster animation speed
  });
  log("superfish initialized.");
});