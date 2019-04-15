Frontend.communication = {
  initialize: function() {
    Frontend.communication.loop(); // start the polling loop
  },
  
  loop: function() {
    Frontend.communication.poll();
    setInterval(Frontend.communication.poll, Frontend.settings.refreshInterval); // poll periodically
  },
  
  poll: function() {
    $.ajax({
      url: Frontend.settings.serverRankingUrl + Frontend.communication.getQueryString(),
      type: "GET",
      dataType: "xml",
      cache: false,
      contentType: "text/xml",
      success: function(data) {
        Frontend.communication.roundTypeRedirect(data);
        Frontend.communication.process(data);
      },
      error: function(blargh, error) {
        if (Frontend.settings.debugMode) window.alert("Something went wrong :(\n" + error);
      },
    });
  },
    
  process: function(data) {
    Frontend.ui.update(data);
    //Frontend.timer.sync($("timer", data));
  },
  
  roundTypeRedirect: function(data) {
    // check if the view (the HTML file) matches the current round type.
    // selection rounds and final rounds have a different template.
    // if the currently loaded HTML file is not the correct one, redirect.
    
    var roundType = $("update", data).attr("roundtype");
    var currentView = document.location.href.match(/.*\/ranking_(.+?)\./)[1];
    
    if (roundType != currentView) {
      // console.log("Wrong template, redirecting...");
      document.location.href = "ranking_" + roundType + ".html" + Frontend.communication.getQueryString();
    }
  },
  
  getQueryString: function() {
    var urlParts = window.location.href.split("?");
    if (typeof(urlParts[1]) == "undefined") return "";
    else return "?" + urlParts[1];
  },
};


jQuery(function() {
  Frontend.communication.initialize();
});
