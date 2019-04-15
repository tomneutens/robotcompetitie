from django.db import models
import random
import itertools
from datetime import datetime

class RobotManager(models.Manager):
    """
    This custom manager ensures that the robot scores in the currently running competition
    are always returned as well, as 'selection_score' and 'final_score'.

    This is implemented as an SQL (sub)query to make the fields sortable in the admin interface.
    """
    def get_queryset(self):
        qs = super(RobotManager, self).get_queryset()
        # old query for 2012's scoring mechanism: win = 1, draw/loss = 0
        #query_str = """
        #SELECT COUNT(*) FROM robots_match
        #JOIN robots_round ON robots_match.round_id = robots_round.id
        #JOIN robots_competition ON robots_round.competition_id = robots_competition.id
        #WHERE robots_competition.running = 1
        #AND robots_round.type = %d
        #AND ((robots_match.robot1_id = robots_robot.id AND robots_match.status = 3)
        #OR (robots_match.robot2_id = robots_robot.id AND robots_match.status = 4))
        #"""

        # old query for 2013's scoring mechanism: win = 3, draw = 1, loss = 0
        # this crazy query counts the # of matches won, multiplies it by 3,
        # then adds the # of matches that ended in a draw. This is the score.
        #query_str = """
        #((SELECT COUNT(*) FROM robots_match
        #JOIN robots_round ON robots_match.round_id = robots_round.id
        #JOIN robots_competition ON robots_round.competition_id = robots_competition.id
        #WHERE robots_competition.running = 1
        #AND robots_round.type = {0}
        #AND ((robots_match.robot1_id = robots_robot.id AND robots_match.status = 3)
        #OR (robots_match.robot2_id = robots_robot.id AND robots_match.status = 4))) * 3 +
        #SELECT COUNT(*) FROM robots_match
        #JOIN robots_round ON robots_match.round_id = robots_round.id
        #JOIN robots_competition ON robots_round.competition_id = robots_competition.id
        #WHERE robots_competition.running = 1
        #AND robots_round.type = {1}
        #AND ((robots_match.robot1_id = robots_robot.id AND robots_match.status = 5)
        #OR (robots_match.robot2_id = robots_robot.id AND robots_match.status = 5))))
        #"""

        # query for this year's scoring mechanism: win = 1, draw = 0, loss = 0, both failed = 0
        #query_str = """
        #SELECT COUNT(*) FROM robots_match
        #JOIN robots_round ON robots_match.round_id = robots_round.id
        #JOIN robots_competition ON robots_round.competition_id = robots_competition.id
        #WHERE robots_competition.running = 1
        #AND robots_round.type = {0}
        #AND ((robots_match.robot1_id = robots_robot.id AND (robots_match.status = 3))
        #OR (robots_match.robot2_id = robots_robot.id AND (robots_match.status = 4)))
        #"""

        # query for this year's scoring mechanism: win = 1, draw = 1, loss = 0, both failed = 0
        #query_str = """
        #SELECT COUNT(*) FROM robots_match
        #JOIN robots_round ON robots_match.round_id = robots_round.id
        #JOIN robots_competition ON robots_round.competition_id = robots_competition.id
        #WHERE robots_competition.running = 1
        #AND robots_round.type = %d
        #AND ((robots_match.robot1_id = robots_robot.id AND (robots_match.status = 3 OR robots_match.status = 5))
        #OR (robots_match.robot2_id = robots_robot.id AND (robots_match.status = 4 OR robots_match.status = 5)))
        #"""



        # old query for 2018's scoring mechanism: win = 3, lost/finished = 1, not finished/draw = 0
        # this crazy query counts the # of matches won, multiplies it by 3,
        # then adds the # of matches that the robot lost but finished. This is the score.
        query_str = """
        (
          (
            SELECT
              COUNT(*)
            FROM
              robots_match
              JOIN robots_round ON robots_match.round_id = robots_round.id
              JOIN robots_competition ON robots_round.competition_id = robots_competition.id
            WHERE
              robots_competition.running = 1
              AND robots_round.type = {0}
              AND (
                (
                  robots_match.robot1_id = robots_robot.id
                  AND (
                    robots_match.status = 3
                    OR robots_match.status = 7
                  )
                )
                OR (
                  robots_match.robot2_id = robots_robot.id
                  AND (
                    robots_match.status = 4
                    OR robots_match.status = 8
                  )
                )
              )
          ) * 3 + (
          SELECT
            COUNT(*)
          FROM
            robots_match
            JOIN robots_round ON robots_match.round_id = robots_round.id
            JOIN robots_competition ON robots_round.competition_id = robots_competition.id
          WHERE
            robots_competition.running = 1
            AND robots_round.type = {1}
            AND (
              (
                robots_match.robot1_id = robots_robot.id
                AND robots_match.status = 8
              )
              OR (
                robots_match.robot2_id = robots_robot.id
                AND robots_match.status = 7
              )
            )
        )
        )
        """



        # These queries are for the sumo competition since we want to have a separate scoring for qualifiers and final
        #selection_query = query_str.format(0, 0)# type 0 = selection rounds
        #final_query = query_str.format(1, 1) # type 1 = final rounds

        # These queries are for the robot race
        selection_query = query_str.format(0, 0)# type 0 = selection rounds
        final_query = selection_query
        #final_query = query_str.format(1, 1) # type 1 = final rounds

        print "Executing query"
        queryresult = qs.extra(select={
            'selection_score': selection_query,
            'final_score': final_query,
        })
        print "queryresult:"
        print queryresult
        return queryresult


        # These queries are for the race competition here there is no final with separate scoring
        #selection_query = query_str
        #final_query = selection_query
        #print "The score calculation query has been executed!"
        #return qs.extra(select={
        #    'selection_score': selection_query,
        #    'final_score': final_query,
        #})

    def participating(self):
        """
        get a list of currently participating robots, including the house robot
        """
        print "getting queryset"
        qs = self.get_queryset()
        print qs
        print "filter on status"
        return qs.filter(status=0)

    def for_scheduling(self):
        """
        get a list of currently participating robots. if its length is odd,
        remove the house robot. This method can be used for scheduling the matches.
        """
        qs = self.participating()
        if len(qs) % 2 == 0:
            return qs
        else:
            return qs.exclude(type=1)


