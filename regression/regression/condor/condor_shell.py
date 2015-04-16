#!/usr/bin/python

import optparse
import os
import sys

user = os.getenv("USER")
condor_write_base = '/afs/cs.wisc.edu/p/multifacet/condor_stats/'+user

notify_user = '%s@cs.wisc.edu' % user
uwmf_requirements = '(Memory > 2900) && (Arch == "X86_64") && (OpSys == "LINUX") && (FileSystemDomain == "cs.wisc.edu" || FileSystemDomain == ".cs.wisc.edu") && (ClusterGeneration>=5) && (Machine != "ale-01.cs.wisc.edu") && (Machine != "ale-02.cs.wisc.edu") && (Machine != "clover-01.cs.wisc.edu") && (Machine != "clover-02.cs.wisc.edu") && (IsComputeCluster == True) && (IsDedicated == True)'

templatestart = \
'\
rank = TARGET.Memory\n\
universe = vanilla\n\
notification = Error\n\
+IsCommittedJob = TRUE\n\
notify_user = %s\n\
getenv = True\n\
requirements = %s\n\
\n\
' % (notify_user, uwmf_requirements)

def runCommand(command, override = False):
    if options.debug and not override:
        print command
    else:
        os.system(command)

def getFilePrefix(directory):
    files = os.listdir(directory)
    files = [int(f[3:]) for f in files if f.startswith('out')]
    files.sort()
    mn = 0
    for i in files:
        if i == mn:
            mn += 1
        else:
            break
    return 'out%010d' % mn

parser = optparse.OptionParser()
parser.add_option("--command", "-c", action="store", help="The command to submit to condor")
parser.add_option("--debug", "-d", action="store_true", default=False, help="Just print commands")
parser.add_option("--output", "-o", action="store", help="Redirect program output to this directory")
(options, args) = parser.parse_args()

if len(args):
    print "ERROR: Script doesn't take any positional arguments"
    sys.exit(-1)

if not options.command:
    print "ERROR: Must specify the command to execute with '-c'"
    sys.exit(-1)

currentdir = os.getcwd()

# Get unique prefix for files
fileprefix = getFilePrefix(condor_write_base)
programoutfile = os.path.join(condor_write_base, fileprefix, 'std.out')

programoutdir = os.path.dirname(programoutfile)
print programoutdir
if not os.path.exists(programoutdir):
    mkdircmd = 'mkdir -p %s' % programoutdir
    runCommand(mkdircmd)

# Generate the bash script
scriptname = fileprefix[3:]+'script'
scriptfilename = os.path.join(programoutdir, scriptname)
print "SHELL: submit wrapper script: %s" % scriptfilename
scriptfile = open(scriptfilename, 'w')
scriptfile.write('#!/bin/bash\n')
scriptfile.write('%s\n' % options.command)
# scriptfile.write('rm -f %s\n' % scriptfilename)
scriptfile.close()
chmodcmd = 'chmod +x %s' % scriptfilename
runCommand(chmodcmd)

hostname = os.getenv('HOSTNAME')

# Generate the submit script
submitname = 'submit'
submitfilename = os.path.join(programoutdir, submitname)
print "SHELL: submit file: %s" % submitfilename
submitfile = open(submitfilename, 'w')
submitfile.write(templatestart)
submitfile.write('initialdir = %s\n' % programoutdir)
submitfile.write('executable = %s\n' % scriptfilename)
logfilename = os.path.join(programoutdir, 'log')
print "SHELL: log file: %s" % logfilename
submitfile.write('log = %s\n' % logfilename)
submitfile.write('output = %s\n' % programoutfile)
submitfile.write('error = %s\n' % programoutfile)
submitfile.write('queue\n')
submitfile.close()

# Submit the job
submitcmd = 'condor_submit %s' % submitfilename
runCommand(submitcmd)

# Wait and copy
waitcmd = "condor_wait %s; " % logfilename
copycmd = "mv -f %s/* %s; " % (programoutdir, currentdir)
deletecmd = 'rm -rf %s; rm -f submit script; ' % programoutdir
runCommand('nohup sh -c "%s" > /dev/null &' % (waitcmd+copycmd+deletecmd))

