// shorthand
jQuery.fn.hasAttr = function(name) {
   return this.attr(name) !== undefined;
};


// based on http://www.dreamincode.net/code/snippet4235.htm
jQuery.fn.fontfit = function() {
  var dwidth = $(this).width();
  $(this).wrapInner('<span id="fontfit"></div>');
  var cwidth = $("#fontfit").width();
  var fsize = (($(this).css("font-size")).slice(0,-2))*1;
  var original_fsize = fsize;

  /* if (Frontend.settings.debugMode && cwidth > dwidth) {
    console.log("dwidth is " + dwidth + "\ncwidth is " + cwidth + "\nfsize is " + fsize);
  } */

  while(cwidth>dwidth && fsize>0) {
    fsize-=1;
    $(this).css("font-size",fsize+"px");
    // a little heuristic to have long robot names properly vertically aligned.
    // var newLineHeight = 1 + ((original_fsize / fsize) - 1) * 5.0;
    // $(this).css("line-height",  newLineHeight);
    var paddingTop = (original_fsize - fsize) / 1.5;
    $(this).css("padding-top", paddingTop);
    cwidth = $("#fontfit").width();
  }

  // if (Frontend.settings.debugMode) console.log("Fontsize is " + fsize);

  $("#fontfit").replaceWith($("#fontfit").html());

  return this;
}


