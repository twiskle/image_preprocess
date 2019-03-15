#python script to output any subjects with missing DTI dicom files (which causes the issue with motion correction)

import os
from os import system,listdir,path
from subprocess import Popen, PIPE

import shlex,sys,subprocess
import re

input_dicom_dir = sys.argv[1]

if (not path.isdir(input_dicom_dir)):
    print "Could not locate the input directory. Please verify"
    exit()

listofproperDTI = path.join(input_dicom_dir,"listofproperDTI.txt")
cmd = 'ls '+input_dicom_dir+'/*/*DTI*/nifti/DWI_CORRECTED.nhdr > '+listofproperDTI
system(cmd)

listofsubjects = path.join(input_dicom_dir,"listofsubjects_3.txt")
cmd = 'ls -p '+input_dicom_dir+'| grep "/" > '+listofsubjects
system(cmd)


#MAIN
d_str = "/"
subjectlist = open(listofsubjects,'r')

output_textfile = open(input_dicom_dir+'/subjects_with_missing_DTI_dicom.txt','w')


for eachSubject in subjectlist:
	k = eachSubject.rfind(d_str)
	eachSubject = eachSubject[:k]
	if not eachSubject in open(listofproperDTI).read():
            print "missing DTI dicom: "+eachSubject
    	    output_textfile.write(eachSubject+"\n")

output_textfile.close()
subjectlist.close()

print "DONE: check for missing DTI dicom at: "+input_dicom_dir
