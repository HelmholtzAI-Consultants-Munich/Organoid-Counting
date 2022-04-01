from setuptools import setup

setup(
    name = 'oragnoid-counting',
    version = '0.0.1',
    classifiers = 'Framework :: napari',
    python_requires = '>= 3.7',
    install_requires = ['napari[all]==0.4.12', 
                        'magicgui[pyqt5]==0.3.7',
                        'scikit-image==0.18.3',
                        'aicsimageio[czi]==4.5.2',
                        'opencv-python==4.5.5.62'],

    entry_points={
        'napari.manifest':[
            'organoid-counting'='organoid_counting:napari.yaml',
        ]
    }
)