Frontend.ui = {
  update: function(data) {
     Frontend.ui.roundtype = $("update", data).attr("roundtype");
     //var rankingData = $("ranking", data);
     var tablesData = $("tables", data);
     var timerData = $("timer", data);
     //Frontend.ui.updateRanking(rankingData);
     Frontend.ui.updateTables(tablesData);
     //Frontend.ui.updateTimer(timerData);
  },


  updateRanking: function(rankingData) {
      //remark: replaced old splitting into lists by css multiple column styling
      var list_html;
      list_html = Frontend.ui.convertRankingToHtml(rankingData);
      if (Frontend.communication.currentSide == "right"){

      }
      let ranking_list = $('#ranking_list');
      ranking_list.empty();
      ranking_list.append(list_html.find("li"));
    },

  convertRankingToHtml: function(rankingData) {
    var list_html = $("<ul>");

    $("player", rankingData).each(function(i) {
      if (Frontend.communication.currentSide == "left" && i < Frontend.settings.maxRankingItemsShownPerPage){
        var playerData = $(this);
        var playerHtml = Frontend.ui.convertPlayerToHtmlForRanking(playerData);
        list_html.append(playerHtml);
      }
      if (Frontend.communication.currentSide == "right" && i >= Frontend.settings.maxRankingItemsShownPerPage && i < Frontend.settings.maxRankingItemsShownPerPage*2){
        var playerData = $(this);
        var playerHtml = Frontend.ui.convertPlayerToHtmlForRanking(playerData);
        list_html.append(playerHtml);
      }
      /*if (i < Frontend.settings.maxRankingItemsShown) {
        if (Frontend.communication.currentSide == "right" && i < 10){

        }else{
          if (i < 10){
            var playerData = $(this);
            var playerHtml = Frontend.ui.convertPlayerToHtmlForRanking(playerData);
            list_html.append(playerHtml);
          }
        }
      }*/
    });

    return list_html;
  },

  convertPlayerToHtmlForTable: function(playerData) {
    var html = $("<li class='player'/>");

    var teamNumberHtml = "<div class='team'><span>" + playerData.attr("teamnumber") + "</span></div>";
    var nameHtml = "<div class='name'>" + playerData.attr("name") + "</div>";
    // var teamNumberHtml = "<span class='team'>" + playerData.attr("teamnumber") + "</span>";
    // var nameHtml = "<div class='name'>" + teamNumberHtml + ". " + playerData.attr("name") + "</div>";
    var avatarHtml = "<div class='avatar'><img src='" + playerData.attr("avatar") + "'><div class='avatar-overlay'></div></div>";

    html.append(avatarHtml);
    html.append(teamNumberHtml);
    html.append(nameHtml);

    html.addClass(playerData.attr("type"));
    html.attr("data-id", playerData.attr("teamnumber"));

    return html;
  },

  convertPlayerToHtmlForRanking: function (playerData) {
    var html = $("<li class='player'/>");
    var teamStr = "(" + playerData.attr("teamnumber") + ")";
    var avatarHtml = "<div class='avatar'><img src='" + playerData.attr("avatar") + "'><div class='avatar-overlay'></div></div>";

    html.append(avatarHtml);
    html.append("<div class='name'>" + playerData.attr("name") + "</div>");
    html.append("<div class='team'>" + teamStr + "</div>");
    html.append("<div class='score'>" + playerData.attr("score") + "</div>");
    html.addClass(playerData.attr("type"));
    html.attr("data-id", playerData.attr("teamnumber"));

    return html;
  },

  updateTables: function(tablesData) {
    tablesData.find("table").each(function() {
      var tableData = $(this);
      var tableNumber = tableData.attr("number");
      var tableDiv = $("div.table[data-id='" + tableNumber + "']");
      var newMatches = Frontend.ui.convertTableToHtml(tableData);

      $("ul.matches li.match").addClass("animated");
      $("ul.matches", tableDiv).quicksand(newMatches.find("li.match"), {
        'duration': Frontend.settings.animationDuration,
        'adjustHeight': false,
        'enhancement': function() {
          $("ul.matches li.match li.player .name").each(function(){
            $(this).fontfit();
          });
          $("ul.matches li.match.current li.player .name").each(function(){
            $(this).fontfit();
          });
        },
      },
      function() {
        $("ul.matches li.match").removeClass("animated");
      });

    });
  },


  convertTableToHtml: function(tableData) {
    var html = $("<ul/>");

    matchesData = tableData.find("match");

    matchesData.each(function() {
      var matchData = $(this);
      var matchLi =  Frontend.ui.convertMatchToHtml(matchData);
      html.append(matchLi);
    });

    return html;
  },

  convertMatchToHtml: function(matchData) {
    var matchId = matchData.attr("id");
    var matchType = matchData.attr("type");
    var matchStatus = matchData.attr("status");
    var playersData = matchData.find("player");
    console.log(matchStatus);

    var html = $("<li/>").addClass("match").addClass(matchType);
    html.attr("data-id", matchId);
    html.addClass(matchStatus);

    var playersHtml = $("<ul class='players'/>");

    playersData.each(function(i) {
      var playerData = $(this);
      var playerHtml = Frontend.ui.convertPlayerToHtmlForTable(playerData);
      playerHtml.addClass("player"+i);

      // add a score div with the correct score
      if (matchStatus == "finished_robot1won") {
        if (i == 0) {
            // playerHtml.prepend("<div class='score'>1</div>");
            playerHtml.addClass("winner");
        }
        if (i == 1) {
            // playerHtml.prepend("<div class='score'>0</div>");
            playerHtml.addClass("loser");
        }
      }
      else if (matchStatus == "finished_robot2won") {
        if (i == 0) {
            // playerHtml.prepend("<div class='score'>0</div>");
            playerHtml.addClass("loser");
        }
        if (i == 1) {
            // playerHtml.prepend("<div class='score'>1</div>");
            playerHtml.addClass("winner");
        }
      }
      else if (matchStatus == "draw") {
        // playerHtml.prepend("<div class='score'>0</div>");
        playerHtml.addClass("draw");
      }
      else if (matchStatus == "fail") {
        playerHtml.addClass("fail");
      }
      // Situation where one robot won and the other robot finished
      else if (matchStatus == "finished_robot1won_robot2finished") {
        if (i == 0) {
            // playerHtml.prepend("<div class='score'>0</div>");
            playerHtml.addClass("winner");
        }
        if (i == 1) {
            // playerHtml.prepend("<div class='score'>1</div>");
            playerHtml.addClass("loser");
        }
      }
      else if (matchStatus == "finished_robot2won_robot1finished") {
        if (i == 0) {
            // playerHtml.prepend("<div class='score'>0</div>");
            playerHtml.addClass("loser");
        }
        if (i == 1) {
            // playerHtml.prepend("<div class='score'>1</div>");
            playerHtml.addClass("winner");
        }
      }
      playersHtml.append(playerHtml);
    });

    html.append(playersHtml);

    return html;
  },


  updateTimer: function(running, timeRemaining) {
    if (running) {
      if (timeRemaining > (Frontend.timer.getMatchDuration() - 5)) {
        formattedTime = "GO!";
        $("#timer .remaining").addClass("end-is-nigh");
      }
      else {
        minutesRemaining = Math.floor(timeRemaining / 60);
        secondsRemaining = timeRemaining % 60;
        formattedTime = Frontend.ui.zeroPad(minutesRemaining, 2) + ":" + Frontend.ui.zeroPad(secondsRemaining, 2);

        if (timeRemaining <= 10) {
          $("#timer .remaining").addClass("end-is-nigh");
        }
        else {
          $("#timer .remaining").removeClass("end-is-nigh");
        }
      }
    }
    else {
      formattedTime = Frontend.settings.timerNotRunningText;
      $("#timer .remaining").removeClass("end-is-nigh");
    }
    $("#timer .remaining").text(formattedTime);
  },

  zeroPad: function(number, len) {
    var padded = "" + number;
    while(padded.length < len) {
      padded = "0" + padded;
    }
    return padded;
  },
};
