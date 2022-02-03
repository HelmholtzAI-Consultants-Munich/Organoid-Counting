import os
import argparse
import warnings
warnings.filterwarnings("ignore")
import json
from skimage.io import imsave
import napari
from magicgui import magicgui
from typing import List
import numpy as np
import pandas as pd
from OrgaCount import *

def get_args():
    parser = argparse.ArgumentParser(description='Organoid counter')
    parser.add_argument('--image', default=False)
    parser.add_argument('--auto-count', default=True)
    parser.add_argument('--save-screenshot', action='store_true')
    parser.add_argument('--output', default='annotations')
    parser.add_argument('--downsample', default=4, type=int)
    parser.add_argument('--sigma', default=3, type=int)
    parser.add_argument('--low-threshold', default=10, type=int)
    parser.add_argument('--high-threshold', default=25, type=int)
    return parser.parse_args()

if __name__ == '__main__':
    args = get_args()
    if os.path.isdir(args.image):
        input_dir = args.image
        file_list = os.listdir(args.image)
        file_list = [file for file in file_list if file.endswith('.czi')]
    else:
        input_dir = './'
        file_list = [args.image]

    if not os.path.isdir(args.output):
        os.makedirs(args.output)

    for image_file in file_list:

        @magicgui(
        auto_call=True,         
        downsampling={"widget_type": "Slider", "min": 1, "max": 10},
        sigma={"widget_type": "Slider", "min": 1, "max": 10},
        low_threshold={"widget_type": "Slider", "max": 100},
        high_threshold={"widget_type": "Slider", "max": 100})
    
        def update_seg_res(downsampling: int=4, sigma: int=3, low_threshold: int=10, high_threshold: int=25) -> List[napari.types.LayerDataTuple]:
            orga_count.update_donwnsampling(downsampling)
            orga_count.update_sigma(sigma)
            orga_count.update_low_threshold(low_threshold)
            orga_count.update_high_threshold(high_threshold)
            segmentation = orga_count.apply_morphologies()
            _, _, bboxes = setup_bboxes(segmentation)
            print('Number of organoids detected with automatic method: ', len(bboxes))
            print('Sigma: ', sigma, ', Low threshold: ', low_threshold, ', High threshold: ', high_threshold, 'Downsampling: ', downsampling)
            img = add_text_to_img(orga_count.img, len(bboxes), downsampling)
            img_tuple = (img, {'name': 'Image'}, 'image')
            if len(bboxes) > 0:
                if downsampling<3: edge_width=5
                else: edge_width=3
                bbox_tuple = (bboxes, {'name': 'Organoids', 
                                        'face_color': 'transparent',
                                        'edge_color': 'magenta',
                                        'shape_type': 'rectangle',
                                        'edge_width': edge_width}, 'shapes')
            else:
                bbox_tuple = ([],{'name': 'Organoids', 'face_color': 'transparent', 'edge_color': 'magenta', 'edge_width': 3}, 'shapes')
            return [img_tuple, bbox_tuple]
 
        raw_filename = os.path.split(image_file)[-1]
        raw_filename = raw_filename.split('.')[0]
        output_path_json = os.path.join(args.output, raw_filename+'.json')
        output_path_csv = os.path.join(args.output, raw_filename+'.csv')
        orga_count = OrgaCount(input_dir, image_file, args.downsample, args.sigma, args.low_threshold, args.high_threshold)
        
        viewer = napari.Viewer()
        img = orga_count.img
        if args.auto_count==True: 
            segmentation = orga_count.apply_morphologies()
            bbox_properties, text_parameters, bboxes = setup_bboxes(segmentation)#, median_cell_size)
            print('Number of organoids detected with automatic method: ', len(bboxes))
            img = add_text_to_img(img, len(bboxes), orga_count.downsampling_size)
            img_layer = viewer.add_image(img, name='Image', colormap='gray')
            shapes_layer = viewer.add_shapes(bboxes, 
                                            name='Organoids',
                                            face_color='transparent',  
                                            edge_color='magenta',
                                            shape_type='rectangle',
                                            edge_width=3)
        else:
            img_layer = viewer.add_image(img, name='Image', colormap='gray')    
            shapes_layer = viewer.add_shapes(name='Organoids', face_color='transparent', edge_color='magenta', edge_width=3)
        viewer.window.add_dock_widget(update_seg_res)
        # update the layer dropdown menu when the layer list changes
        viewer.layers.events.changed.connect(update_seg_res.reset_choices)

        @viewer.bind_key('s')
        def store_centroids(viewer):
            if args.save_screenshot:
                screenshot=viewer.screenshot()
                imsave(os.path.join(args.output, raw_filename+'_screenshot.png'), screenshot)
            data_json = {} 
            data_csv = []
            bboxes = viewer.layers['Organoids'].data # returns numpy array
            for i, bbox in enumerate(bboxes):
                bbox *= orga_count.get_current_downsampling()
                d1 = abs(bbox[0][0] - bbox[1][0])
                d2 = abs(bbox[0][1] - bbox[2][1])
                d1, d2, area = orga_count.compute_real_values(d1,d2)
                data_csv.append([i, round(d1,3), round(d2,3), round(area,3)])
                data_json.update({str(i): [list(bboxit) for bboxit in bbox]})
            #write to csv
            df = pd.DataFrame(data_csv, columns =['OrganoidID', 'D1[mm]','D2[mm]', 'Area [mm^2]']) 
            df.to_csv(output_path_csv, index=False)
            #write to json
            with open(output_path_json, 'w') as outfile:
                json.dump(data_json, outfile)        
            viewer.close()
        
        napari.run()
    