"""
Process the registrations CSV file and enter all robots into the competition software.
"""

import os

# Set the DJANGO_SETTINGS_MODULE environment variable.
os.environ['DJANGO_SETTINGS_MODULE'] = "robotcomp.settings"

import csv
import urllib2
from PIL import Image, ImageFile, ImageOps


     
from django.core.files import File
from django.core.files.base import ContentFile
from cStringIO import StringIO

from robots import models

REGISTRATIONS_PATH = "WELEK robotcompetitie- wedstrijdregistratie 2014 (Responses) - Form Responses.csv" # registraties.csv"
PLACEHOLDER_IMAGE_PATH = "placeholder.jpg"
HOUSEROBOT_IMAGE_PATH = "huisrobot.jpg"
AVATAR_SIZE = 300 # in pixels

# ['Timestamp', 'voornaam', 'achternaam', 'e-mailadres', 'Instelling', 'Studierichting', 'Jaar', 'IEEE-lid?', 'Ik doe mee in het kader van een vak', 'voornaam', 'achternaam', 'e-mailadres', 'Instelling', 'Studierichting', 'Jaar', 'IEEE-lid?', 'Ik doe mee in het kader van een vak', 'voornaam', 'achternaam', 'e-mailadres', 'Instelling', 'Studierichting', 'Jaar', 'IEEE-lid?', 'Ik doe mee in het kader van een vak', 'voornaam', 'achternaam', 'e-mailadres', 'Instelling', 'Studierichting', 'Jaar', 'IEEE-lid?', 'Ik doe mee in het kader van een vak', 'Naam van de robot', 'Link naar avatar']

IDX_NAME = 33 # 29
IDX_AVATAR_LINK = 34 # 30
IDCS_IEEE = [7, 15, 23, 31] # [7, 14, 21, 28]
# IDCS_INSTELLING = [4, 11, 18, 25]
# IDCS_BACHELOR = [6, 13, 20, 27]
IDCS_HIGH_SCHOOL = [6, 14, 22, 30]
IDCS_CREDITS = [8, 16, 24, 32]
IDCS_FIRSTNAME = [1, 9, 17, 25] # [1, 8, 15, 22] # to detect if they were filled out. If the first name is filled out, we assume all the rest is there as well.

reader = csv.reader(file(REGISTRATIONS_PATH, 'r'))

for i, row in enumerate(reader):
    if i == 0: # header row, insert house robot instead
        name = "Kenny"
        is_ieee = True
        for_credits = False
        is_high_school = False
        robot_type = 1 # house robot
        avatar_url = ""
    else:
        robot_type = 0 # participating robot
        name = row[IDX_NAME]
        print "Processing %s" % name
        avatar_url = row[IDX_AVATAR_LINK].strip()

        ieee, credits, high_school = [], [], []
        for k in xrange(4):
            if row[IDCS_FIRSTNAME[k]].strip() != "":
                ieee.append(row[IDCS_IEEE[k]])
                credits.append(row[IDCS_CREDITS[k]])
                high_school.append(row[IDCS_HIGH_SCHOOL[k]])

        is_ieee = any(s == 'Ja' for s in ieee)
        for_credits = all(s == 'Ja' for s in credits)
        is_high_school = all(("secundair" in s) for s in high_school)

        print "  IEEE: %s" % is_ieee
        print "  All for credits: %s" % for_credits
        print "  All in high school: %s" % is_high_school
    
    # if URL is empty, use placeholder.
    print "  downloading and resizing/cropping avatar..."
    if robot_type == 1:
        in_stream = open(HOUSEROBOT_IMAGE_PATH)
    elif avatar_url == "":
        in_stream = open(PLACEHOLDER_IMAGE_PATH)
    else:
        in_stream = urllib2.urlopen(avatar_url)

    parser = ImageFile.Parser()
    while True:
        s = in_stream.read(1024)
        if not s:
            break
        parser.feed(s)

    in_image = parser.close()
    # convert to RGB to avoid error with png and tiffs
    if in_image.mode != "RGB":
        in_image = in_image.convert("RGB")

    thumb = ImageOps.fit(in_image, (AVATAR_SIZE, AVATAR_SIZE), Image.ANTIALIAS)
    # thumb.show()

    img_temp = StringIO()
    thumb.save(img_temp, format='PNG')
    img_temp.seek(0)

    filename = os.path.basename(avatar_url)
    file_object = ContentFile(img_temp.read())

    print "  creating robot object"
    robot = models.Robot()
    robot.team_number = i
    robot.name = name
    robot.is_ieee = is_ieee
    robot.for_credits = for_credits
    robot.is_high_school = is_high_school
    robot.type = robot_type
    robot.avatar.save(filename, file_object, save=True)
    robot.save()

    print "  created robot %s (team %d)" % (name, i)

