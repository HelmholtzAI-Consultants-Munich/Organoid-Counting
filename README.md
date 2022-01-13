# Organoid_Counting

## Installation through command line

This software has been tested with Python 3.9. Simple run ```pip install -r requirements.txt``` in your environment to install the necessary packages.

## Usage from command line:

**Required argument**:

* -image: The path of the input image.

To run this software, open a terminal and type:
```
python viewer.py --image example_data/well00.jpg
```
This will launch napari where you can view and edit the segmentation and original image. In the segmentation layer, if you want to add an organoid, you could choose paint mode and press 'M' to set the label as a new value and begin drawing.