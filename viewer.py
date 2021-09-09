import os
import napari
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import skimage
import skimage.feature
import skimage.viewer
from skimage.measure import regionprops,label
from scipy import ndimage as ndi
from skimage.morphology import opening,remove_small_objects,closing,dilation,erosion
from CellCounter import get_binary_map,apply_opening,find_median_cell_size,apply_watershed

def get_args():
    parser = argparse.ArgumentParser(description='Organoid counter')
    parser.add_argument('--image', default=False)
    return parser.parse_args()

if __name__ == '__main__':
    args = get_args()
    
    if os.path.isdir(args.image):
        listOfFiles = list()
        for (dirpath, dirnames, filenames) in os.walk(args.image):
            filenames = [f for f in filenames if not f[0] == '.']
            dirnames[:] = [d for d in dirnames if not d[0] == '.']
            filenames.sort()
            listOfFiles += [os.path.join(dirpath, file) for file in filenames]
    else:
        listOfFiles = [args.image]
    
    result = []
    # image process
    for image in listOfFiles:
        res = np.zeros((520,520)).astype(bool)
        image_list= []
        seg = []
        for zslice in range(8):
            image_path = image.split('.')[0][:-1]+str(zslice)+'.jpg'
            img = plt.imread(image_path)  

            img = img[::10,::10]
            image_list.append(img)
            mask = np.where(img<20,False,True)
#             img = ((image-image.min())/(image.max()-image.min())*255).astype(np.uint16)

            edges = skimage.feature.canny(
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
            seg.append(filled)
            res = res | filled
        
#         res = remove_small_objects(res,40)
        image_list.append(np.mean(image_list,axis=0))
        seg.append(res)
        seg = np.array(seg)
        image_list = np.array(image_list)
        
        res = label(res)
        median_size = find_median_cell_size(res)
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

        points=np.array(points)
        point_properties={
            'point_colors': np.array(colors),
            'diameter': diameter
        }
#         properties = {
#         'diameter': diameter,
#         }
        text_properties = {
            'text': '{diameter}',
            'anchor': 'upper_left',
            'translation': [-5, 0],
            'size': 8,
            'color': 'magenta',
        }
        bboxes = np.array(bboxes)
        print('Image name: ',image)
        print('Image size: ',img.shape)
        print('Number of organoids detected with automatic method: ', len(points))
        result.append([image,len(points)])

        with napari.gui_qt():
            viewer = napari.Viewer()
            img_layer = viewer.add_image(image_list, name='image')
            seg_layer = viewer.add_labels(label(seg), name='segmentation')
#             seg_layer = viewer.add_image(seg, name='segmentation',blending='additive',colormap='cyan')
#                     viewer = napari.view_image(img, name='image')
#             if len(bboxes)>0:
#                 shapes_layer = viewer.add_shapes(bboxes,
#                                         face_color='transparent',
#                                         edge_color='magenta',
#                                         name='bounding box',
#                                         properties=properties,
#                                         text=text_properties,
#                                         edge_width=3)
            if len(points)>0:
                points_layer = viewer.add_points(points,
                                        text=text_properties,
                                        properties=point_properties,
                                        face_color='point_colors',
                                        size=5,
                                        name='points')

            @viewer.bind_key('d') # denote done
            def update_cell_numbers(viewer):
                num_cells = viewer.layers['points'].data.shape[0]
                print('Number of organoids after manual correction: ', num_cells)
                result[-1].append(num_cells)
                viewer.close()
    
        if len(result[-1]) == 2:
            result[-1].append(None)
            
#     df = pd.DataFrame(result, columns =['Name', 'Automatic Cell Number','Corrected Cell Number']) 
#     df.to_excel('result.xlsx')
#     print('Done! All results are saved in result.xlsx!')