class Robot(models.Model):
    STATUS_CHOICES = (
        (0, 'participating'),
        (1, 'eliminated'),
    )

    TYPE_CHOICES = (
        (0, 'regular'),
        (1, 'house robot'),
    )

    name = models.CharField(max_length=200)
    team_number = models.IntegerField()
    is_ieee = models.BooleanField(default=False, verbose_name="at least one team member is an IEEE member")
    is_high_school = models.BooleanField(default=False, verbose_name="all team members are in high school")
    for_credits = models.BooleanField(default=False, verbose_name="the team is participating for credits")
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    type = models.IntegerField(choices=TYPE_CHOICES, default=0)
    avatar = models.ImageField(upload_to="avatars")

    objects = RobotManager()

    def __unicode__(self):
        return "Robot '%s' (team %d)" % (self.name, self.team_number)

    def get_matches(self):
        return self.matches_as_1st.all() | self.matches_as_2nd.all() # merge both querysets

    def get_matches_won(self):
        as_1st = self.matches_as_1st.filter(status__in=[3, 5]) # robot 1 won or draw
        as_2nd = self.matches_as_2nd.filter(status__in=[4, 5]) # robot 2 won or draw
        return as_1st | as_2nd # merge querysets

    def selection_matches_played_vs(self, other_robot):
        """
        Return the selection matches that this robot has
        played against the other robot, in the currently running competition
        """
        as_1st = self.matches_as_1st.filter(robot2=other_robot, status__in=[2,3,4,5,6], round__type=0, round__competition__running=True)
        as_2nd = self.matches_as_2nd.filter(robot1=other_robot, status__in=[2,3,4,5,6], round__type=0, round__competition__running=True)
        return as_1st | as_2nd

    def num_selection_matches_played_vs(self, other_robot):
        return len(self.selection_matches_played_vs(other_robot))



