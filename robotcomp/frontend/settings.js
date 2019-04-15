Frontend = {};

Frontend.settings = {
  'refreshInterval': 2000, // in milliseconds - the server is polled this frequently
  'serverUrl': '/frontend_data/', // the url to poll to obtain the update XML
  'serverRankingUrl': '/ranking_data/', // the url to poll to obtain the ranking update XML
  // 'matchDuration': 180, // in seconds - necessary for the countdown timer
  'matchDurationSelection4': 120, // in seconds - match duration of the 4-table selection rounds
  'matchDurationSelection2': 120, // in seconds - match duration of the 2-table selection rounds
  'matchDurationFinal': 120, // in seconds - duration of the final
  'timerRefreshInterval': 1000, // 250, // in milliseconds - the timer is refreshed (roughly) this frequently
  'timerNotRunningText': '00:00', // text to show when the timer is not running (no matches in progress)
  'animationDuration': 1000, // 1500, // duration of the update animation
  'debugMode': false, // false, // show nasty error dialogs if something goes wrong (silent failures if false).
  'selectionRankingSize': 60, // how many players to include in the ranking in selection mode.
  'maxRankingItemsShownPerPage': 10, // how many ranking items are visible in the interface
};
