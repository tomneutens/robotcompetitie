from robots.models import Robot, Match, Round, Competition
from django.contrib import admin



class RobotAdmin(admin.ModelAdmin):
    actions = ['eliminate_robot', 'reenter_robot']
    list_display = ['name', 'team_number', 'type', 'status', 'is_high_school', 'for_credits', 'is_ieee', 'selection_score', 'final_score']
    list_editable = ['status']
    list_filter = ['status', 'type']
    ordering = ['team_number']
    
    # the following two methods don't seem to do anything useful, but they are apparently
    # necessary for getting the admin to play nice with these extra score fields.
    def selection_score(self, robot):
        return robot.selection_score
                    
    selection_score.admin_order_field = 'selection_score'
    
    def final_score(self, robot):
        
        return robot.final_score
        
    final_score.admin_order_field = 'final_score'
    
    def eliminate_robot(self, request, queryset):
        rows_updated = queryset.update(status=1)
        self.message_user(request, "%s robot(s) successfully eliminated from the competition." % rows_updated)
    eliminate_robot.short_description = "Eliminate robots from the competition"
    
    def reenter_robot(self, request, queryset):
        rows_updated = queryset.update(status=0)
        self.message_user(request, "%s robot(s) successfully reentered into the competition." % rows_updated)
    reenter_robot.short_description = "Reenter robots into the competition"


class MatchAdmin(admin.ModelAdmin):
    list_display = ['round', 'table', 'robot1', 'robot2', 'status', 'play_order', 'started_time']
    list_editable = ['status']
    list_filter = ['round', 'table', 'status']


class RoundAdmin(admin.ModelAdmin):
    actions = ['start_round', 'stop_round', 'plan_round']
    list_display = ['name', 'type', 'status', 'num_tables', 'competition', 'manage']
    list_editable = ['status']
    list_filter = ['status', 'type']
    
    def start_round(self, request, queryset):
        rows_updated = queryset.update(status=1) # 1 = running
        self.message_user(request, "%s round(s) successfully started." % rows_updated)
        
    def stop_round(self, request, queryset):
        rows_updated = queryset.update(status=2) # 2 = finished
        self.message_user(request, "%s round(s) successfully finished." % rows_updated)
        
    def plan_round(self, request, queryset):
        for r in queryset:
            r.plan_round()
        self.message_user(request, "%s round(s) successfully planned." % len(queryset))
        
        
    def manage(self, round):
        manage_round_link = '<a href="/manage_round/%d/">manage</a>' % round.id
        plan_round_link = '<a href="/plan_round/%d/">plan</a>' % round.id
        replan_round_link = '<a href="/replan_round/%d/">replan</a>' % round.id
        matches_link = '<a href="/admin/robots/match/?round__id__exact=%d">view matches</a>' % round.id
        links = "%s, %s, %s, %s" % (manage_round_link, plan_round_link, replan_round_link, matches_link)
        return links
    manage.allow_tags = True

    def available_data(self, form):
        q = FormResponse.objects.filter(form_name=form.title)
        if not q.count(): return 'No data yet...'

        dates = q.dates('time', kind="month", order='ASC')
        month_string = '<a href="/forms/download/%%s/%Y/%m/">%B %Y</a>'
        months = ', '.join([d.strftime(month_string) % form.slug for d in dates])

        return '<a href="/forms/get-data/%s/">All data</a>, %s' % (form.slug, months)
    available_data.allow_tags = True


class CompetitionAdmin(admin.ModelAdmin):
    list_display = ['name', 'running']
    list_editable = ['running']
    list_filter = ['running']
    

admin.site.register(Robot, RobotAdmin)
admin.site.register(Match, MatchAdmin)
admin.site.register(Round, RoundAdmin)
admin.site.register(Competition, CompetitionAdmin)
