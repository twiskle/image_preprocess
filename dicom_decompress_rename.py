#from os import sys, listdir, path
import os, re
from os import sys,path,system
from glob import glob
import numpy as np

try:
#if len(sys.argv) > 2 or len(sys.argv) == 0:
    subject_File = sys.argv[1]
except:
    print "Incorrect input(s). Please verify" 
    print "1st input: file of list of directory of subjectID"
#    print "2nd input: path of TN_MS (default: current path)"
    exit()

script_dir = path.dirname(path.realpath(__file__))


#MAIN

k2 = subject_File.rfind("/")
root_subject_directory = subject_File[:k2]

#ls -p | grep "/" > listofsubjects.txt

subjectlist = open(subject_File,'r')

for eachSubject in subjectlist:
    k = eachSubject.rfind("/")
    eachSubject = eachSubject[:k]
    print "****************************************************"
    print eachSubject
    print ("decompressing...")

    cmd = 'python %s/dicom_decompress.py %s/%s' % (script_dir,root_subject_directory,eachSubject)
    print cmd
    system(cmd)

    print ("renaming folder...")
    cmd = 'python %s/dicom_folder_rename.py %s/%s' % (script_dir,root_subject_directory,eachSubject)
    print cmd
    system(cmd)

subjectlist.close()
