#python script to look at dicom header and then sort

#from gtsutils import exec_cmd

import os
from os import system,listdir,path
from subprocess import Popen, PIPE

import shlex,sys,subprocess
import re

input_dicom_dir = sys.argv[1]

if (not path.isdir(input_dicom_dir)):
    print "Could not locate the input directory. Please verify"
    exit()

cmd = 'rm %s/../dicom_files_checker_output.txt' % (input_dicom_dir)
system(cmd)

#cmd = 'rm -rf %s/../SN_*' % (input_dicom_dir)
#system(cmd)

#current directory
current_DIR = os.getcwd()

SN_list = []
file_checker = []
counter = 1
for fn in sorted(listdir(input_dicom_dir)):

    if fn.endswith(".dcm"):

        #print (str(counter) + ': looking at ' + fn + '...')

        #cmd = 'gdcmraw -i %s -t 8,103e -o header_temp.log' % (fn)

        #Series Number
        cmd = 'gdcmdump -i %s | grep "0020,0011"' % (input_dicom_dir + '/' + fn)
        #exec_cmd(cmd,display=False)
        line_SN = Popen(cmd,stdout=PIPE, shell=True)
        (out,err) = line_SN.communicate()

        #print (out)
        str1 = "[";
        str2 = "]";
        SN = out[out.index(str1)+1:out.index(str2)]
        #SN=SN.replace(" ","")
        SN = re.sub('\W+','', SN )
        #print (SN)

        #Title
        cmd = 'gdcmdump -i %s | grep "0008,103e"' % (input_dicom_dir + '/' + fn)
        line_TITLE = Popen(cmd,stdout=PIPE, shell=True)
        (out,err) = line_TITLE.communicate()

        #print (out)
        str1 = "[";
        str2 = "]";
        TITLE = out[out.index(str1)+1:out.index(str2)]
        #TITLE=TITLE.replace(" ","")
        TITLE = re.sub('\W+','', TITLE )
        #print (TITLE)

	    #sort based on different series number (create new folder based on the title -- series title without space)

#        cmd = 'mkdir -p %s/../SN_%s' % (input_dicom_dir, SN)
        cmd = 'mkdir -p %s/../%s' % (input_dicom_dir, TITLE)
        system(cmd)

        cmd = 'mkdir -p %s/../%s/dicom' % (input_dicom_dir, TITLE)
        system(cmd)

        newPath = input_dicom_dir + '/../' + TITLE + '/dicom'

# Create symbolic link
        if input_dicom_dir.endswith("/"):
            k = input_dicom_dir.rfind("/",0,len(input_dicom_dir)-1)
        else:
            k = input_dicom_dir.rfind("/")
        originalFolder = input_dicom_dir[k+1:]

        cmd = 'ln -s ../../%s/%s %s' % (originalFolder,fn, newPath)
        system(cmd)

        #record down the path of first file for checking later
        if SN not in SN_list:
            SN_list.append(SN)
            file_checker.append(newPath)

        counter += 1

#perform dcm2nii the images in each directory
for num in range(len(SN_list)):

    path = file_checker[num]

    cmd = 'dcm2nii -d N -e N -f Y -i N -p N -o %s/../. %s/*.dcm' % (path,path)

    #print ('->'+cmd)
    system(cmd)


TotalFiles=0;
#after for loop, count the files to make sure the number of files match with the series number!!! 2728 for example
for num in range(len(SN_list)):

    path = file_checker[num]
    firstFilePath = next(path+'/'+f for f in listdir(path))

    #Images in Acquisition
    '''
    cmd = 'gdcmdump -i %s | grep "0020,1002"' % (firstFilePath)
    line_IMGNUM = Popen(cmd,stdout=PIPE, shell=True)
    (out,err) = line_IMGNUM.communicate()

    str1 = "[";
    str2 = "]";
    IMGNUM = out[out.index(str1)+1:out.index(str2)]
    IMGNUM = re.sub('\W+','', IMGNUM )
    '''

    cmd = 'gdcmdump -i %s | grep "0025,1007"' % (firstFilePath)
    line_IMGNUM = Popen(cmd,stdout=PIPE, shell=True)
    (out,err) = line_IMGNUM.communicate()

    str1 = "SL";
    IMGNUM = out[out.index(str1)+3:out.index(str1)+8]
    IMGNUM = re.sub('\W+','', IMGNUM )

    #Images in the directory
#    cmd = 'find %s -type f | wc -l' % (path)
    cmd = 'find %s -type l | wc -l' % (path)

    numFiles = Popen(cmd,stdout=PIPE, shell=True)
    (numOfFiles,err) = numFiles.communicate()

    #print ('Number of Images in Acquisition in ' + firstFilePath + ' is ' + IMGNUM)
    #print ('Number of Files in the directory of ' + str(path) + ' (SN_' + str(SN_list[num]) + ') is ' + numOfFiles)

    #rename the folder to "DTI" if number of files exceeds 1000
    if (int(numOfFiles) > 1000 and int(IMGNUM) > 1000):

        #get number of direction
        cmd = 'gdcmdump -i %s | grep "0019,10e0"' % (firstFilePath)
        line_DIR = Popen(cmd,stdout=PIPE, shell=True)
        (out,err) = line_DIR.communicate()

        str1 = "[";
        str2 = ".";
        DIR = out[out.index(str1)+1:out.index(str2)]
        DIR = re.sub('\W+','', DIR )

        #get the folder name
        last_k = path.rfind("/")
        second_last_k = path.rfind("/",0,last_k-1)
        newPath = path[:second_last_k+1]+"DTI"+DIR
        cmd = 'mv %s %s' % (path[:last_k],newPath)
        system(cmd)

    if (int(numOfFiles) != int(IMGNUM)):
        text_file = open(input_dicom_dir+'/../dicom_files_checker_output.txt','a')
        text_file.write('number of files in SN_' + str(SN_list[num]) + '\n')
        text_file.write('# of Images in Acq: ' + IMGNUM + ' and\n' +
            '# of Images in directory of SN_' + str(SN_list[num]) + ': ' + numOfFiles + '\n\n')
        text_file.close()

    TotalFiles += int(numOfFiles)

text_file = open(input_dicom_dir+'/../dicom_files_checker_output.txt','a')
text_file.write('Total count of files examined is: ' + str(TotalFiles) + '\n')
cmd = 'find %s -type f | wc -l' % (input_dicom_dir)
numFiles = Popen(cmd,stdout=PIPE, shell=True)
(numDICOM,err) = numFiles.communicate()
text_file.write('Total number of DICOM files is: ' + str(numDICOM))
text_file.close()
print "DONE: sorting files"
