from django.shortcuts import get_object_or_404, render_to_response, render
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.template import RequestContext
from robots.models import Robot, Match, Round, Competition
from datetime import datetime
import time

NUM_UPCOMING_MATCHES = 3 # number of upcoming matches per table to show
roundtype = ""


def to_timestamp(d):
    """
    converts a python datetime to a unix timestamp.
    """
    return int(time.mktime(d.timetuple()))


def manage_current_round(request):
    try:
        current_round_id = Round.objects.get(status=1).id
    except:
        current_round_id = -1
    return manage_round(request, current_round_id)

def manage_round(request, round_id):
    print "round_id:"
    print round_id
    try:
        current_round = Round.objects.get(id=round_id)
        tables_matches = current_round.matches_by_table()
    except Round.DoesNotExist:
        current_round = None
        tables_matches = []

    return render_to_response('manage_round.html', {
        'current_round': current_round,
        'tables_matches': tables_matches,
    })

def plan_round(request, round_id):
    round = Round.objects.get(id=round_id)
    round.plan_round()
    print "redirecting to manage_round"
    return HttpResponseRedirect("/manage_round/" + round_id)

def replan_round(request, round_id):
    round = Round.objects.get(id=round_id)
    round.replan_round()
    print "redirecting to manage_round"
    return HttpResponseRedirect("/manage_round/" + round_id)

def start_round(request, round_id):
    round = Round.objects.get(id=round_id)
    round.start()
    print "redirecting to manage_round"
    return HttpResponseRedirect("/manage_round/" + round_id)

def finish_round(request, round_id):
    round = Round.objects.get(id=round_id)
    round.finish()
    print "redirecting to manage_round"
    return HttpResponseRedirect("/manage_round/" + round_id)

def index(request):
    return HttpResponseRedirect("/manage_round/")


def postpone_match(request, match_id):
    match = Match.objects.get(id=match_id)
    match.postpone()
    print "redirecting to manage_round"
    return HttpResponseRedirect("/manage_round")

def finish_match(request, match_id):
    match = Match.objects.get(id=match_id)
    match.finish(request.POST['result'])
    print "redirecting to manage_round"
    print match.round.id
    return HttpResponseRedirect("/manage_round")


def start_next_matches(request, round_id):
    round = Round.objects.get(id=round_id)
    round.start_next_matches()
    print "redirecting to manage_round"
    return HttpResponseRedirect("/manage_round/" + round_id)


def get_ranking_entries():
    print "getting ranking entries"
    # ranking - ALWAYS sort by selection score, even in the final
    robots = Robot.objects.filter(status=0, type=0) # participating robots, exclude house robot
    print "i have a list of robots"


    #if roundtype == 'selection':
    print "the last round was a selection round"
    score = lambda r: r.selection_score
    order_field = '-selection_score'
    #elif roundtype == 'final':
    #    print "the last round was a final round"
    #    score = lambda r: r.final_score
    #    order_field = '-final_score'

    ranking_entries = []
    print "creating ranking entries"
    for r in robots.order_by(order_field):
        print r.avatar
        ranking_entries.append({
            'name': r.name,
            'teamnumber': r.team_number,
            'score': score(r),
            'avatar': r.avatar,
        })

    print ranking_entries
    return ranking_entries


def ranking_data(request):
    """
    This view generates the XML file used by the frontend to display the ranking.
    """
    # get the type of the last played round, even if there is no currently active round
    latest_round = Round.objects.order_by('-id')[0] # this is the latest created round
    print "the latest round type was"
    print latest_round.type
    if latest_round.type == 0:
        roundtype = 'selection'
    else:
        roundtype = 'final'

    ranking_entries = get_ranking_entries()

    return render(request, 'ranking_data.xml', {
        'roundtype': roundtype,
        'ranking_entries': ranking_entries,
    }, content_type="text/xml")



def get_tables(current_round):
    tables = []
    for t in range(current_round.num_tables):
        matches = []
        # most recent finished match per table
        match = current_round.most_recent_match_for_table(t)
        matches.append({ 'type': 'last', 'match': match })

        # running match per table
        match = current_round.running_match_for_table(t)
        matches.append({ 'type': 'current', 'match': match })

        # a couple of upcoming matches
        upcoming_matches = current_round.upcoming_matches_for_table(t)[:NUM_UPCOMING_MATCHES]
        if upcoming_matches is not None:
            for match in upcoming_matches:
                matches.append({ 'type': 'next', 'match': match })

        tables.append(matches)

        print "Printing tables:"
        print tables

    return tables


def frontend_data(request):
    """
    This view generates the XML file used by the frontend to display the match status
    """
    if Round.objects.filter(status=1).count() == 0:
        return render_to_response('frontend_data.xml', {
            'roundtype': 'pause',
        }, content_type="text/xml")
    else:
        current_round = Round.objects.get(status=1)
        if current_round.type == 0:
            roundtype = 'selection'
        else:
            roundtype = 'final'

    # tables
    tables = get_tables(current_round)

    # timer
    timer_running = False
    timer_now = datetime.now()
    timer_since = timer_now
    running_matches = current_round.running_matches
    if running_matches.count() > 0:
        timer_running = True
        timer_since = running_matches[0].started_time

    timer = {
        'since': to_timestamp(timer_since),
        'now': to_timestamp(timer_now),
        'running': timer_running,
    }

    return render(request, 'frontend_data.xml', {
        'roundtype': roundtype,
        # 'ranking_entries': ranking_entries,
        'tables': tables,
        'timer': timer,
    }, content_type="text/xml")




def public_data(request):
    """
    Generate a static HTML file with all relevant info that will be periodically uploaded to
    a public location. (with bootstrap so it plays nice on mobile)
    """

    if Round.objects.filter(status=1).count() == 0:
        tables = []
    else:
        current_round = Round.objects.get(status=1)
        if current_round.type == 1: # final round, no tables
            tables = []
        else:
            tables = get_tables(current_round)

    ranking_entries = get_ranking_entries()

    return render_to_response('public_data.html', {
        'ranking_entries': ranking_entries,
        'tables': tables,
    })

def live_display(request):
    """
    Generate a live display of the current and upcomming matches with the color of the table above so Peter
    can easlily announce the next teams.
    """

    if Round.objects.filter(status=1).count() == 0:
        tables = []
    else:
        current_round = Round.objects.get(status=1)
        if current_round.type == 1: # final round, no tables
            tables = []
        else:
            tables = get_tables(current_round)


    return render_to_response('live_display.html', {
        'tables': tables,
    })
