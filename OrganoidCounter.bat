cd Desktop/Organoid_Counting
git pull https://github.com/HelmholtzAI-Consultants-Munich/Organoid_Counting.git
conda activate imaging
python -W ignore viewer.py --image images/ --auto_count False