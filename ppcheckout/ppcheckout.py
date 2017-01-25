#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""ppcheckout

Usage:
  ppcheckout [options] <projectid> [<projectname>]
  ppcheckout -h | --help
  ppcheckout --version

Automates the initial setup of a pgdp.net post processing project.

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
import shlex
import subprocess


__appname__ = "ppcheckout"
__author__  = "David Maranhao"
__license__ = "MIT"
__version__ = "0.1.0" # MAJOR.MINOR.PATCH | http://semver.org


def main():
    args = docopt(__doc__, version="ppcheckout v{}".format(__version__))

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
    projectId = re.search("(projectID[A-Fa-f0-9]+)",projectId).group(1)
    logging.info("Checking out project {} to {}".format(projectId,projectName))

    # Parse project page for title and author
    logging.info("Parsing project page for {}".format(projectId))
    projectURL = "http://www.pgdp.net/c/project.php?id={}".format(projectId)
    browser = RoboBrowser()
    browser.open(projectURL)
    projectInfo = browser.find('table',id='project_info_table')
    title = projectInfo.find('b',text="Title").parent.next_sibling.string
    author = projectInfo.find('b',text="Author").parent.next_sibling.string

    if not projectName:
        projectName = generateProjectName(title)

    # Download project files
    logging.info("Downloading project files for '{}' by {}".format(title,author))
    imagesURL = "http://www.pgdp.net/c/tools/download_images.php?projectid={}&dummy={}images.zip".format(projectId, projectId)
    textURL = "http://www.pgdp.net/projects/{}/{}.zip".format(projectId, projectId)
    downloadFile(imagesURL,"images.zip")
    downloadFile(textURL,"text.zip")

    # Init project skeleton
    logging.info("Building project base structure")
    srcDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)),"_NEW_PROJECT_TEMPLATE"))
    dstDir = os.path.abspath(projectName)
    try:
        shutil.copytree(srcDir, dstDir)
    except FileExistsError as e:
        logging.error("{} - {}".format(e.filename,e.strerror))


    # Copy/unzip project files
    projectPath = os.path.abspath(projectName)
    projectFilePath = os.path.join(projectPath,"{}-src.txt".format(projectName))
    print(projectPath)
    print(projectFilePath)
    logging.info("Adding project files")
    zipText = zipfile.ZipFile("text.zip","r")
    zipImages = zipfile.ZipFile("images.zip","r")
    zipText.extractall(path=os.path.join(projectPath,"originals"))
    zipImages.extractall(path=os.path.join(projectPath,"pngs"))
    moveFiles(glob.glob(os.path.join(projectPath,"pngs","*.jpg")), os.path.join(projectPath,"originals","illustrations"))
    shutil.copy(os.path.join(projectPath,"originals","{}.txt".format(projectId)),projectFilePath)
    moveFiles(glob.glob(os.path.abspath("*.zip")), os.path.join(projectPath,"originals"))

    try:
        os.remove(os.path.join(projectPath,"originals","{}_TEI.txt".format(projectId)))
    except OSError as e:
        logging.error("{} - {}".format(e.filename,e.strerror))

    # Convert illustrations
    files = glob.glob(os.path.join(projectPath,"originals","illustrations","*.jpg"))
    logging.info("Converting illustrations to lossless format")
    for f in files:
        shellCommand("mogrify -format png {}".format(f))

    # Update Makefile with project name
    prependText('PROJECTNAME={}\n'.format(projectName), os.path.join(projectPath,"Makefile"))

    # Initialize git repo
    shellCommand("git init",cwd=projectPath)
    shellCommand("git add {}-src.txt".format(projectName),cwd=projectPath)
    shellCommand('git commit -m "ppcheckout: Initial version"',cwd=projectPath)

    # Convert to UTF-8
    shellCommand("recode ISO-8859-1..UTF-8 {}".format(os.path.join(projectPath,"{}-src.txt".format(projectName))))
    prependText('', projectFilePath) # convert to native line endings
    shellCommand('git commit -am "ppcheckout: Convert to UTF-8, native line endings"',cwd=projectPath)

    # Add title
    titleTxt = ".dt {}, by {}—A Project Gutenberg eBook\n".format(title,author)
    prependText(titleTxt, projectFilePath)
    shellCommand('git commit -am "ppcheckout: Add title"',cwd=projectPath)

    return


def prependText( s, fn ):
    with open(fn,'r') as f:
        t = f.read()
    with open(fn,'w') as f:
        f.write(s)
        f.write(t)


def shellCommand( s, cwd=None ):
    logging.info("Executing shell command:\n{}".format(s))
    cl = shlex.split(s)
    proc=subprocess.Popen(cl,cwd=cwd)
    proc.wait()
    if( proc.returncode != 0 ):
        logging.error("Command failed: {}".format(s))


def moveFiles( files, dest ):
    for f in files:
        logging.info("Moving file {} to {}".format(f,dest))
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
    name = re.sub("P[123]","",s)
    name = name.lower()
    name = re.sub(" +[&] +","-",name)
    name = re.sub("[^a-z0-9- ]","",name)
    name = re.sub("^(the |\w )","",name)
    name = re.sub("^ +","",name)
    name = re.sub(" {2,}","",name)
    name = re.sub(" ","-",name)
    name = re.sub("-{2,}","-",name)
    name = re.sub("(^-|-$)","",name)
    words = name.split("-")
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






















