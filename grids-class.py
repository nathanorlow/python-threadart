import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from sklearn.cluster import KMeans
import numpy as np

import os.path as ospath
from collections import defaultdict
from sortedcontainers import SortedSet

from circle import Circle
from square import Square
from line import Line

channel_count = 3

PIXEL_COUNT = 100
PIN_COUNT = 100
HALF_PIN_COUNT = round(PIN_COUNT / 2)
LINES_TO_SHOW = PIN_COUNT
TOTAL_LINES = round((LINES_TO_SHOW + 1) * (LINES_TO_SHOW) /2)
FORCE_NEW_WEIGHT_MATRIX = False

GRAM_SCALE = .05 #or .03 for face
TOTAL_MATCHES_REQUESTED = 1000

#FILENAME = "sunflower_gray100"
#FILENAME = "plumface-contrast"
FILENAME = "spinner"
EXTENSION = ".png"

weight_matrix_file_name = f"pin{PIN_COUNT}_pixel{PIXEL_COUNT}.csv"
gram_matrix_file_name = f"gram_pin{PIN_COUNT}_pixel{PIXEL_COUNT}.csv"      

def show_size(matrix, matrix_name):
    shape = matrix.shape
    print( f"The shape is {shape} for {matrix_name}" )

print(f"total lines is {TOTAL_LINES}")

input_image=mpimg.imread(FILENAME + EXTENSION)

[height, width, channel_count] = input_image.shape
input_image = np.ones([height, width, channel_count]) - input_image #white in image should be black (0)

print(f"Input image height {height} width {height}")
image_row = input_image.reshape([1, height * width, channel_count])
image_row_first = image_row[:,:,1]
im = image_row_first.reshape([height*width])

assert(height == PIXEL_COUNT)

square = Square(PIXEL_COUNT)
PIXEL_COUNT = square.get_pixel_count() #try to refactor to move pixel count dependencies to square
circle = Circle(PIN_COUNT)

weight_matrix = np.zeros([PIXEL_COUNT*PIXEL_COUNT, TOTAL_LINES])

line_index = 0
PIXEL_WIDTH = square.get_pixel_width()


pin_to_pin = defaultdict(SortedSet)
line_index_to_ij = dict() #allows to easily get ij from the line index


if((not FORCE_NEW_WEIGHT_MATRIX) and ospath.isfile(weight_matrix_file_name)):
    print(f"Using saved weight matrix {weight_matrix_file_name}")
    weight_matrix = np.genfromtxt(weight_matrix_file_name, delimiter=',')
else:
    print(f"Re-computing weight matrix and will save to {weight_matrix_file_name}")
    for i in range(LINES_TO_SHOW):
        print("i = " + str(i))
        for j in range(LINES_TO_SHOW):
            if(i >= j): #is actually a point not a line (and avoids double counting)
                continue
            line = circle.line_coord_by_index(i, j)
            for x_index in line.x_range_by_index(PIXEL_WIDTH, PIXEL_COUNT):
                for y_index in range(PIXEL_COUNT):
                    if(line.y_index_near_line_for_x_index(x_index, y_index, PIXEL_WIDTH)):
                        next #not near line so already 0

                    (center_x, center_y) = square.center_by_index(x_index, y_index)
                    pixel_weight = line.weight_for_center(center_x, center_y, PIXEL_WIDTH)# / HALF_PIN_COUNT
                    weight_matrix[y_index * PIXEL_COUNT + x_index, line_index] = pixel_weight
            line_index +=1
    np.savetxt(weight_matrix_file_name, weight_matrix, delimiter=",", fmt="%.5f")

print("Done computing lines")
line_index =0
connected_index = 0
for i in range(LINES_TO_SHOW):
    for j in range(LINES_TO_SHOW):
        if(i >= j): #is actually a point not a line (and avoids double counting)
            continue
        line_index_to_ij[line_index] =(i,j)
        line_index +=1


#print("line index to ij", line_index_to_ij)
if(ospath.isfile(gram_matrix_file_name)):
    print(f"Using saved gram matrix {gram_matrix_file_name}")
    gram_matrix = np.genfromtxt(gram_matrix_file_name, delimiter=',')
    print("Done loading gram matrix")
else:
    gram_matrix = np.matmul(np.transpose(weight_matrix), weight_matrix)
    np.savetxt(gram_matrix_file_name, gram_matrix, delimiter=",", fmt="%.5f")
    print("Done saving gram matrix")

print("Computing match matrix from weight matrix")
match_matrix = np.matmul(im, weight_matrix)

lines_im = np.zeros(PIXEL_COUNT * PIXEL_COUNT)
match_place_max = TOTAL_MATCHES_REQUESTED
for match_place in range(TOTAL_MATCHES_REQUESTED):
    #todo: go through match matrix -- find the largest entry, then find that row on weight matrix and subtract it (transpose) from image

    max_match_index = np.argmax(match_matrix)
    match_value = match_matrix[max_match_index]
    print(f"place {match_place}: picked index {max_match_index} with match value {match_value}")
    if(match_value <= 0 ):
        print("Match value not positive, so stopping")
        match_place_max = match_place - 1
        break
    line_chosen = np.transpose(weight_matrix[:,max_match_index])
    im = im - line_chosen
    lines_im = lines_im + GRAM_SCALE * line_chosen
    #now remove this indexfrom selection
    match_matrix[max_match_index] = 0

    match_matrix = match_matrix - GRAM_SCALE * gram_matrix[max_match_index, :]
    (i,j) = line_index_to_ij.get(max_match_index)
    #print(f"({i},{j}) is from index {max_match_index}")

    pin_to_pin[i].add(j)
    pin_to_pin[j].add(i)

#print("pin to pin ", pin_to_pin)
chosen_pin_order = list()
current_index = PIN_COUNT - 1
previous_index = 0 #for confirming nearby
connected_index = 0
match_place = 0
nearby_list = []

while(connected_index < PIN_COUNT):
    chosen_pin_order.append(current_index) #add it to the list
    if(match_place % 25 == 24):
        print("")
    if(abs(current_index - previous_index) > 5):
        if(len(nearby_list) > 0):
           print ("Nearby points: " + ", ".join(nearby_list))
           nearby_list = []
           match_place += 1;
        print(f"{match_place}: Added pin {current_index}")
        match_place += 1
    else:
        nearby_list.append(str(current_index))
    previous_index = current_index

    connected_index = current_index
    next_connections = pin_to_pin[connected_index]
    #but maybe this index doesn't have any next_connections, so pick connections from a different index

    while(len(next_connections) == 0):
        if(connected_index <= current_index):
            connected_index -= 1
        else:
            connected_index += 1
        if(connected_index < 0):
            connected_index = current_index + 1
        if(connected_index >= PIN_COUNT):
            print(f"Ran out of connections to check (no pin {connected_index})")
            break
        #print(f"Started at {current_index} and will next check {connected_index}")
        next_connections = pin_to_pin[connected_index]

    #break out early if no more connections
    if(connected_index >= PIN_COUNT):
        break
    if(current_index != connected_index): #announce if picked a different connection
        print(f"{match_place}: Go from {current_index} to {connected_index}")
        match_place += 1

    actual_next_index = next_connections.pop() #this is the usual direction
    reverse_connections = pin_to_pin[actual_next_index]
    reverse_connections.remove(connected_index) #also remove the reverse direction

    current_index = actual_next_index

lines_im_square = lines_im.reshape(PIXEL_COUNT, PIXEL_COUNT)

image_plot = plt.imshow(lines_im_square, vmin=0, vmax=.8, cmap='gray_r', )
plt.show()