class Match(models.Model):
    STATUS_CHOICES = (
        (0, 'planned'),
        (1, 'running'),
        (2, 'finished_no_score'),
        (3, 'finished_robot1won'),
        (4, 'finished_robot2won'),
        (5, 'draw'), # both robots finished at the same time (rare)
        (6, 'fail'), # both robots failed to finish
        (7, 'finished_robot1won_robot2finished'),
        (8, 'finished_robot2won_robot1finished'),
    )
    robot1 = models.ForeignKey('Robot', related_name='matches_as_1st')
    robot2 = models.ForeignKey('Robot', related_name='matches_as_2nd')
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    round = models.ForeignKey('Round')
    table = models.IntegerField()
    play_order = models.IntegerField()
    started_time = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return "Match between '%s' (%d) and '%s' (%d) in round '%s'" % (
            self.robot1.name, self.robot1.team_number, self.robot2.name, self.robot2.team_number, self.round.name)

    def is_between(self, r1, r2):
        return (r1 == self.robot1 and r2 == self.robot2) or (r1 == self.robot2 and r2 == self.robot1)

    def start(self):
        if self.status == 0:
            self.status = 1
            self.started_time = datetime.now()
            self.save()
        else:
            raise RuntimeError("Cannot start a match that is already running or finished.")

    def postpone(self):
        if self.status == 0:
            self.play_order = self.round.last_order()
            self.save()
        else:
            raise RuntimeError("Cannot postpone running or finished match.")

    def finish(self, result):
        if self.status == 1:
            self.status = result
            self.save()
        else:
            raise RuntimeError("Cannot finish a match that is not running.")

    @property
    def planned(self):
        return self.status == 0

    @property
    def running(self):
        return self.status == 1

    @property
    def finished(self):
        return self.status in [2, 3, 4, 5]

    @property
    def no_score(self):
        return self.status == 2

    @property
    def robot1won(self):
        return self.status == 3

    @property
    def robot2won(self):
        return self.status == 4

    @property
    def draw(self):
        return self.status == 5

    @property
    def fail(self):
        return self.status == 6

    @property
    def duplicates(self):
        """
        gives all matches with the same opponents as this match (including this one!)
        """
        as_12 = Match.objects.filter(robot1=self.robot1, robot2=self.robot2, round__competition__running=True)
        as_21 = Match.objects.filter(robot1=self.robot2, robot2=self.robot1, round__competition__running=True)
        return (as_12 | as_21)

    @property
    def has_been_played_before(self):
        return self.duplicates.count() > 1


