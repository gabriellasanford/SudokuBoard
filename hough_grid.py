import cv2
import numpy as np
import math
import matplotlib as plt


# Constants
# Canny thresholds
THRESH_ONE = 10
THRESH_TWO = 200

# HoughLinesP parameters
RHO = 1
THETA = math.pi/180
LINE_THRESH = 50
MIN_LENGTH = 25
MAX_GAP = 5

# Line drawing thickness
THICKNESS = 3

# Line drawing colors
BLACK = (255, 0, 0)

# Digit image dimensions
DIGIT_WIDTH = 28
DIGIT_HEIGHT = 28
DIGIT_CHANNELS = 1


# Accepts a grayscale image and returns list of edges from Canny edge detector
def canny_edges(gray_img):
    return cv2.Canny(gray_img, THRESH_ONE, THRESH_TWO)


# Accepts a grayscale image and returns the approximate width and height of
# each cell in the Sudoku grid.
def count_sudoku(gray_img):
    edges = canny_edges(gray_img)
    # Detect points that form lines, and give them to calculate_cells() to get
    # info on the Sudoku grid.
    lines = cv2.HoughLinesP(edges, RHO, THETA, LINE_THRESH, MIN_LENGTH, MAX_GAP)
    grid_info = calculate_cells(lines)
    # Get the individual digit images
    img_squares = collect_squares(gray_img, grid_info)
    for row in img_squares:
        for img in row:
            cv2.imshow("Digit", img)
            cv2.waitKey()
    cv2.destroyAllWindows()


# Accepts a list of lines detected by the Hough transform, and returns a list
# with four elements, of the form: 
# [<top left x>, <top left y>, <cell width>, <cell height>]
def calculate_cells(hough_lines):
    grid_info = []
    x1_list, y1_list, x2_list, y2_list = decompose_lines(hough_lines)
    # Collect the top left corner of the grid
    start_x = min([min(x1_list), min(x2_list)])
    start_y = min([min(y1_list), min(y2_list)])
    grid_info.append(start_x)
    grid_info.append(start_y)
    # Collect the cell dimensions
    cell_tuple = cell_dims(x1_list, y1_list, x2_list, y2_list)
    grid_info.append(cell_tuple[0])
    grid_info.append(cell_tuple[1])
    return grid_info


# Helper function to calculate_cells(), factored out to improve readability.
# Accepts a list generated by cv2.HoughLinesP() and returns four distinct lists
# of points.
def decompose_lines(hough_lines):
    x1_list, y1_list, x2_list, y2_list = [], [], [], []
    # Split the hough line list into four lists of coordinates
    for line in hough_lines:
        for entry in line:
            x1_list.append(entry[0])
            y1_list.append(entry[1])
            x2_list.append(entry[2])
            y2_list.append(entry[3])
    return x1_list, y1_list, x2_list, y2_list


# Helper function to calculate_cells(), factored out to improve readability.
# Accepts four lists of numbers and returns a 2-tuple of the form:
# (<cell width>, <cell height>)
def cell_dims(x1_list, y1_list, x2_list, y2_list):
    # Calculate board width and height by taking the difference between max and
    # min x's and y's, across both lists of x's and y's
    width = ((max(x1_list) - min(x1_list)) \
        + (max(x2_list - min(x2_list)))) // 2
    height = ((max(y1_list) - min(y1_list)) \
        + (max(y2_list - min(y2_list)))) // 2
    # Calculate cell width and height
    cell_width = width // 9
    cell_height = height // 9
    return (cell_width, cell_height)


# Accepts a list of four elements of the form:
# [<top left x>, <top left y>, <cell width>, <cell height>]
# and returns a list of images of the individual cells in 28x28 format for
# digit identification.
def collect_squares(img, grid_info):
    x_pos, y_pos = grid_info[0], grid_info[1]
    cell_width, cell_height = grid_info[2], grid_info[3]
    # 2-d array of digit images in the same arrangement as the Sudoku board
    digit_imgs = [[0 for i in range(9)] for i in range(9)]
    for y in range(1, 10):
        for x in range(1, 10):
            cell_img = grid_slice(img, x_pos + (cell_width * x),\
                y_pos + (cell_height * y), cell_width, cell_height)
            digit_imgs[x-1][y-1] = cv2.resize(cell_img,\
                (DIGIT_WIDTH, DIGIT_HEIGHT))
    return digit_imgs


# Accepts an image, a start position (x and y), and a width and height, and
# returns a slice of the given image of size (width, height) starting at
# position (x, y).
def grid_slice(img, x_start, y_start, width, height):
    x_end = x_start + width + 1
    y_end = y_start + height + 1
    return img[x_start:x_end, y_start:y_end]
