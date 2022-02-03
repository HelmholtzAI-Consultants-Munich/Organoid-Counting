# Organoid_Counting

## Full installation description for Windows

For windows users you will need to first install Python (simply go to the Microsoft Store and install Python 3.9). Next navigate to the directory named ```Windows``` and double click on the ```setupWindows.bat``` file which will install all necessary packages for you to run the software. In order to run the software you have two options:
 
 * Simple annotation tool with no automation (see below)
 * Automatic Organoid Counter with option for correction (see Use for automatic organoid counting on Windows)

## Use for annotation tool with no automations on Windows
To annotate organoids on images from a Windows machine, place the images you wish to annotate in the folder named ```images``` within the ```Organoid_Counting``` directory. Next double click on the ```OrganoidCounter.bat``` file which will open your visualisation and annotation tool. Add bounding boxes around the organoids with the rectangle button on the top left window ("layer controls"). Once you are completed with an image press the ```s``` key on the keyboard to save the result and open the next image. A JSON file will be created for each image which holds x and y coordinates and is stored in the annotations folder and a CSV file which stores d1 (diameter 1), d2 (diameter 2) and area of ellipse of the organoid within the bounding box.

## Use for automatic organoid counting on Windows
Here too, in order to use the tool on organoid images from a Windows machine, place the images you wish to annotate in the folder named ```images``` within the current directory. To use the automatic organoid counter option double click on the ```AutoOrganoidCounter.bat``` file. This will open the napari tool which shows the original image and the bounding boxed of the already detected organoids. Wrongly detected objects can be removed by first selecting them (arrow button) and then clicking the backspace key on your keyboard, new bounding boxes can be added on organoids that were missed by selecting the rectanlge button, and existing boxes can be corrected by clicking on them and resizing them from the corners. Here also, once you are done you can press the ```s``` key on the keyboard to save the result of the annotation as a JSON file and parameters in a CSV file (d1,d2 and area) and open the next image.

![image](https://github.com/HelmholtzAI-Consultants-Munich/Organoid_Counting/blob/dev/readme_imgs/example_gui.png)

### Available parameters
On the top right window the user has the option to adapt several of the parameters that are used for the automatic organoid detection. 

* **downsample:** default=4 -> The downsamplign applied to the original image - this affects the outcome of the method 
* **sigma:** default=3 -> The sigma, standard deviation used for the Gaussian filter of the Canny edge detection algorithm. See [here](https://scikit-image.org/docs/dev/auto_examples/edges/plot_canny.html) for more details.
* **low_threshold:** default=10 -> The lower bound for hysteresis thresholding of the Canny edge detection algorithm. See [here](https://scikit-image.org/docs/dev/auto_examples/edges/plot_canny.html) for more details.
* **high_threshold:** default=25 -> The upper bound for hysteresis thresholding of the Canny edge detection algorithm. See [here](https://scikit-image.org/docs/dev/auto_examples/edges/plot_canny.html) for more details.

## Installation on MacOS or Linux systems

This software has been tested with Python 3.9. To setup the environment needed navigate to the directory ```LinuxMacOS``` and open a terminal. From there execute the file ```setupLinuxMacOS.sh```, i.e. ```bash setupLinuxMacOS.sh``` to create a virtual environment and install the necessary packages.

Similarly as with the Windows setup to use the annotation tool with no automations execute the file ```OrganoidAnnotator.sh```, i.e. ```bash OrganoidAnnotator.sh```. To run the software with automatic organoid counting execute the file ```AutoOrganoidCounter.sh```, i.e. ```bash AutoOrganoidCounter.sh```. In both cases your images should be first placed in a folder named ```images``` within the ```Organoid_Counting``` directory.


## Usage from command line:

**Required argument**:

* -image: The path of the input image.

To run this software, open a terminal and type:
```
python viewer.py --image example_data/
```
This will launch napari where you can view and edit the segmentation and original images in the folder example_data sequentially. In the segmentation layer, if you want to add, edit or remove an organoid, you can use the layer controls window. See [above](## Use for automatic organoid counting on Windows) for more details. 

**Optional arguments**

* ```--auto_counter --> default=False```: whether to apply the automatic detection algorithm(True) or run the simple annotation tool(False)
* ```--save-screenshot```: Add this parameter when you wnat to save a screenshot of the napari window result
* ```--output --> default='annotations'```: the directory in which to store the JSON annotation file, CSV files with parameters and screenshots (if specified). If nothing is specified a folder named annotations will be created within the working directory and the JSON and CSV files will have the same names as the input images
* ```--downsample --> default=4```: see above
* ```--sigma --> default=3```: see above
* ```--low-threshold --> default=10```: see above
* ```--high-threshold --> default=25```: see above
