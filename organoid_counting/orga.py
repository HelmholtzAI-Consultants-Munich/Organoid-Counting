'''
from magicgui import magicgui
import numpy as np

def have_button():
    @magicgui(call_button="preprocess")
    def update_display_text(img) -> napari.types.ImageData:
        img = np.squeeze(img)
        img_tuple = (img, {'name': 'Image'}, 'image')
        return img_tuple

'''
