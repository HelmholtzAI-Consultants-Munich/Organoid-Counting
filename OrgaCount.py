import os
from aicsimageio import AICSImage
from skimage.measure import block_reduce
from scipy import ndimage as ndi
from skimage.feature import canny
from skimage.measure import regionprops,label
from skimage.morphology import opening,remove_small_objects,closing,dilation,erosion
import numpy as np
import math

def setup_bboxes(segmentation): 
    bboxes = []
    diameter1 = []
    diameter2 = []
    i=0
    for region in regionprops(segmentation):
        minr, minc, maxr, maxc = region.bbox
        bbox_rect = np.array([[minr, minc], [maxr, minc], [maxr, maxc], [minr, maxc]])
        bboxes.append(bbox_rect)
        diameter1.append(maxr-minr)
        diameter2.append(maxc-minc)
    bbox_properties = {'diameter1': diameter1, 'diameter2': diameter2}
    text_parameters = {
        'text': 'D1: {diameter1}\nD2: {diameter2}',
        'anchor': 'upper_left',
        'translation': [-5, 0],
        'size': 8,
        'color': 'green',
    }
    bboxes = np.array(bboxes)
    return bbox_properties, text_parameters, bboxes

def circle_area(r):
    return math.pi * r**2 

def apply_normalization(img):
    img_min = np.min(img) # 31.3125 png 0
    img_max = np.max(img) # 2899.25 png 178
    img_norm = (255 * (img - img_min) / (img_max - img_min)).astype(np.uint8)
    return img_norm

class OrgaCount():
    def __init__(self, root_path, img_path, downsampling_size=4, sigma=3, low_threshold=10, high_threshold=25):
        img_czi = AICSImage(os.path.join(root_path, img_path))
        self.img_resX_orig = img_czi.physical_pixel_sizes.X # in micrometers
        self.img_resY_orig = img_czi.physical_pixel_sizes.Y
        self.img_original = np.squeeze(img_czi.data)
        print('Opened image: ', img_path, 'with shape: ', self.img_original.shape)
        self.downsampling_size = downsampling_size
        self.sigma = sigma
        self.low_threshold = low_threshold
        self.high_threshold = high_threshold
        self.background_intensity = 40
        self.min_radius_um = 15 # min diameter defined by collaborators as d=30 micrometers. Min area A=pi*r^2
        self.img = block_reduce(self.img_original, block_size=(self.downsampling_size, self.downsampling_size), func=np.mean)
        self.update_resolutions()
        self.img = apply_normalization(self.img)

    def update_resolutions(self):
        self.img_resX = self.downsampling_size * self.img_resX_orig
        self.img_resY = self.downsampling_size * self.img_resY_orig
    
    def get_current_downsampling(self):
        return self.downsampling_size
        
    def update_donwnsampling(self, new_size):
        self.downsampling_size = new_size
        self.update_resolutions()

    def update_sigma(self, new_sigma):
        self.sigma = new_sigma

    def update_low_threshold(self, new_low):
        self.low_threshold = new_low

    def update_high_threshold(self, new_high):
        self.high_threshold = new_high

    def min_pixel_area(self):
        min_area = circle_area(self.min_radius_um)
        min_area_pix = min_area / (self.img_resX * self.img_resY)
        return round(min_area_pix)

    def apply_morphologies(self):
        # downsample 
        self.img = block_reduce(self.img_original, block_size=(self.downsampling_size, self.downsampling_size), func=np.mean)   
        print('Image resampled to size: ', self.img.shape)
        self.update_resolutions()
        # normalise
        self.img = apply_normalization(self.img)
        # get mask of well and background
        mask = np.where(self.img<self.background_intensity,False,True)
        # find edges in image
        edges = canny(
                    image=self.img,
                    sigma=self.sigma,
                    low_threshold=self.low_threshold,
                    high_threshold=self.high_threshold,
                    mask = mask)
        # dilate edges
        edges = ndi.binary_dilation(edges)
        # fill holes
        filled = ndi.binary_fill_holes(edges)
        filled = erosion(filled)
        filled = erosion(filled)
        labels = label(filled)
        region = regionprops(labels)
        # remove objects larger than 30% of the image
        for prop in region:
            if prop.area > 0.3*self.img.shape[0]*self.img.shape[1]:
                filled[prop.coords] = 0
        # get min organoid size in pixels
        min_size_pix = self.min_pixel_area()
        filled = remove_small_objects(filled, min_size_pix)
        segmentation = label(filled)
        return segmentation

    def find_median_cell_size(segmentation):
        sizes=[]
        for region in regionprops(segmentation):
            shapes_areas = region.area
            sizes.append(shapes_areas)
        if len(sizes)!=0: avg_size = sum(sizes)/len(sizes)
        else: avg_size = 0
        return avg_size


## confirmed with png image ##
'''         
img_jpg = Image.open('example_data/image001.png') #plt.imread('example_data/image001.png')
#img_jpg  = Image.fromarray(img_jpg)
img_jpg = img_jpg.convert('L')
imgx = np.array(img_jpg)
print('aaaa', img_jpg.size)
#r, g, b = img_jpg[:,:,0], img_jpg[:,:,1], img_jpg[:,:,2]
#img = img_jpg[:,:,3] #r*0.2126+g*0.7152+b*0.0722

#print('AAAAAAA',[layer.name for layer in viewer.layers]) # ['Image', 'Segmentation', 'bboxes',]

'''