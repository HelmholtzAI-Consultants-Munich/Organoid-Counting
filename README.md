# Organoid_Counting

## Full installation description for Windows

For windows users you will need to first install Python (simply go to the app store and install the latest version of Python). Next double click on the ```setup.bat``` file which will install all necessary packages for you to run the software. In order to run the software you have two options:
 
 * Simple annotation tool (see Use for manual annotations below)
 * Automatic Organoid Counter with option for correction (see Use for automatic organoid counting on Windows below)

## Use for manual annotations on Windows
To annotate organoids on images from a Windows machine, place the images you wish to annotate in the folder named ```images``` in the current directory. Next double click on the ```OrganoidCounter.bat``` file which will open your visualisation and annotation tool. Add organoid centroids with the + option and once you are completed with an image press the ```s``` key on the keyboard to save the result and open the next image. A .json file will be created for each image which holds x and y coordinates and is stored in the annotations folder.

## Use for automatic organoid counting on Windows
To use the automatic organoid counter option double click on the ```AutoOrganoidCounter.bat``` file. This will open the napari tool which shows the original image and the segmentation created, as well as the centroid points of the each segmented object.


## Installation through command line

This software has been tested with Python 3.9. Simple run ```pip install -r requirements.txt``` in your environment to install the necessary packages.

## Usage from command line:

**Required argument**:

* -image: The path of the input image.

To run this software, open a terminal and type:
```
python viewer.py --image example_data/well00.jpg
```
This will launch napari where you can view and edit the segmentation and original image. In the segmentation layer, if you want to add an organoid, you could choose paint mode and press 'M' to set the label as a new value and begin drawing. To run the simple annotation tool set ```--auto_counter False```.
