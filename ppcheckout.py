#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""ppcheckout

Usage:
  ppcheckout [options] <projectid> [<projectname>]
  ppcheckout -h | --help
  ppcheckout --version

Translates pgdp.org formatted text files into ppgen syntax.

Examples:
  ppcheckout projectID509579cf64be8
  ppcheckout projectID509579cf64be8 proj-name

Options:
  -q, --quiet           Print less text.
  -v, --verbose         Print more text.
  -h, --help            Show help.
  --version             Show version.
"""

from docopt import docopt
from robobrowser import RoboBrowser
import urllib
import logging
import re
import shutil
import os
import zipfile


VERSION="0.1.0" # MAJOR.MINOR.PATCH | http://semver.org

def main():
    args = docopt(__doc__, version="ppcheckout v{}".format(VERSION))

    # Configure logging
    logLevel = logging.INFO #default
    if args['--verbose']:
        logLevel = logging.DEBUG
    elif args['--quiet']:
        logLevel = logging.ERROR

    logging.basicConfig(format='%(levelname)s: %(message)s', level=logLevel)
    logging.debug(args)

    # Process command line arguments
    projectId = args['<projectid>']
    projectName = args['<projectname>']

    # Parse project page for title and author
    projectURL = "http://www.pgdp.net/c/project.php?id={}".format(projectId)
    browser = RoboBrowser()
    browser.open(projectURL)
    projectInfo = browser.find('table',id='project_info_table')
    title = projectInfo.find('b',text="Title").parent.next_sibling.string
    author = projectInfo.find('b',text="Author").parent.next_sibling.string
    print(title)
    print(author)

    if not projectName:
        projectName = generateProjectName(title)

    print(projectId)
    print(projectName)

    # Download project files
    goodWordsURL = "http://www.pgdp.net/projects/{}/good_words.txt".format(projectId)
    badWordsURL = "http://www.pgdp.net/projects/{}/bad_words.txt".format(projectId)
    imagesURL = "http://www.pgdp.net/c/tools/download_images.php?projectid={}&dummy={}images.zip".format(projectId, projectId)
    textURL = "http://www.pgdp.net/projects/{}/{}.zip".format(projectId, projectId)

    try:
        urllib.request.urlretrieve(goodWordsURL,"good_words.txt")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            logging.warning("No good_words.txt at {}".format(goodWordsURL))
            pass
        else:
            raise

    try:
        urllib.request.urlretrieve(badWordsURL,"bad_words.txt")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            logging.warning("No bad_words.txt at {}".format(badWordsURL))
            pass
        else:
            raise

    try:
        urllib.request.urlretrieve(imagesURL,"images.zip")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            logging.error("HTTP Error 404: Not Found {}".format(imagesURL))
            pass
        else:
            raise

    try:
        urllib.request.urlretrieve(textURL,"text.zip")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            logging.error("HTTP Error 404: Not Found {}".format(textURL))
            pass
        else:
            raise

    # Init project skeleton
    srcDir = os.path.abspath("_NEW_PROJECT_TEMPLATE")
    dstDir = os.path.abspath(projectName)
    shutil.copytree(srcDir, dstDir)

    return


def generateProjectName( s ):
    name = s.lower()
    name = re.sub(" +[&] +","-",name)
    name = re.sub("[^a-z0-9- ]","",name)
    name = re.sub("^(the |\w )","",name)
    name = re.sub("^ +","",name)
    name = re.sub(" {2,}","",name)
    name = re.sub(" ","-",name)
    name = re.sub("-{2,}","-",name)
    words = name.split("-")
    #print(words)
    #print(min(3,len(words)))
    #print(words[0:min(3,len(words))])
    #print("-".join(words[0:min(3,len(words))]))
    print(len(name))
    wc = len(words)
    maxNameLength = 30
    while( len(name) > maxNameLength and wc > 0 ):
        name = "-".join(words[0:min(wc,len(words))])
        wc = wc-1

    return name

if __name__ == "__main__":
    main()





#inputs
#projectID or project URL
#local project name (used for project folder name, naming of src file..)



#download
#good_words.txt (http://www.pgdp.net/projects/$PROJECTID/good_words.txt)
#bad_words.txt (http://www.pgdp.net/projects/$PROJECTID/bad_words.txt)
#zipped images (http://www.pgdp.net/c/tools/download_images.php?projectid=$PROJECTID&dummy=$PROJECTIDimages.zip
#zipped text (http://www.pgdp.net/projects/$PROJECTID/$PROJECTID.zip)

#hit checkout button
#Not sure about this.. cant accidentally check back in. User will need to visit project page for projectID anyways.

#create project skeleton
#$PROJECTID/
#    pngs/
#        001.png
#        ...
#    originals/
#        illustrations/
#            001.png
#            ...
#        good_words.txt
#        bad_words.txt
#        $PROJECTID.txt
#        $PROJECTID_comments.html
#    images/
#        001.jpg
#    good_words.txt
#    bad_words.txt
#    $PROJECTID-src.txt
#    Makefile
#    notes.txt

#create project folders
#copy word lists to originals/
#unzip text to originals/
#unzip images to illustrations/
#move .png page scans to ../pngs/ (how to differ these from illustrations reliably?)
#convert remaining images in illustrations/ to lossless format (like .png or .tif)
#- Unzip files
#   - Unzip all project files into project/originals
#   - Move files into appropriate directories
#- Copy proofed text from originals to project_root/projectname-src.txt
#- Update PROJECTNAME in Makefile
#- Set up version control for project
#   - git init
#   - git add projectname-src.txt
#   - git commit -m "Initial version"

# prepend title line to project text
# print .dt line for user to verify name is set correctly
#   - git commit -am "Add title"






















