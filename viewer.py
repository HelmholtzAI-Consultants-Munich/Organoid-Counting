import os
import napari
import argparse
import numpy as np
#import pandas as pd
import matplotlib.pyplot as plt
from scipy import ndimage as ndi
from skimage.feature import canny
from skimage.measure import regionprops,label
from skimage.morphology import opening,remove_small_objects,closing,dilation,erosion
from skimage.transform import resize
import czifile
import json
import warnings
warnings.filterwarnings("ignore")

def get_args():
    parser = argparse.ArgumentParser(description='Organoid counter')
    parser.add_argument('--image', default=False)
    parser.add_argument('--auto_count', default=True)
    parser.add_argument('--output', default='annotations')
    return parser.parse_args()

def compute_diameter(res):
    # viewer
    points = [] 
    colors = []
    bboxes = []
    diameter = []
    i=0
    for region in regionprops(res):
        y,x = region.centroid
#             if region.area >= 2*median_size:       
#                 #bound
        minr, minc, maxr, maxc = region.bbox
        diameter.append(np.around(0.5*(maxr+maxc-minc-minr),2))
#                 bbox_rect = np.array([[minr, minc], [maxr, minc], [maxr, maxc], [minr, maxc]])
#                 colors.append('green') #0.1)
#                 bboxes.append(bbox_rect)

#             elif region.area < median_size/2:
#                 colors.append('red')
#             else:
        colors.append('red')
        points.append([y,x])

#         points=np.array(points)
    point_properties={
        'point_colors': np.array(colors),
        'diameter': diameter
    }
    text_properties = {
        'text': '{diameter}',
        'anchor': 'upper_left',
        'translation': [-5, 0],
        'size': 8,
        'color': 'magenta',
    }
    bboxes = np.array(bboxes)
    return points, point_properties, text_properties, bboxes

def apply_morphologies(img):
    
    #img = ((image-image.min())/(image.max()-image.min())*255).astype(np.uint16)
    mask = np.where(img<20,False,True)
    edges = canny(
                    image=img,
                    sigma=3,
                    low_threshold=10,
                    high_threshold=25,
                    mask = mask
                )
    edges = ndi.binary_dilation(edges)
    # edges = closing(edges)

    filled = ndi.binary_fill_holes(edges)
    filled = erosion(filled)
    filled = erosion(filled)

    region = regionprops(label(filled))
    for prop in region:
        if prop.area > 5000:
            filled[prop.coords] = 0
    
    filled = remove_small_objects(filled,40)
    return filled


if __name__ == '__main__':
    args = get_args()
    
    if os.path.isdir(args.image):
        input_dir = args.image
        file_list = os.listdir(args.image)
        file_list = [file for file in file_list if file.endswith('.czi')]
    else:
        input_dir = './'
        file_list = [args.image]

    if args.auto_count==True: 
        result = []
        for image_file in file_list:
            img = czifile.imread(os.path.join(input_dir, image_file))
            img = img[::10,::10]
            filled = apply_morphologies(img)
            segmentation = label(filled)
            max_label = max(np.unique(segmentation))
            points, point_properties, text_properties, _ = compute_diameter(segmentation)
            print('Image name: ', image_file)
            print('Image size: ', img.shape)
            print('Number of organoids detected with automatic method: ', len(points))
            result.append([image_file,len(points)])

            def add_points(event):
                updated_seg = viewer.layers['Segmentation'].data
                new_points, new_properties, text_properties, _ = compute_diameter(updated_seg)
                viewer.layers.pop(2)
                points_layer = viewer.add_points(np.array(new_points),
                        text=text_properties,
                        properties=new_properties,
                        face_color='point_colors',
                        size=5,
                        name='points')

            viewer = napari.Viewer()
            img_layer = viewer.add_image(img, name='Image')
            seg_layer = viewer.add_image(segmentation, name='Segmentation',blending='additive',colormap='cyan')
            seg_layer.events.set_data.connect(add_points) 

            if len(points)>0:
                points_layer = viewer.add_points(np.array(points),
                                        text=text_properties,
                                        properties=point_properties,
                                        face_color='point_colors',
                                        size=5,
                                        name='points')
            napari.run()

            @viewer.bind_key('d') # denote done
            def update_cell_numbers(viewer):
                new_points = []
                new_diameter = []
                new_colors = []
                for region in regionprops(viewer.layers['Segmentation'].data):      
                    y,x = region.centroid
                    new_points.append([y,x])
                    minr, minc, maxr, maxc = region.bbox
                    new_diameter.append(np.around(0.5*(maxr+maxc-minc-minr),2))
                    new_colors.append('red')
                        
                new_properties={
                    'point_colors': np.array(new_colors),
                    'diameter': new_diameter
                }
                viewer.layers.pop(4)
                points_layer = viewer.add_points(np.array(new_points),
                        text=text_properties,
                        properties=new_properties,
                        face_color='point_colors',
                        size=5,
                        name='points')
            @viewer.bind_key('e')
            def close_viewer(): viewer.close()
        
    else:
        if not os.path.isdir(args.output):
            os.makedirs(args.output)
        for image_file in file_list:
            img = czifile.imread(os.path.join(input_dir, image_file))
            #img = np.squeeze(img)
            #img_shape = img.shape
            #slice_index = np.argmin(img_shape)
            #img_mip = np.max(img, axis=slice_index)
            viewer = napari.Viewer()
            image = viewer.add_image(img, name='stack')
            #image = viewer.add_image(img_mip, name='MIP')
            points_layer = viewer.add_points([], name='Organoid Centroids', face_color='#00aa7f', size=100)
            raw_filename = image_file.split('.')[0]
            output_path = os.path.join(args.output, raw_filename+'.json')
            @viewer.bind_key('s') # denote save
            def store_centroids(viewer):
                points = viewer.layers['Organoid Centroids'].data # returns numpy array
                data = {'x': list(points[:,0]), 'y':list(points[:,1])}
                #write to json
                with open(output_path, 'w') as outfile:
                    json.dump(data, outfile)
                viewer.close()
            napari.run()
            


