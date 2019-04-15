Frontend.timer = {
  running: false,

  serverNow: 0, // server time at the last sync
  serverSince: 0, // server time when the timer was started
  localNow: 0, // local time at the last sync

  initialize: function() {
    Frontend.timer.loop(); // start the polling loop
  },

  loop: function() {
    Frontend.timer.refresh();
    setTimeout(Frontend.timer.loop, Frontend.settings.timerRefreshInterval);
  },

  sync: function(timerData) {
    // NOTE: sync does not compensate for the loading time of each AJAX request.
    // The delay is assumed to be negligible (< 200ms).
    var running = (timerData.attr("running") == "true");

    if (running) {
      Frontend.timer.serverNow = parseInt(timerData.attr("now"));
      Frontend.timer.serverSince = parseInt(timerData.attr("since"));
      Frontend.timer.localNow = Frontend.timer.timestamp();
      // console.log("set localNow to: " + Frontend.timer.localNow);
    }

    Frontend.timer.running = running;
  },

  refresh: function() {
    Frontend.ui.updateTimer(Frontend.timer.running, Frontend.timer.timeRemaining());
  },

  timeRunning: function() {
    // compute timer running time in seconds
    var serverPart = Frontend.timer.serverNow - Frontend.timer.serverSince;
    var localPart = Frontend.timer.timestamp() - Frontend.timer.localNow;
    return serverPart + localPart;
  },

  timeRemaining: function() {
    var remainder = Frontend.timer.getMatchDuration() - Frontend.timer.timeRunning();
    // prevent negative remainder:
    return Math.max(remainder, 0);
  },

  timestamp: function() {
    return Math.round(new Date().getTime() / 1000);
  },

  getMatchDuration: function() {
    if (Frontend.communication.currentRoundType == "selection") {
      if (Frontend.communication.currentNumTables == 4) {
        return Frontend.settings.matchDurationSelection4;
      }
      else if (Frontend.communication.currentNumTables == 3){
        //Same time as with 4 tables
        return Frontend.settings.matchDurationSelection4;
      }
      else if (Frontend.communication.currentNumTables == 2) {
        return Frontend.settings.matchDurationSelection2;
      }
    }
    else if (Frontend.communication.currentRoundType == "final") {
      return Frontend.settings.matchDurationFinal;
    }
  },
};


jQuery(function() {
  Frontend.timer.initialize();
});
