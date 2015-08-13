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
import glob


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
    logging.info("Checking out project {} to {}".format(projectId,projectName))

    # Parse project page for title and author
    logging.info("Parsing project page for {}".format(projectId))
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
    logging.info("Downloading project files for {} by {}".format(title,author))
    imagesURL = "http://www.pgdp.net/c/tools/download_images.php?projectid={}&dummy={}images.zip".format(projectId, projectId)
    textURL = "http://www.pgdp.net/projects/{}/{}.zip".format(projectId, projectId)
    downloadFile(imagesURL,"images.zip")
    downloadFile(textURL,"text.zip")

    # Init project skeleton
    logging.info("Building project base structure")
    srcDir = os.path.abspath("_NEW_PROJECT_TEMPLATE")
    dstDir = os.path.abspath(projectName)
    shutil.copytree(srcDir, dstDir)

    # Copy/unzip project files
    logging.info("Adding project files")
    zipText = zipfile.ZipFile("text.zip","r")
    zipImages = zipfile.ZipFile("images.zip","r")
    zipText.extractall(path=os.path.abspath("{}/originals/".format(projectName)))
    zipImages.extractall(path=os.path.abspath("{}/pngs/".format(projectName)))
    moveFiles(glob.glob(os.path.abspath("{}/pngs/*.jpg".format(projectName))), os.path.abspath("{}/originals/illustrations/".format(projectName)))
    shutil.copy(os.path.abspath("{}/originals/{}".format(projectName,"{}.txt".format(projectId))),os.path.abspath("{}/{}-src.txt".format(projectName,projectName)))

    return


def moveFiles( files, dest ):
    for f in files:
        print(f)
        shutil.move(f,dest)


def downloadFile( src, dest ):
    logging.info("Saving {} to {}".format(src,dest))
    try:
        urllib.request.urlretrieve(src,dest)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            logging.error("Error downloading {}\nHTTP 404: Not Found {}".format(dest,src))
            pass
        else:
            raise


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






