class Round(models.Model):
    """
    A round is a set of matches that has every robot playing a single match.
    Note that each level will probably have multiple rounds as a result.

    A final round should always have a single table.
    """
    STATUS_CHOICES = (
        (0, 'created'),
        (1, 'running'),
        (2, 'finished'),
    )
    TYPE_CHOICES = (
        (0, 'selection'),
        (1, 'final'),
    )
    competition = models.ForeignKey("Competition")
    name = models.CharField(max_length=200)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    type = models.IntegerField(choices=TYPE_CHOICES, default=0)
    num_tables = models.IntegerField()

    def __unicode__(self):
        return "Round '%s' in competition '%s'" % (self.name, self.competition.name)

    def last_order(self):
        """
        Returns an integer that, when assigned as the play_order of a match,
        ensures that the match is the last to be played in this round.
        """
        return self.max_order() + 1

    def max_order(self):
        """
        Returns the play_order of the last match to be played in this round.
        """
        if self.match_set.count() == 0:
            return 0
        else:
            return self.match_set.aggregate(models.Max('play_order'))['play_order__max']

    def start(self):
        self.status = 1
        self.save()

    def finish(self):
        self.status = 2
        self.save()

    def replan_round(self):
        """
        Delete all matches in this round and replan it.
        """
        self.match_set.all().delete()
        self.plan_round()

    def plan_round(self):
        print(self.type)
        if self.type == 0: # selection
            self.plan_selection_round()
        elif self.type == 1: # final
            self.plan_final_round()

    def plan_selection_round(self):
        """
        This method creates matches for the round. It will include all currently participating
        robots, and optionally (if there is an odd number of regular robots) the house robot.
        It also takes in account previously played matches and tries to pit different robots
        against each other in every round, if possible (in the finals this probably won't
        be possible).
        Every regular robot should occur exactly once in a selection round.
        """
        # get the list of robots to schedule (its length will be even).
        robots_to_schedule = list(Robot.objects.for_scheduling())
        random.shuffle(robots_to_schedule)
        # the shuffling prevents the same robot from always being picked first.

        current_table = 0
        while len(robots_to_schedule) > 0:
            robot1 = robots_to_schedule.pop() # select last robot in the list and remove it
            possible_opponents = sorted(robots_to_schedule, key=lambda r: (r.num_selection_matches_played_vs(robot1), random.random()))
            robot2 = possible_opponents[0]
            # by selecting the first robot, we ensure that it has the least possible amount of matches played against robot1.
            robots_to_schedule.remove(robot2)
            # schedule match
            m = Match(robot1=robot1, robot2=robot2, round=self, table=current_table, play_order=self.last_order())
            m.save()
            current_table = (current_table + 1) % self.num_tables

    def plan_final_round(self):
        """
        This method creates matches for the round, pitting all participating robots against each other.
        This means that each robot will occur (num_robots - 1) times in this round!
        """
        robots_to_schedule = list(Robot.objects.filter(status=0, type=0)) # get all participating robots, but not the house robot
        print(robots_to_schedule)
        pairs = list(itertools.combinations(robots_to_schedule, 2))
        print(pairs)
        random.shuffle(pairs)
        for robot1, robot2 in pairs:
            if random.random() > 0.5:
                robot1, robot2 = robot2, robot1 # switch places half of the time, looks nicer

            m = Match(robot1=robot1, robot2=robot2, round=self, table=0, play_order=self.last_order())
            m.save()
            print(m)


    #def plan_final_round(self):
    #    """
    #    This method does nothing, as the final this year consists of a single race with 5 robots pitted against each other.
    #    """
    #    pass

    def matches_by_table(self):
        """
        Returns a list of querysets. The list contains a queryset for each table.
        Each queryset contains the matches on the given table of this round in play order.
        """
        return [self.match_set.filter(table=t).order_by('play_order') for t in range(self.num_tables)]

    @property
    def matches_running(self):
        return self.match_set.filter(status=1).count() > 0

    @property
    def all_matches_finished(self):
        return self.match_set.filter(status__in=[0,1]).count() == 0

    def start_next_matches(self):
        """
        Start the next matches in line synchronously, provided that no matches are currently running.
        """
        if self.matches_running:
            raise RuntimeError("Cannot start next matches because one or more matches are still running.")
        for t in range(self.num_tables):
            match_qs = self.match_set.filter(table=t, status=0).order_by('play_order')
            if match_qs.count() > 0:
                match_qs[0].start()

    @property
    def created(self):
        return self.status == 0

    @property
    def running(self):
        return self.status == 1

    @property
    def finished(self):
        return self.status == 2

    @property
    def has_matches(self):
        return self.match_set.count() > 0

    def most_recent_match_for_table(self, table):
        qs = self.match_set.filter(table=table, status__in=[2,3,4,5,6,7,8]).order_by("-started_time")
        if qs.count() > 0:
            return qs[0]
        else:
            return None

    def running_match_for_table(self, table):
        qs = self.match_set.filter(table=table, status=1)
        if qs.count() > 0:
            return qs[0]
        else:
            return None

    def upcoming_matches_for_table(self, table):
        return self.match_set.filter(table=table, status=0).order_by("play_order")

    @property
    def running_matches(self):
        return self.match_set.filter(status=1)





class Competition(models.Model):
    name = models.CharField(max_length=200)
    running = models.BooleanField(default=False)

    def __unicode__(self):
        if self.running:
            return "Competition '%s', currently running" % self.name
        else:
            return "Competition '%s', not running" % self.name
