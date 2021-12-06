import cv2
import csv
import argparse
import glob
import numpy as np

# Global variables
SCALE_FACTOR = 0.2
real_scale = 3 / 488  # mm/pixel


def parse_args():
    parser = argparse.ArgumentParser(description='Segment microplastic content from microscope images of particles.')
    parser.add_argument("--img_name", default='', help='Image to be processed')
    parser.add_argument("--img_dir", default='20210422-S2-All\*_ch00.tif', help="Directory containing images to be processed")
    args = parser.parse_args()
    return args.img_name, args.img_dir

#calculate and return the location and area size of each filter
def findFilterViaPosition(img, center, radius, bg):
    binary_mask = cv2.circle(bg, center, radius, (255, 255, 255), -1)
    #remove the hashtag for the line below if you want to export the filter mask 
    #cv2.imwrite("filter_mask.png", binary_mask)
    img[binary_mask == 0] = 255
    filter_area=3.14 * radius ** 2 / (SCALE_FACTOR ** 2) * (real_scale ** 2)
    print("filter area:", filter_area)
    return img, binary_mask, filter_area


#calculate and return the location and area size of undigested residue using image analysis tools suc as Gaussian blur and binary threshold
def findGITViaContours(img, filter_mask):
    img_gray = cv2.cvtColor(img.copy(), cv2.COLOR_BGR2GRAY)
    #remove the hashtag for the line below if you want to export the grayscale image
    #cv2.imwrite("gray.png", img_gray)
    img_blue = img.copy()[:, :, 0]
    img[filter_mask == 0] = 0
    # find blue mask
    img_blue = img[:, :, 0]
    #remove the hashtag for the line below if you want to export the blue image
    #cv2.imwrite("blue.png", img_blue)
    img_blue_blur = cv2.GaussianBlur(img_blue, (17, 17), 0)
    #remove the hashtag for the line below if you want to export the blue blur image
    #cv2.imwrite("blue_blur.png", img_blue_blur)
    ret1, img_mask1 = cv2.threshold(img_blue_blur, 150, 255, cv2.THRESH_BINARY)
    cv2.imshow("mask1", img_mask1)
    #remove the hashtag for the line below if you want to export the mask
    #cv2.imwrite("mask1.png", img_mask1)
    img_mix = img_blue - img_gray
    img_mix[filter_mask == 0] = 255
    #remove the hashtag for the line below if you want to export the mix channel image
    #cv2.imwrite("mix.png", img_mix)
    img_blur = cv2.GaussianBlur(img_mix, (25, 25), 0)
    #remove the hashtag for the line below if you want to export the gaussian blur
    #cv2.imwrite("mix_blur.png", img_blur)
    cv2.imshow("b-gray blur img", img_blur)
    ret2, img_mask2 = cv2.threshold(img_blur, 85, 255, cv2.THRESH_BINARY_INV)
    cv2.imshow("mask2", img_mask2)
    #remove the hashtag for the line below if you want to export the mask
    #cv2.imwrite("mask2.png", img_mask2)
    img_mask = img_mask1 + img_mask2
    #remove the hashtag for the line below if you want to export the mask
    #cv2.imwrite("mask.png", img_mask)
    cv2.imshow("mask", img_mask)
    # 1b. Find circular contour
    contours, heirarchy = cv2.findContours(img_mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    # Find the area size by non zero, i.e not black part on the mask
    total_area = cv2.countNonZero(img_mask)
    print("git_px:", total_area)
    img_cnt = img.copy()
    for i in range(len(contours)):
        cv2.drawContours(img, contours, i, (0, 255, 0), 1)
    img_cnt[img_mask == 0] = 0
    #calculate total area
    git_area = total_area / (SCALE_FACTOR ** 2) * (real_scale ** 2)
    print("git area:", git_area)
    return img, git_area, img_mask, img_cnt

#extract the value of the blue channel encoded in each pixel selected
def countBlueIntensity(img_mask, img):
    values = [0] * 256
    (row, col, channel) = img.shape
    px_count = 0
    for i in range(row):
        for j in range(col):
            if img_mask[i, j] != 0:
                intensity = img[i, j, 0]
                values[intensity] += 1
                px_count += 1
    print("px count", px_count, sum(values))
    return values

def averageBlueIntensity(values):
    blue_value_sum=0
    for i in range(len(values)):
        blue_value_sum += i*values[i]
    ave_intensity=blue_value_sum/sum(values)
    return ave_intensity

# Input and downsize image, then process the images using the functions defined above
def processImage(img_name):
    img_raw = cv2.imread(img_name)
    #resizing the image into a square around the filter, find the following number in imageJ or photoshop, draw a square around the filter and find the coordinate of the top left corner (x,y), and the length of the square (l) 
    x = 900
    y = 0
    l = 3648
    center = (int(l / 2 * SCALE_FACTOR), int(l / 2 * SCALE_FACTOR))
    radius = int(l / 2 * SCALE_FACTOR * 0.9)
    img = img_raw[y:y + l, x:x + l].copy()
    (height, width, channel) = img.shape
    scaled_height = int(SCALE_FACTOR * height)
    scaled_width = int(SCALE_FACTOR * width)
    img_filter = cv2.resize(img, (scaled_width, scaled_height))
    bg = np.zeros((scaled_width, scaled_height))
    img_git = img_filter.copy()
    print("find filter")
    (filter_cnt, filter_mask,filter_area) = findFilterViaPosition(img_filter, center, radius, bg)
    (git, git_area, git_mask, git_cnt) = findGITViaContours(img_git, filter_mask)
    values = countBlueIntensity(git_mask, img_filter)
    ave_intensity = averageBlueIntensity(values)
    residue_coverage = git_area/filter_area
    cv2.imshow("filter", filter_cnt)
    cv2.imshow("git", git_cnt)
    return values, git_mask, git_cnt, ave_intensity, residue_coverage


# Main function
if __name__ == '__main__':
    # Parse command line arguments
    (img_name, img_dir) = parse_args()
    f = open('output.csv', 'w', newline='\n')
    writer = csv.writer(f, delimiter=",")
    writer.writerow(["img_name"] + ["ave_int"] +["res_cov"]+ list(range(256)))
    if img_name:
        # Process single image
        processImage(img_name)
    elif img_dir:
        # Process all images in directory
        # Find all TIFs in director
        tif_dir = img_dir+"\*.tif"
        for fn in sorted(glob.glob(tif_dir)):
            (values, git_mask, git_cnt, ave_intensity, residue_coverage) = processImage(fn)
            writer.writerow([fn.split("/")[-1]] + [ave_intensity] + [residue_coverage] + values)
            cv2.imwrite(fn.replace(".tif", "_mask.png"), git_mask)
            cv2.imwrite(fn.replace(".tif", "_cnt.png"), git_cnt)
    f.close()

    print("Processing all images")