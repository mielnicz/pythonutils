#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Generates Gource config file from git submodules, starts Gource.
# Place to /usr/local/bin and run at the main repository root.
#
# (c) 2010 Mikael Lammentausta
# License is the same as Gource (GPLv3)

import sys
import os
import re
from git import *

class GourceCustomLog():
    """
   If you want to use Gource with something other than the supported systems, there is a pipe ('|') delimited custom log format:

      timestamp - A unix timestamp of when the update occured.
      username  - The name of the user who made the update.
      type      - Single character for the update type - (A)dded, (M)odified or (D)eleted.
      file      - Path of the file updated.
      colour    - A colour for the file in hex (FFFFFF) format. Optional.
    """
    file = None
    entries = []

    def __init__(self,filename,**kwargs):
        self.file = open(filename,'w+')

    def __del__(self):
        if self.file and not self.file.closed:
            self.file.close()

    @staticmethod
    def __update_type(commit,file):
        """Single character for the update type - (A)dded, (M)odified or (D)eleted.
        This should be in GitPython, I could not find a method there.
        """
        # if no parents, everything is new
        if not commit.parents:
            return 'A'

        # if file is not found in parent tree..
        elif not file in map(
            lambda blob:
                blob.path
            , commit.parents[0].tree.traverse()
            ):
            return 'A' # added

        # if file is not found in tree..
        elif not file in map(
            lambda blob:
                blob.path
            , commit.tree.traverse()
            ):
            return 'D' # deleted

        else:
            return 'M' # modified

    @staticmethod
    def __entry(commit,file,prefix=None):
        """Log entry.
        @returns a tuple of (timestamp, username, type, file)
        """
        if prefix:
            _file = '/'.join([prefix,file])
        else:
            _file = file
        # Author and type may give errors, substitute
        author = "unknown"
        try:
          author = str(commit.author)
        except:
          pass
        update = 'M'
        try:
          update = GourceCustomLog.__update_type(commit,file)
        except:
          pass
        return (
            commit.authored_date,
            author,
            update,
            _file,
            #'colour'
        )

    @staticmethod
    def __format(entry):
        # Handle email addresses with weird unicode characters
        try:
          str(entry[1])
        except:
          entry = ( entry[0], "unknown", entry[1], entry[2])
        # Create the log entry
        return '|'.join(map(str, entry)) + "\n"

    def append(self,commit,**kwargs):
        for file in commit.stats.files:
            self.entries.append(
                GourceCustomLog.__entry(commit,file,**kwargs)
                )

    def sort_by_timestamp(self):
        self.entries = sorted(self.entries, key=lambda entry: entry[0])

    def write(self):
        for entry in self.entries:
            try:
                self.file.write(GourceCustomLog.__format(entry))
            except:
                print "Error! Entry @ %i, %s" % (entry[0], entry[3])

def find_repos():
  urls = dict()
  repos = list()
  # List of repos found
  def walker(arg, dirname, names):
    # We are only interested in directories containing a '.git' subdir
    path, child = os.path.split(dirname)
    if child <> ".git":
      return
    # Get the repo
    repo = Repo(path)
    print "Found repository at '%s'" % os.path.relpath(path)
    # Find the URL to the remote (so we can skip duplicates)
    try:
      remote = repo.remote()
      print "  %s" % remote.url
      if urls.has_key(remote.url):
        return # Already have this one
      urls[remote.url] = True
    except:
      pass # Do nothing, assume this is a local repo only
    repos.append(os.path.relpath(path))
  # Scan for all .git directories below the working directory
  os.path.walk(os.getcwd(), walker, None)
  return repos

def create_log(**kwargs):
    log = GourceCustomLog(**kwargs)

    # Walk through all the directories we were given
    for path in kwargs['repos']:
      repo = Repo(path)
      print "Repository: " + str(repo)
      # Get the commits
      commits = repo.iter_commits('master')
      for commit in commits:
        if path == ".":
          log.append(commit)
        else:
          log.append(commit, prefix=path)

    # Sort and write the log
    log.sort_by_timestamp()
    log.write()

def create_conf(filename, logfile):
    file = open(filename,'w')
    file.write('[gource]\n')
    file.write('  path=%s\n' % logfile)
    file.close()

def launch_gource(configfile):
    os.system('''gource --load-config %s -s 0.01''' % configfile)

if '__main__' == __name__:
    logfilename = 'submodules.log'
    if len(sys.argv) == 2:
      logfilename = sys.argv[1]
    create_log(filename=logfilename, repos=find_repos())
#    create_conf(filename='gource.conf', logfile=logfilename)
    #launch_gource(configfile='gource.conf')

