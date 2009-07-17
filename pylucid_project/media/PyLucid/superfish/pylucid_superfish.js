$(document).ready(function(){
  //
  // initialise Superfish menu
  // 
  $('ul.sf-menu').superfish({ 
      delay:       1000,                            // one second delay on mouseout 
      animation:   {opacity:'show',height:'show'},  // fade-in and slide-down animation 
      speed:       'fast'                           // faster animation speed
  });
});