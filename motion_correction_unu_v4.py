#!/usr/bin/python

#Pipeline for Preprocessing: motion correction
# Author: Powell Chu
# Hodaie's Lab (2018)

'''


Softwares that need to be installed:
1. Python 2.7
2. dcm2nii (NITRC)
3. FSL 5.0
4. Slicer 4.3.1




Usage: 

python [/PATH/to/]motion_correction_unu_v2.py [OPTION] [input_DTI_directory]

where OPTION is as follows:

-f, --all : runs FSL motion correction
-a, --flipaxis : axis to invert. Comma-separated.
    0: X-axis
    1: Y-axis
    2: Z-axis

    for example, if you want to flip all axes, type "-a 0,1,2". If you want to flip X and Z axes, type "-a 0,2"
-n, --dry-run : dry run the code without executing files to make sure the code works properly


EXAMPLE:
1) python [/PATH/to/]motion_correction_unu_v4.py -f -a 1 .
- run FSL motion correction and flip axis on Y-axis on the current DTI folder

2) python [/PATH/to/]motion_correction_unu_v4.py -a 0,2 .
- flip axes ONLY on X-axis and Z-axis on the current DTI folder

'''

#from os import system, listdir, path
from optparse import OptionParser
import os,sys
from glob import glob
import numpy as np


#dryrun = False       #no FSL correction and no flipping bvec


def execute(cmd,dryrun=False):
    print("->"+cmd+"\n")
    if not dryrun:
        os.system(cmd)


def transpose(filename):
    """
    content = []
    f = open(filename, 'r')
    nmax = 0
    for line in f:
        text = line.strip()
        tokens = text.split()
        tlen = len(tokens)
        if tlen > nmax:
            nmax = tlen
        content.append(tokens)

    f.close()

    transposed = open('dirs_62.dat','w')
    for item in content:
        print>>transposed, item
    transposed.close()
    """
    data = np.loadtxt(filename)
    data_T = data.transpose()
    return data_T

def winvhalf(X):
    """
    equivalent to matlab code M^-0.5
    """
    e, V = np.linalg.eigh(X)
    return np.dot(V, np.dot(np.linalg.inv(np.diag(e+0j)**0.5),V.T))

def correct_bvecs(bvecs, data):
    """
    Perform finite strain correction for bvecs
    """

#20180508: added condition to check bvecs size
    if (bvecs.shape[1] > bvecs.shape[0]) and (bvecs.shape[0] == 3):
        bvecs = bvecs.T

    #print '-- before --'
    #print bvecs

#    print bvecs.shape
#    print data.shape
#    raw_input("***pchu***")

    cor_bvecs = np.zeros(bvecs.shape)

    trans = np.split(data, bvecs.shape[0])
    for i, bvec in enumerate(bvecs):
        rt = np.matrix(trans[i][:3,:3], dtype=np.complex)
        R = np.real(winvhalf(rt*rt.T)*rt)
        cor_bvecs[i] = np.nan_to_num(bvec*R.T)
    return cor_bvecs

def dattonrrd(bvec):
    bvec_file = open(bvec,'r')
    new_bvec = []
    index = 0
    for line in bvec_file:
        newline = 'DWMRI_gradient_%04d:= %s' % (index,line)
        new_bvec.append(newline)
        index += 1
    return new_bvec



#2. FSL correction
#a) motion correction

def doFSLcorrection(subjname,base,newBvecFile,dryrun=False):

    ##split the 4D data into individual volume
    print('Splitting scans')
    cmd=('fslsplit %s.nii.gz' % subjname)
    execute(cmd,dryrun)

    #remove .xfm files
    cmd = 'rm *.xfm'
    execute(cmd,dryrun)   

    print('Register to baseline')
    ##apply transformation
    for vol in sorted(glob('vol*.nii.gz')):
        print ('Registering: %s' % vol)
        base = os.path.splitext(os.path.splitext(vol)[0])[0]
        cmd = 'flirt -in %s.nii.gz -ref vol0000.nii.gz -nosearch -noresampblur -omat %s_trans_nobet.xfm -interp spline -out %s_reg_nobet.nii.gz -paddingsize 1' % (base,base,base)
        execute(cmd,dryrun)

    ##merge the files together
    print ('fslmerge')
    cmd = 'fslmerge -t Motion_Corrected_DWI_nobet.nii.gz *reg_nobet.nii.gz'
    execute(cmd,dryrun)

    cmd = 'rm vol*nii*'
    execute(cmd,dryrun)


    ##Apply transform to .bvec file
    print ('Calculating transforms')

    if not dryrun:
        ##transpose .bvec
        bvec_transposed = transpose(subjname+'.bvec')
        np.savetxt('dirs_62.dat',bvec_transposed,fmt='%.3f')

    ##getting transform matrices from each volume and concatenate them
    cmd = ('cat *trans*.xfm > Transforms.txt')
    execute(cmd,dryrun)

    if not dryrun:
        ##finitestrain.py
        transform_mrtix = np.loadtxt('Transforms.txt')
        bvecs = bvec_transposed

        cor_bvecs = correct_bvecs(bvecs, transform_mrtix)

        #print '-- after --'
        #print cor_bvecs
        np.savetxt(newBvecFile, cor_bvecs, fmt='%.10f')


