# image_preprocess
# preprocessing script on MR images

This script (batch_run.sh) performs preprocessing steps on MR images, in the following steps:

1) Decompression on DICOM images
2) Sort through all DICOM images to create symbolic links and put them into separate folders based on their image sequence
3) Perform motion correction on the subsequent diffusion MR image
