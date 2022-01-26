# Organoid_Counting

## Full installation description for Windows

For windows users you will need to first install Python (simply go to the app store and install the latest version of Python). Next double click on the ```setup.bat``` file which will install all necessary packages for you to run the software. In order to run the software you have two options:
 
 * Simple annotation tool with no automation (see below)
 * Automatic Organoid Counter with option for correction (see Use for automatic organoid counting on Windows)

## Use for annotation tool with no automations on Windows
To annotate organoids on images from a Windows machine, place the images you wish to annotate in the folder named ```images``` within the current directory. Next double click on the ```OrganoidCounter.bat``` file which will open your visualisation and annotation tool. Add bounding boxes around the organoids with the rectangle button on the top left window ("layer controls"). Once you are completed with an image press the ```s``` key on the keyboard to save the result and open the next image. A .json file will be created for each image which holds x and y coordinates and is stored in the annotations folder.

## Use for automatic organoid counting on Windows
To use the automatic organoid counter option double click on the ```AutoOrganoidCounter.bat``` file. This will open the napari tool which shows the original image and the bounding boxed of the already detected organoids. Wrongly detected objects can be removed by first selecting them (arrow button) and then clicking the backspace key on your keyboard, new bounding boxes can be added on organoids that were missed by selecting the rectanlge button, and existing boxes can be corrected by clicking on them and resizing them from the corners.

### Available parameters
On the top right window the user has the option to adapt several of the parameters that are used for the automatic organoid detection. 

* **sigma:** default=3
* **downsample:** default=4
* **low_threshold:** default=10
* **high_threshold:** default=25

## Installation through command line

This software has been tested with Python 3.9. Simple run ```pip install -r requirements.txt``` in your environment to install the necessary packages.

## Usage from command line:

**Required argument**:

* -image: The path of the input image.

To run this software, open a terminal and type:
```
python viewer.py --image example_data/well00.jpg
```
This will launch napari where you can view and edit the segmentation and original image. In the segmentation layer, if you want to add, edit or remove an organoid, you can use the layer controls window. See above for more details. The following arguments are availabel to the user:

* ```--auto_counter --> default=False```: whether to apply the automatic detection algorithm(True) or run the simple annotation tool(False)
* ```--save-screenshot```: Add this parameter when you wnat to save a screenshot of the napari window result
* ```--output --> default='annotations'```: the directory in which to store the .json annotation files. If nothing is specified a folder named annotations will be created within the working directory and the .json files will have the same names as the input images
* ```--downsample --> default=4```: see above
* ```--sigma --> default=3```: see above
* ```--low-threshold --> default=10```: see above
* ```--high-threshold --> default=25```: see above