def flip_gradient(newBvecFile, flip):
    bvec = np.loadtxt(newBvecFile)

    if bvec.shape[0] < bvec.shape[1]:
        bvec = bvec.transpose()

#pchu:commented bval input
#    grad = np.column_stack((bvec, bval))
    grad = bvec

    print "**************original**************"
    print grad
    # invert GE grad axis for mrtrix

    grad[:,flip] *= -1

    print "corrected"
    print "------------------------------"
    print grad

    np.savetxt(newBvecFile, grad, fmt="%10.6f")


#get script path
def get_script_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))




##################
#Main Run function
##################

def run(options,args):
    input_dir = os.path.join(os.getcwd(),args[0])

#    raw_input(input_dir)

    if not (os.path.isdir(input_dir)):
        print ("Invalid DTI directory. Please verify.")
        os.sys.exit()

    dryrun=options.dryrun
    runFSL=options.fsl
    ax = [ int(i) for i in options.axis.split(',') ]
    
    #remove old nifti directory
    #cmd = 'rm -rf %s/nifti' % input_dir
    #execute(cmd,dryrun)

    subjname = "0"
    bval_file = glob(input_dir+"/*.bval")
    if bval_file:
        bval_file = bval_file[0]
        base = os.path.splitext(os.path.splitext(bval_file)[0])[0]
        subjname = base

    print ("subjname: "+subjname)

    if not ( (os.path.isfile(subjname+".nii") or os.path.isfile(subjname+".nii.gz")) and os.path.isfile(subjname+".bvec") ):

         #1. Convert DICOM to Nifti
        if not os.path.isdir(input_dir+"/dicom"):
            for fn in sorted(os.listdir(input_dir)):

                if fn.endswith(".dcm"):

                    #move all dicom files into a dicom folder
                    cmd = 'mkdir -p %s/dicom' % input_dir
                    execute(cmd,False)
                    cmd = 'mv %s/*.dcm %s/dicom/.' % (input_dir,input_dir)
                    execute(cmd,dryrun)

                    cmd = 'mkdir -p %s/nifti' % input_dir
                    execute(cmd,False)

                    print 'Converting DICOM to Nifti...'
                    cmd = 'dcm2nii -d N -e N -f Y -i N -p N -o %s/nifti %s/dicom/*' % (input_dir,input_dir)
                    execute(cmd,dryrun)
                    break
        else:
            cmd = 'mkdir -p %s/nifti' % input_dir
            execute(cmd,False)
            for fn in sorted(os.listdir(input_dir+"/dicom")):
                print 'Converting DICOM to Nifti...'
                cmd = 'dcm2nii -d N -e N -f Y -i N -p N -o %s/nifti %s/dicom/*' % (input_dir,input_dir)
                execute(cmd,dryrun)
                break
    else:

        cmd = 'mkdir -p %s/nifti' % input_dir
        execute(cmd,False)

        cmd = 'ln -s %s* %s/nifti/.' % (subjname,input_dir)
        execute(cmd,dryrun)
    
    os.chdir(input_dir + "/nifti")
    if not dryrun:

        if os.path.isfile("DWI_CORRECTED.nii.gz"):
            cmd = 'rm DWI_CORRECTED.nii.gz'
            execute(cmd,dryrun)
        if os.path.isfile("DWI_CORRECTED.bvec"):
            cmd = 'rm DWI_CORRECTED.bvec'
            execute(cmd,dryrun)
        if os.path.isfile("DWI_CORRECTED.bval"):
            cmd = 'rm DWI_CORRECTED.bval'
            execute(cmd,dryrun)
        if os.path.isfile("DWI.bval"):
            cmd = 'rm DWI.bval'
            execute(cmd,dryrun)


        nii_file = glob("*.nii*")[0]
        #print(nii_file)
        base = os.path.splitext(os.path.splitext(nii_file)[0])[0]
        subjname = base
    else:
        subjname = "DRYRUN"

    '''
    subjname = input_dir
    #print(subjname)

    os.rename(base+".nii.gz", subjname+".nii.gz")
    os.rename(base+".bvec", subjname+".bvec")
    os.rename(base+".bval", subjname+".bval")
    '''

    #2 do FSL motion correction, on both images and bvec

    newBvecFile = 'newdirs.dat'

    if (runFSL):
        doFSLcorrection(subjname,base,newBvecFile,dryrun)

    #2b: flip direction if necessary
    # -1: flip NO AXES
    # flip x: 0
    # flip y: 1
    # flip z: 2

    if (ax[0]) > -1:
        print ("Flipping axes:")
        for flip in ax:
            flip_axis = {
                0: "X-axis",
                1: "Y-axis",
                2: "Z-axis"
            }
            print (str(flip_axis.get(flip,"invalid argument")))
            flip_gradient(newBvecFile,flip)

    if (os.path.isfile(newBvecFile)):
        #3 To generate newdirs.nhdr from newdirs.dat
        newBvec_nhdr = dattonrrd(newBvecFile)

        f = open('newdirs.nhdr', 'w')
        for index in range(0,len(newBvec_nhdr)):
            f.write(newBvec_nhdr[index])
        f.close()

    #4. Conversion to NRRD
    print "Convert to nrrd"

    #print "Slicer --launch DWIConvert --inputBVectors subject.bvec --inputBValues subject.bval --inputVolume Motion_Corrected_DWI_nobet.nii.gz --outputVolume temp_dwi_old_bvec.nrrd --conversionMode FSLToNrrd"
    cmd = 'Slicer --launch DWIConvert --inputBVectors %s.bvec --inputBValues %s.bval --inputVolume Motion_Corrected_DWI_nobet.nii.gz --outputVolume temp_dwi_old_bvec.nrrd --conversionMode FSLToNrrd' % (subjname,subjname)
    execute(cmd,dryrun)


    #5. convert to nhdr + raw and append the new directions onto the header
    dwi_out="DWI_CORRECTED.nhdr"


    ##Without unu (teem) installation
    #added:20180209: call unu in script directory
    script_path = get_script_path()
    print script_path
    cmd = '%s/unu save -i temp_dwi_old_bvec.nrrd -o %s -f nrrd' % (script_path,dwi_out)
    execute(cmd,dryrun)
    #20180209: end

    '''
    ##With unu (teem) installation
    cmd = 'unu save -i temp_dwi_old_bvec.nrrd -o %s -f nrrd' % dwi_out
    execute(cmd,dryrun)
    '''

