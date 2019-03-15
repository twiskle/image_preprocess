#!/bin/bash
# Created by: Pchu (Nov 2017)

#this script is used to automate run the following:
#dicom_decompress_rename.py: calls dicom_decompress to decompress the dicom files, and calls dicom_folder_rename to rename the folder name to [subject]_[date]
#dicom_divide_batch.py: calls dicom_header_divider_3_link_dcm2nii.py to create symbolic links to the dicom folders and separate them into respective subfolders
#DTI_mc_batch.py: calls motion_correction.py to perform motion correction on DTI images of each subject


#arguments:
#1st: root folder's DIRECTORY that contains all subjects' dicom images
#2nd: 

if [ "$1" = "" ]; then
    echo "Empty Input. Please specify the DIRECTORY of the root folder that contains subjects' folder to be executed"
    echo "Root folder --> subject(s) folder --> dicom images"
    exit 1
elif [ ! -d "$1" ]; then
    echo "Invalid directory name"
    exit 1
fi

BASEDIR=$(dirname "$0")
echo "script directory: '$BASEDIR'"

echo "Root folder specified: '$1'"

ls -p "$1" | grep "/" > "$1"/listofsubjects.txt
python "$BASEDIR"/dicom_decompress_rename.py "$1"/listofsubjects.txt
ls -p "$1" | grep "/" > "$1"/listofsubjects_2.txt
python "$BASEDIR"/dicom_divide_batch.py "$1"/listofsubjects_2.txt
python "$BASEDIR"/DTI_mc_batch.py "$1"/listofsubjects_2.txt

echo "DONE batch run on preprocessing!!"

