Frontend.communication = {
  currentRoundType: null,
  currentNumTables: null,
  currentSide: null,

  initialize: function() {
    Frontend.communication.loop(); // start the polling loop
  },
  
  loop: function() {
    Frontend.communication.poll();
    setInterval(Frontend.communication.poll, Frontend.settings.refreshInterval); // poll periodically
  },
  
  poll: function() {
    $.ajax({
      url: Frontend.settings.serverUrl + Frontend.communication.getQueryString(),
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

    $.ajax({
      url: Frontend.settings.serverRankingUrl + Frontend.communication.getQueryString(),
      type: "GET",
      dataType: "xml",
      cache: false,
      contentType: "text/xml",
      success: function(data) {
        Frontend.communication.processRanking(data);
      },
      error: function(blargh, error) {
        if (Frontend.settings.debugMode) window.alert("Something went wrong :(\n" + error);
      },
    });
  },
    
  process: function(data) {
    // window.data = data; // TODO DEBUG
    Frontend.ui.update(data);
    Frontend.timer.sync($("timer", data));
  },

  processRanking: function(data) {
    Frontend.ui.updateRanking($("ranking", data));
  },

  setRoundType: function(roundType, numTables, side) {
    Frontend.communication.currentRoundType = roundType;
    Frontend.communication.currentNumTables = numTables;
    Frontend.communication.currentSide = side;
  },
  
  roundTypeRedirect: function(data) {
    // check if the view (the HTML file) matches the current round type.
    // selection rounds and final rounds have a different template.
    // if the currently loaded HTML file is not the correct one, redirect.
    
    var roundType = $("update", data).attr("roundtype");
    var numTables = $("table", data).length;

    if ((roundType != Frontend.communication.currentRoundType) || (numTables != Frontend.communication.currentNumTables)) {
      // window.alert("redirecting");
      document.location.href = roundType + numTables.toString() + "_" + Frontend.communication.currentSide + ".html" + Frontend.communication.getQueryString();
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
