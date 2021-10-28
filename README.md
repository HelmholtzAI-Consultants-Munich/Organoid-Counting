# Organoid_Counting

## Usage:
In Final segmentation layer, if you want to add an organoid, you could choose paint mode and press 'M' to set the label as a new value and begin drawing.

**Require arguments**:

* -image: The path of the input image.

```
python viewer.py --image example_data/well00.jpg
```

## Use for manual annotations
To annotate organoids on images from a Windows machine place the images you wish to annotate in the a folder names images/ in the current directory. Next double click on the ```OrganoidCounter.bat``` file which will open your visualisation and annotation tool. Add organoid centroid with the + option and once you are completed with an image press the ```s``` key on the keyboard to save the result and open the next image

## Installation

This software has been tested with Python 3.9. Simple run ```pip install -r requirements.txt``` in your environment to install the necessary packages.
