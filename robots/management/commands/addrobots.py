from django.core.management.base import BaseCommand, CommandError
from robots.models import Robot

class Command(BaseCommand):
    help = 'Creates entries for all robots registered for the competition'

    def handle(self, *args, **options):
        ROBOTS = (
            # team_number, name, is_high_school, is_ieee, is_houserobot, is_ugent
            (1, 'Lodewijk de 14e', True, False, False, False),
            (2, 'de nayer', True, False, False, False),
            (4, 'Right On Track', False, False, False, False),
            (5, 'P', True, False, False, False),
            (6, 'Lindsay', True, False, False, False),
            (7, 'The Professor', False, True, False, False),
            (8, 'Doos', True, False, False, True),
            (9, 'Mr. Flash', True, True, False, True),
            (10, 'C3PO', True, False, False, False),
            (11, 'BSOD3', True, True, False, False),
            (12, 'Karton', True, False, False, False),
            (13, 'Lightning McQueen', True, False, False, False),
            (14, '\'T Snuiverken', True, False, False, True),
            (15, 'Kermit', False, False, False, False),
            (16, 'Nightrider', True, False, False, False),
            (17, 'Blanco', True, False, False, True),
            (18, 'The Challenger', True, False, False, True),
            (19, 'Trollbot', True, False, False, False),
            (20, 'R2-D3', True, True, False, False),
            (21, 'Black Jack', False, False, False, False),
            (22, 'Roeland 2.0', False, False, False, False),
            (23, 'Gobelijn 5', True, False, False, False),
            (24, 'Speedybot', True, False, False, False),
            (25, 'Trolbot', False, False, False, True),
            (26, 'Mr. Dirk', False, False, False, False),
            (30, 'Johnny Cache', False, False, False, False),
            (32, 'Brecht 3000', False, False, False, False),
            (0, 'Steamer', False, False, True, True),
        )
        
        for team_number, name, is_high_school, is_ieee, is_houserobot, is_ugent in ROBOTS:
            r = Robot()
            r.team_number = team_number
            r.name = name
            r.is_ieee = is_ieee
            r.is_high_school = is_high_school
            r.is_ugent = is_ugent
            r.type = 1 if is_houserobot else 0
            r.save()
            self.stdout.write('Created robot %s (team %d)\n' % (name, team_number))
