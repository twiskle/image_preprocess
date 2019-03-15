#python script to decompress all the compressed dicom images (from Coral)


from os import system,listdir,path
from subprocess import Popen, PIPE

import sys


input_dicom_dir = sys.argv[1]

if (not path.isdir(input_dicom_dir)):
    print "Could not locate the input directory. Please verify"
    exit()

dicomFolder = 'dicom'
'''
if ( path.isdir(input_dicom_dir + '/../' + dicomFolder) ):
    cmd = 'rm -rf %s/../%s' % (input_dicom_dir, dicomFolder)
    system(cmd)
'''

cmd = 'mkdir -p %s/%s' % (input_dicom_dir, dicomFolder)
system(cmd)

num=0
for fn in sorted(listdir(input_dicom_dir)):
    fullPath = input_dicom_dir + '/' + fn


    if fn.endswith(".dcm"):
#        print ( 'executing file %s...' % (fn) )

        '''
        num += 1
        cmd = 'gdcmconv %s %s/IM_%s.dcm -w' % (fullPath, input_dicom_dir, num)
        system(cmd)

        cmd = 'mv %s/IM_%s.dcm %s/../%s' % (input_dicom_dir, num, input_dicom_dir, dicomFolder)
        system(cmd)
        '''
        cmd = 'gdcmconv %s %s -w' % (fullPath, fullPath)
        system(cmd)

        cmd = 'mv %s %s/%s' % (fullPath, input_dicom_dir, dicomFolder)
        system(cmd)

print "DONE"
