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

#ls -p | grep "/" > listofsubjects_2.txt

subjectlist = open(subject_File,'r')

for eachSubject in subjectlist:
#    print eachSubject
    k = eachSubject.rfind("/")
    dicom_path = eachSubject[:k]+"/dicom"

    print dicom_path
    print ("sorting...")

    cmd = 'python %s/dicom_header_divider_3_link_dcm2nii.py %s/%s' % (script_dir,root_subject_directory,dicom_path)
    print (cmd)
    system(cmd)

#    cmd = 'python %s/motion_correction.py %s/%s/*DTI*' % (script_dir,root_subject_directory,eachSubject[:k])
#    print (cmd)
#    system(cmd)

subjectlist.close()