#20180328: comment out because this portion only works for slicer 4.3.1
    '''
    cmd = 'cat %s | head -22  > tmp.nhdr' % dwi_out
    execute(cmd,dryrun)
    cmd = 'cat newdirs.nhdr >> tmp.nhdr'
    execute(cmd,dryrun)
    cmd = 'mv tmp.nhdr %s' % dwi_out
    execute(cmd,dryrun)
    '''

#20180328: using this section of the code instead (from Peter) that works for Slicer 4.3.1 and newer
    cmd = 'cat %s | head -25  > tmp.nhdr' % dwi_out
    execute(cmd,dryrun)
    cmd = 'cat tmp.nhdr | egrep -v \'^*#\' > tmp2.nhdr'
    execute(cmd,dryrun)
    cmd = 'cat tmp2.nhdr | head -17  > tmp3.nhdr'
    execute(cmd,dryrun)

    cmd = 'cat newdirs.nhdr >> tmp3.nhdr'
    execute(cmd,dryrun)
    cmd = 'cat tmp3.nhdr  > %s' % dwi_out
    execute(cmd,dryrun)
    cmd = 'rm tmp*.nhdr'
    execute(cmd,dryrun)


    #6. set proper links before feeding into SAGIT
    print "setting links..."

    print "DWI_CORRECTED.nii.gz --> Motion_Corrected_DWI_nobet.nii.gz"

    if os.path.isfile("Motion_Corrected_DWI_nobet.nii.gz"):
        cmd = 'ln -s Motion_Corrected_DWI_nobet.nii.gz DWI_CORRECTED.nii.gz'
        execute(cmd,dryrun)

    print "DWI_CORRECTED.bvec --> newdirs.dat"
    if os.path.isfile("newdirs.dat"):
        cmd = 'ln -s newdirs.dat DWI_CORRECTED.bvec'
        execute(cmd,dryrun)

    print "DWI_CORRECTED.bval --> subject.bval"
    if os.path.isfile(subjname+".bval"):
        cmd = 'ln -s %s.bval DWI_CORRECTED.bval' % (subjname)
        execute(cmd,dryrun)

    print "DWI.bval --> subject.bval"
    if os.path.isfile(subjname+".bval"):
        cmd = 'ln -s %s.bval DWI.bval' % (subjname)
        execute(cmd,dryrun)


#################################
#Main
#################################


'''
try:
    input_dir = sys.argv[1]
except:
    print "\n\nUsage: python [/PATH/to/]motion_correction_unu.py [input_directory]"
    print "[input directory] is the DTI folder. Please verify.\n"
    exit()

'''

if __name__ == '__main__':
    parser = OptionParser(usage="Usage: %prog [options] <input DTI directory>")
    parser.add_option("-f", "--all", dest="fsl", action='store_true', default=False, help="Run (FSL) motion correction.")
    parser.add_option("-a", "--flipaxis", dest="axis", default='-1', help="Axis to invert. 0:X-axis; 1:Y-axis; 2:Z-axis. Comma-separated, default is None")
    parser.add_option("-n", "--dry-run", action='store_true',dest="dryrun", help="Dry run, don't save output",default=False)
    options, args =  parser.parse_args()

    if len(args) < 1:
        parser.print_help()
        sys.exit(2)

    else:
        run(options, args)
        
print "DONE"
