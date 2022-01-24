import os
import napari
import argparse
import numpy as np
#import pandas as pd
import matplotlib.pyplot as plt
from scipy import ndimage as ndi
from skimage.feature import canny
from skimage.filters import gaussian
from skimage.measure import regionprops,label
from skimage.morphology import opening,remove_small_objects,closing,dilation,erosion
from skimage.transform import resize
import json
import warnings
warnings.filterwarnings("ignore")
from magicgui import magicgui
from aicsimageio import AICSImage
from skimage.measure import block_reduce
from PIL import Image
import math
from typing import List


def get_args():
    parser = argparse.ArgumentParser(description='Organoid counter')
    parser.add_argument('--image', default=False)
    parser.add_argument('--auto-count', default=True)
    parser.add_argument('--output', default='annotations')
    return parser.parse_args()

def find_median_cell_size(segmentation):
    sizes=[]
    for region in regionprops(segmentation):
        shapes_areas = region.area
        sizes.append(shapes_areas)
    if len(sizes)!=0: avg_size = sum(sizes)/len(sizes)
    else: avg_size = 0
    return avg_size

def setup_bboxes(res): #, median_cell_size):
    bboxes = []
    diameter1 = []
    diameter2 = []
    i=0
    for region in regionprops(res):
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

def apply_morphologies(img, x_res, y_res, downsampling_size=1, sigma=3, low_threshold=10, high_threshold=25):
    
    img_min = np.min(img) # 31.3125 png 0
    img_max = np.max(img) # 2899.25 png 178
    img = (255 * (img - img_min) / (img_max - img_min)).astype(np.uint8)
    x_res = x_res * downsampling_size
    y_res = y_res * downsampling_size
    min_size = math.pi * 15**2 # min diameter defined by collaborators as d=30 micrometers. Min area A=pi*r^2
    min_size_pix = min_size / (x_res * y_res)

    mask = np.where(img<40,False,True)
    edges = canny(
                image=img,
                sigma=sigma,
                low_threshold=low_threshold,
                high_threshold=high_threshold,
                mask = mask)
    edges = ndi.binary_dilation(edges)
    filled = ndi.binary_fill_holes(edges)
    filled = erosion(filled)
    filled = erosion(filled)
    
    region = regionprops(label(filled))
    for prop in region:
        if prop.area > 5000:
            filled[prop.coords] = 0
    
    filled = remove_small_objects(filled, min_size_pix)
    segmentation = label(filled)
    return segmentation

if __name__ == '__main__':
    args = get_args()
    downsampling_size = 4
    if os.path.isdir(args.image):
        input_dir = args.image
        file_list = os.listdir(args.image)
        file_list = [file for file in file_list if file.endswith('.czi')]
    else:
        input_dir = './'
        file_list = [args.image]
    
    @magicgui(
            auto_call=True,         
            sigma={"widget_type": "Slider", "max": 10},
            low_threshold={"widget_type": "Slider", "max": 255},
            high_threshold={"widget_type": "Slider", "max": 255})
    def update_seg_res(sigma: int=3, low_threshold: int=10, high_threshold: int=25) -> List[napari.types.LayerDataTuple]:
        segmentation = apply_morphologies(img, img_resX, img_resY, downsampling_size, sigma=sigma, low_threshold=low_threshold, high_threshold=high_threshold)
        bbox_properties, text_parameters, bboxes = setup_bboxes(segmentation)
        print('Number of organoids detected with automatic method: ', len(bboxes))
        print('Sigma: ', sigma, ', Low threshold: ', low_threshold, ', High threshold: ', high_threshold)
        if len(bboxes) > 0:
            bbox_tuple = (bboxes, {'name': 'Organoids', 
                                    'face_color': 'transparent',
                                    'edge_color': 'magenta',
                                    'properties': bbox_properties,
                                    'text': text_parameters,
                                    'shape_type': 'rectangle',
                                    'edge_width': 3}, 'shapes')
        else:
            bbox_tuple = [([],{'name': 'Organoids', 'face_color': 'transparent', 'edge_color': 'magenta', 'edge_width': 3}, 'shapes')]
        return [bbox_tuple]

    output_dir = '/Users/christina.bukas/Documents/AI_projects/datasets/organoid_counting/2022-01-17_HFibs_Organoids_EF_all_wells_trainingdata/results/CValgoRuolin'
    if not os.path.isdir(args.output):
        os.makedirs(args.output)

    for image_file in file_list:
        img_czi = AICSImage(os.path.join(input_dir, image_file))
        img_resX = img_czi.physical_pixel_sizes.X # in micrometers
        img_resY = img_czi.physical_pixel_sizes.Y
        img = np.squeeze(img_czi.data)
        print('Opened image: ', image_file, 'with shape: ', img.shape)
        img = block_reduce(img, block_size=(downsampling_size, downsampling_size), func=np.mean) # downsample       

        raw_filename = image_file.split('.')[0]
        output_path = os.path.join(args.output, raw_filename+'.json')

        viewer = napari.Viewer()
        img_layer = viewer.add_image(img, name='Image', colormap='gray')
        if args.auto_count==True: 
            segmentation = apply_morphologies(img, img_resX, img_resY, downsampling_size)
            bbox_properties, text_parameters, bboxes = setup_bboxes(segmentation)#, median_cell_size)
            print('Number of organoids detected with automatic method: ', len(bboxes))
            #seg_layer = viewer.add_labels(segmentation, name='Segmentation')
            shapes_layer = viewer.add_shapes(bboxes, 
                                            name='Organoids',
                                            face_color='transparent',  
                                            edge_color='magenta',
                                            properties=bbox_properties,
                                            text=text_parameters,
                                            shape_type='rectangle',
                                            edge_width=3) #30
            screenshot=viewer.screenshot()
            screenshot = Image.fromarray(screenshot)
            screenshot.save(os.path.join(output_dir, raw_filename+'_screenshot.png'))
        else:
            shapes_layer = viewer.add_shapes(name='Organoids', face_color='transparent', edge_color='magenta', edge_width=3)
            data = {}
        viewer.window.add_dock_widget(update_seg_res)
        # update the layer dropdown menu when the layer list changes
        viewer.layers.events.changed.connect(update_seg_res.reset_choices)
        napari.run()

        @viewer.bind_key('s')
        def store_centroids(viewer): 
            bboxes = viewer.layers['Organoids'].data # returns numpy array
            for i, bbox in enumerate(bboxes):
                data.update({str(i): [list(bboxit) for bboxit in bbox]})
            #write to json
            with open(output_path, 'w') as outfile:
                json.dump(data, outfile)        
            viewer.close()
    



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