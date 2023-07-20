# Image Analysis for microplastic extraction of chitinous gut tissue of large decapods

## Image preparation
1. Take the images of stainless-steel filter under the same condition (same location on the image, same light, same white balance for the same batch you need to compare), one filter per image
2. <p id="find-image">Find the universal location of the filter, i.e. draw a square around the filter and find the coordinate of the top left corner (x,y), and the length of the square (l)</p>
 
 
## Requirements
*  miniconda
*  Python==3.8
*  numpy==1.21.1
*  opencv-python==4.5.3.56

Go to line [103-105](https://github.com/joanlyq/microplastic-filter-analysis/blob/22b96c72c7f9c4618930243b407604b9fa8b3d15/filterAnalysis.py#L103-L105)in [filterAnalysis.py](https://github.com/joanlyq/microplastic-filter-analysis/blob/22b96c72c7f9c4618930243b407604b9fa8b3d15/filterAnalysis.py), change `x`,`y`,`l` according to what you find out in [step 2](#find-image) while prepare image
 
* If the images are in other format, open the filterAnalysis.py in notepad, go to [line 139](https://github.com/joanlyq/microplastic-filter-analysis/blob/22b96c72c7f9c4618930243b407604b9fa8b3d15/filterAnalysis.py#L139) `tif_dir = img_dir+"/*.tif`, change `.tif` to the image file type you have, e.g. `.jpg`, `.png`, etc 
 

## Set up
1. Clone repository to your local directory: `git clone https://github.com/joanlyq/microplastic-filter-analysis.git`
2. Change directory to inside repo: `cd microplastic-filter-analysis/`
3. Create conda environment from yml file: `conda env create -f environment.yml`
4. Activate the conda environment: `conda activate microplastic`

## Run
1. Analyze one image, run `python filterAnalysis.py --img_name <the file directory of one single image>`
2. Analyze multiple image, run `python filterAnalysis.py --img_dir <the folder directory of all images>`

## Check the result
The pixel result is saved in the `output.csv` file in the same folder as the scripts

Each row contains: 
*  `img_name` - file name;
*  `ave_int`- average blue intensity (not normalized with sample weight);
*   `res_cov` - residual coverage (full coverage = 1);
*   `0`, `1`, `2`, `3`, ... - all values in blue channel (0-255)

To understand the result, please check the publication.
Li, J. Y., Nankervis, L., & Dawson, A. L. (2022). Digesting the Indigestible: Microplastic Extraction from Prawn Digestive Tracts. Frontiers in Environmental Chemistry, 3, 903314. Access at: <https://doi.org/10.3389/fenvc.2022.903314>