'''
# Ruolin's implementation on the stack

result = []
        # image process
        for image in file_list:
            res = np.zeros((520,520)).astype(bool)
            image_list= []
            seg = []
            for zslice in range(8):
                image_path = image.split('.')[0][:-1]+str(zslice)+'.jpg'
                img = plt.imread(os.path.join(input_dir,image_path))  
                img = img[::10,::10]
                image_list.append(img)
                filled = apply_morphologies(img)
                seg.append(filled)
                res = res | filled
                #res = remove_small_objects(res,40)
                #image_list.append(np.mean(image_list,axis=0))
            average_image = np.mean(image_list,axis=0)
            seg = np.array(seg)
            image_list = np.array(image_list)
            
            res = label(res)
            max_label = max(np.unique(res))
            #median_size = find_median_cell_size(res)
            points, point_properties, text_properties, _ = compute_diameter(res)
            print('Image name: ', image)
            print('Image size: ', img.shape)
            print('Number of organoids detected with automatic method: ', len(points))
            result.append([image,len(points)])

            def add_points(event):
                updated_seg = viewer.layers['Final segmentation'].data
                new_points, new_properties, text_properties, _ = compute_diameter(updated_seg)
                viewer.layers.pop(4)
                points_layer = viewer.add_points(np.array(new_points),
                        text=text_properties,
                        properties=new_properties,
                        face_color='point_colors',
                        size=5,
                        name='points')

            viewer = napari.Viewer()
            img_layer = viewer.add_image(image_list, name='image')
            seg_layer = viewer.add_image(seg, name='segmentation',blending='additive',colormap='cyan')
            avgimg_layer = viewer.add_image(average_image, name='Average image')
            final_layer = viewer.add_labels(res, name='Final segmentation')
            final_layer.events.set_data.connect(add_points) 

            if len(points)>0:
                points_layer = viewer.add_points(np.array(points),
                                        text=text_properties,
                                        properties=point_properties,
                                        face_color='point_colors',
                                        size=5,
                                        name='points')
            napari.run()

            @viewer.bind_key('d') # denote done
            def update_cell_numbers(viewer):
                new_points = []
                new_diameter = []
                new_colors = []
                for region in regionprops(viewer.layers['Final segmentation'].data):      
                    y,x = region.centroid
                    new_points.append([y,x])
                    minr, minc, maxr, maxc = region.bbox
                    new_diameter.append(np.around(0.5*(maxr+maxc-minc-minr),2))
                    new_colors.append('red')
                        
                new_properties={
                    'point_colors': np.array(new_colors),
                    'diameter': new_diameter
                }
                viewer.layers.pop(4)
                points_layer = viewer.add_points(np.array(new_points),
                        text=text_properties,
                        properties=new_properties,
                        face_color='point_colors',
                        size=5,
                        name='points')
            @viewer.bind_key('e')
            def close_viewer(): viewer.close()


'''