import os
import argparse
import warnings
warnings.filterwarnings("ignore")
import json
from skimage.io import imsave
import napari
from magicgui import magicgui
from napari.types import ShapesData, ImageData
from typing import List
import numpy as np
import csv
from OrgaCount import *

def get_args():
    parser = argparse.ArgumentParser(description='Organoid counter')
    parser.add_argument('--image', default=False)
    parser.add_argument('--auto-count', default=True)
    parser.add_argument('--save-screenshot', action='store_true')
    parser.add_argument('--output', default='annotations')
    parser.add_argument('--downsample', default=4, type=int)
    parser.add_argument('--min-diameter', default=30)
    parser.add_argument('--sigma', default=3, type=int)
    parser.add_argument('--low-threshold', default=10, type=int)
    parser.add_argument('--high-threshold', default=25, type=int)
    parser.add_argument('--background-intensity', default=40, type=int)
    return parser.parse_args()

if __name__ == '__main__':
    args = get_args()
    # check if a single image or a directory of images has been given
    if os.path.isdir(args.image):
        input_dir = args.image
        file_list = os.listdir(args.image)
        file_list = [file for file in file_list if file.endswith('.czi')]
    else:
        input_dir = './'
        file_list = [args.image]
    # create output directory if not existing
    if not os.path.isdir(args.output):
        os.makedirs(args.output)
    
    # for image provided
    for image_file in file_list:
        # set up execute button in napari viewer, which when clicked will update the number of organoids displayed in text
        @magicgui(call_button="execute")
        def update_display_text(bboxes: ShapesData) -> List[napari.types.LayerDataTuple]:
            img = orga_count.img_orig_norm.copy()
            img = add_text_to_img(img, len(bboxes)) #, downsampling)
            img_tuple = (img, {'name': 'Image'}, 'image')
            bbox_tuple = (bboxes, {'name': 'Organoids', 
                        'face_color': 'transparent',
                        'edge_color': 'magenta',
                        'shape_type': 'rectangle',
                        'edge_width': 12}, 'shapes')      
            return [img_tuple, bbox_tuple]
        # set up parameter sliders in napari viewer, so user can change algorithm parameters and choose best results
        @magicgui(
        auto_call=True,         
        downsampling={"widget_type": "Slider", "min": 1, "max": 10},
        min_diameter={"widget_type": "Slider", "min": 10, "max": 100},
        sigma={"widget_type": "Slider", "min": 1, "max": 10})
        # low and high threshold removed for now as not helpful for user
        #low_threshold={"widget_type": "Slider", "max": 100},
        #high_threshold={"widget_type": "Slider", "max": 100})
        def update_seg_res(downsampling: int=args.downsample, min_diameter: int=args.min_diameter, sigma: int=args.sigma) -> List[napari.types.LayerDataTuple]: #, low_threshold: int=args.low_threshold, high_threshold: int=args.high_threshold
            # update all parameters in OrgaCount instance
            orga_count.update_donwnsampling(downsampling)
            orga_count.update_min_organoid_size(min_diameter)
            orga_count.update_sigma(sigma)
            #orga_count.update_low_threshold(low_threshold)
            #orga_count.update_high_threshold(high_threshold)
            
            # get segmentation
            segmentation = orga_count.apply_morphologies()
            _, _, bboxes = setup_bboxes(segmentation)
            # reset box coordinates to original resolution
            bboxes *= orga_count.get_current_downsampling() 
            print('Number of organoids detected with automatic method: ', len(bboxes))
            print('Downsampling: ', downsampling, 'Minimum organoid diameter: ', min_diameter, ', Sigma: ', sigma) #', Low threshold: ', low_threshold, ', High threshold: ', high_threshold,
            # display image and bounding boxes in naapri viewer
            img = orga_count.img_orig_norm.copy()
            img = add_text_to_img(img, len(bboxes)) #, downsampling)
            img_tuple = (img, {'name': 'Image'}, 'image')
            if len(bboxes) > 0:
                bbox_tuple = (bboxes, {'name': 'Organoids', 
                                        'face_color': 'transparent',
                                        'edge_color': 'magenta',
                                        'shape_type': 'rectangle',
                                        'edge_width': 12}, 'shapes')
            else:
                bbox_tuple = ([],{'name': 'Organoids', 'face_color': 'transparent', 'edge_color': 'magenta', 'edge_width': 12}, 'shapes')
            return [img_tuple, bbox_tuple]
        
        # create filenames for two output files
        raw_filename = os.path.split(image_file)[-1]
        raw_filename = raw_filename.split('.')[0]
        output_path_json = os.path.join(args.output, raw_filename+'.json')
        output_path_csv = os.path.join(args.output, raw_filename+'.csv')

        # initialise OrgaCount instance with current image
        orga_count = OrgaCount(input_dir, image_file, args.downsample, args.min_diameter, args.sigma, args.low_threshold, args.high_threshold, args.background_intensity)
        
        # initialise napari viewer
        viewer = napari.Viewer()
        img = orga_count.img_orig_norm.copy()
        # if auto_count is true get image segmentation, else open napari viewer so user can annotate
        if args.auto_count==True: 
            # get image segmentation and get bounding boxes
            segmentation = orga_count.apply_morphologies()
            _, _, bboxes = setup_bboxes(segmentation)
            bboxes *= orga_count.get_current_downsampling()
            print('Number of organoids detected with automatic method: ', len(bboxes))
            img = add_text_to_img(img, len(bboxes))
            # add image and bounding boxes layer to napari viewer
            img_layer = viewer.add_image(img, name='Image', colormap='gray')
            shapes_layer = viewer.add_shapes(bboxes, 
                                            name='Organoids',
                                            face_color='transparent',  
                                            edge_color='magenta',
                                            shape_type='rectangle',
                                            edge_width=12)
            # add parameters window to napari viewer
            viewer.window.add_dock_widget(update_seg_res)
            # update the layer dropdown menu when the layer list changes
            viewer.layers.events.changed.connect(update_seg_res.reset_choices)
        else:
            img_layer = viewer.add_image(img, name='Image', colormap='gray')    
            shapes_layer = viewer.add_shapes(name='Organoids', face_color='transparent', edge_color='magenta', edge_width=12)
        # update the text displaying the number of organoids
        viewer.window.add_dock_widget(update_display_text)
        viewer.layers.events.changed.connect(update_display_text.reset_choices)
        
        # once user hit the 's' key on the keyboard save results and close viewer
        @viewer.bind_key('s')
        def store_centroids(viewer):
            # take a screenshot of current visualisation - overlay image and bounding boxes
            if args.save_screenshot:
                screenshot=viewer.screenshot()
                imsave(os.path.join(args.output, raw_filename+'_screenshot.png'), screenshot)
            data_json = {} 
            data_csv = []
            bboxes = viewer.layers['Organoids'].data # returns numpy array
            # save diameters and area of organoids (approximated as ellipses)
            for i, bbox in enumerate(bboxes):
                d1 = abs(bbox[0][0] - bbox[2][0])
                d2 = abs(bbox[0][1] - bbox[2][1])
                d1, d2, area = orga_count.compute_real_values(d1,d2)
                data_csv.append([i, round(d1,3), round(d2,3), round(area,3)])
                data_json.update({str(i): [list(bboxit) for bboxit in bbox]})
            #write diameters and area to csv
            with open(output_path_csv, 'w') as f:
                write = csv.writer(f, delimiter=';')
                write.writerow(['OrganoidID', 'D1[um]','D2[um]', 'Area [um^2]'])
                write.writerows(data_csv)
                viewer.close()
            #write bbox coordinates to json
            with open(output_path_json, 'w') as outfile:
                json.dump(data_json, outfile)   
        
        napari.run()
    