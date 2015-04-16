#!/usr/bin/env python

import itertools
import json

from os import path
import pprint
import subprocess
import sys

import argparse

null = open('/dev/null', 'wr')

def setupArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['restore', 'retrieve'], help='command to run')
    parser.add_argument('-f', '--file', default=None)
    parser.add_argument('-d', '--base-dir', default='.')
    parser.add_argument('--force', help='Force retrieve even if repos are dirty', action='store_true', default=False)
    return parser

def checkClean(repo):
    return subprocess.check_output(['hg', 'status', '-q'], cwd=repo).strip()

def getRevision(repo):
    try:
        return subprocess.check_output(['hg', 'identify', '-r', 'qparent', '-i'], cwd=repo, stderr=null).strip()
    except subprocess.CalledProcessError:
        return subprocess.check_output(['hg', 'identify', '-i'], cwd=repo).strip()
    
def getPatchRevision(repo, force):
    data = {}
    
    try:
        data['revision'] = subprocess.check_output(['hg', 'identify', '--mq', '-i'], cwd=repo, stderr=null).strip().strip('+')
    except subprocess.CalledProcessError:
        return
        
    try:
        data['qtop'] = subprocess.check_output(['hg', 'qtop'], cwd=repo, stderr=null).strip()
    except subprocess.CalledProcessError as e:
        # no patches applied
        assert(e.returncode == 1)
        return
        
    dirty = subprocess.check_output(['hg', 'status', '-q', '--mq'], cwd=repo).strip()
    if dirty:
        print repo, "patches not clean"
        print dirty
        while not force:
            ans = raw_input("Continue? [Ny]")
            if not ans or ans.lower() == 'n':
                sys.exit(1)
            elif ans.lower() == 'y':
                break
    data['dirty'] = bool(dirty)
    if dirty:
        data['diff'] = subprocess.check_output(['hg', 'diff', '--mq'], cwd=repo)
    
    qq = subprocess.check_output(['hg', 'qqueue', '-l'], cwd=repo).strip()
    for queue in qq.split('\n'):
        if queue.find('active') != -1:
            data['queue'] = queue.replace('(active)', '').strip()
            break
    try:        
        data['qtop'] = subprocess.check_output(['hg', 'qtop'], cwd=repo, stderr=null).strip()
    except subprocess.CalledProcessError as e:
        assert(e.returncode == 1)
        return
    
    return data
    
def getDiff(repo):
    return subprocess.check_output(['hg', 'diff'], cwd=repo)

def retrieve(baseDir, force):
    repos = {'gem5':{}, 'gem5-gpu':{}, 'gpgpu-sim':{}}
    
    if not path.isdir(baseDir) or any([not path.isdir(path.join(baseDir, i)) for i in repos]):
        print "Bad base directory provided", baseDir
        sys.exit(1)

    for repo,data in repos.iteritems():
        dirty = checkClean(path.join(baseDir, repo))
        if dirty:
            print repo, "not clean"
            print dirty
            while not force:
                ans = raw_input("Continue? [Ny]")
                if not ans or ans.lower() == 'n':
                    sys.exit(1)
                elif ans.lower() == 'y':
                    break
        
        data['revision'] = getRevision(path.join(baseDir, repo))
        data['patch repo'] = getPatchRevision(path.join(baseDir, repo), force)
        data['dirty'] = bool(dirty)
        if dirty:
            data['diff'] = getDiff(path.join(baseDir, repo))

    return repos
        
def checkCleanPatches(repo, data):
    thisDirty = bool(subprocess.check_output(['hg', 'status', '-q', '--mq'], cwd=repo).strip())
    
    if data['queue'] != 'patches':
        other = path.join(repo, '.hg/patches-'+data['queue'])
        try:
            otherDirty = bool(subprocess.check_output(['hg', 'status', '-q'], cwd=other).strip())
        except subprocess.CalledProcessError as e:
            print "Cannot update patch repo", data['queue'], "in", repo
            exit(1)
        return thisDirty or otherDirty
    else:
        return thisDirty
        
def applyPatch(dir, diff):
    p = subprocess.Popen(['patch'], stdin=subprocess.PIPE, cwd=dir, stdout=null)
    p.communicate(diff)
    p.wait()
    if p.returncode != 0:
        print "Error applying the diff"
        exit(1)
        
def updatePatchRepo(repo, data):
    ret = subprocess.call(['hg', 'qqueue', data['queue']], cwd=repo, stderr=null)
    qq = subprocess.check_output(['hg', 'qqueue', '-l'], cwd=repo).strip()
    for queue in qq.split('\n'):
        if queue.find('active') != -1:
            qq = queue.replace('(active)', '').strip()
            break
    if ret != 0 and data['queue'] != qq:
        subprocess.check_call(['hg', 'qpop', '-a'], cwd=repo, stdout=null)
        subprocess.check_call(['hg', 'qqueue', data['queue']], cwd=repo)
    
    subprocess.check_call(['hg', 'update', '--mq', '-r', data['revision']], cwd=repo, stdout=null)
        
    if data['dirty']:
        if data['queue'] == "patches":
            dir = 'patches'
        else:
            dir = 'patches-' + data['queue']
        applyPatch(path.join(repo, '.hg/', dir), data['diff'])
    
def updateRepo(repo, revision):
    subprocess.check_call(['hg', 'qpop', '-a'], cwd=repo, stdout=null)
    subprocess.check_call(['hg', 'update', '-r', revision], cwd=repo, stdout=null)
        
def restore(baseDir, infile):
    with open(infile) as indata:
        repos = json.load(indata)
    
    if not path.isdir(baseDir) or any([not path.isdir(path.join(baseDir, i)) for i in repos]):
        print "Bad base directory provided", baseDir
        sys.exit(1)
        
    for repo,data in repos.iteritems():
        if checkClean(path.join(baseDir, repo)):
            print repo, "is dirty. Cannot restore!"
            sys.exit(1)
        if data['patch repo']:
            if checkCleanPatches(path.join(baseDir, repo), data['patch repo']):
                print repo, "patch repo is dirty. Cannot restore!" 
                exit(1)
            
    for repo,data in repos.iteritems():
        if data['patch repo']:
            updatePatchRepo(path.join(baseDir, repo), data['patch repo'])
        updateRepo(path.join(baseDir, repo), data['revision'])
        if data['patch repo']:
            subprocess.check_call(['hg', 'qpush', data['patch repo']['qtop']], cwd=path.join(baseDir, repo), stdout=null)
        if data['dirty']:
            applyPatch(path.join(baseDir, repo), data['diff'])
    
            

if __name__ == "__main__":
    args = setupArgs().parse_args()
    
    if args.command == 'retrieve':
        repos = retrieve(args.base_dir, args.force)

        if args.file:
            with open(args.file, 'w') as out:
                json.dump(repos, out)
        else:
            pprint.pprint(repos)
    elif args.command == 'restore':
        if not args.file:
            print "file required for restore"
            sys.exit(1)
        restore(args.base_dir, args.file)
