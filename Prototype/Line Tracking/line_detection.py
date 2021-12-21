from time import sleep

import cv2 as cv
import numpy as np
import line2class as l2c

# image size for warped image
img_width = img_height = 720

# real dimensions (cm)
width = 58.8
height = 65.5

# factor for px to distance (cm) ratio
factorX = img_width / width
factorY = img_height / height

x_step = 30  # steps for coordinate list, adjust according to camera distance
# neighbor_dst_threshold = 20
edge_split_dst_threshold = 8  # min. distance between two edges in px
neighbor_amount_threshold = 8  # max. amount of elements per row, i.e. how many white px per row are allowed


def displayimage(window_name, input_image):
    while True:
        cv.imshow(window_name, input_image)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break


def average(lst):
    average_sum = 0
    for (x, y) in lst:
        average_sum = average_sum + y

    return [x, int(average_sum / len(lst))]


# gray_img = cv.imread("testImages_PNG/WIN_20210802_18_52_56_Pro.jpg", cv.IMREAD_GRAYSCALE)
# gray_img = cv.imread("testImages_PNG/circle.jpg", cv.IMREAD_GRAYSCALE)
gray_img = cv.imread("testImages_PNG/track.png", cv.IMREAD_GRAYSCALE)

# blur
kernel_size = 3
blur_gray_img = cv.GaussianBlur(gray_img, (kernel_size, kernel_size), 0)

# edge detection (Sobel + Canny)
low_threshold = 100
high_threshold = 150
edges = cv.Canny(blur_gray_img, low_threshold, high_threshold)
displayimage('Edge Detection', edges)

# image correction algo
# ---------------------
'''
start_point = (-1, -1)
px_threshold = 5
px_threshold_range = px_threshold + 1

# connect lines
x = 0
flag = False
for row in edges:
    y = 0
    for element in row:
        if element == 255:
            if not flag:
                flag = True
                start_point = (x, y)
            neighbor_count = 0
            for x_neighbor in range(x - 1, x + 2):
                for y_neighbor in range(y - 1, y + 2):
                    if edges[x_neighbor][y_neighbor] == 255 and (x_neighbor, y_neighbor) != (x, y):
                        neighbor_count += 1
            if neighbor_count == 0:
                edges[x][y] = 0
            if neighbor_count == 1:
                print(x, y)  # current point with only 1 neighbor
                for x_neighbor in range(x - px_threshold, x + px_threshold_range):  # 3, 4
                    for y_neighbor in range(y - px_threshold, y + px_threshold_range):
                        neighbors_neighbor_count = 0
                        if edges[x_neighbor][y_neighbor] == 255 and (x_neighbor, y_neighbor) != (
                        x, y):  # all neighbors of current point with distance 3
                            for x_neighbors_neighbor in range(x_neighbor - 1, x_neighbor + 2):
                                for y_neighbors_neighbor in range(y_neighbor - 1, y_neighbor + 2):
                                    if edges[x_neighbors_neighbor][y_neighbors_neighbor] == 255 \
                                            and (x_neighbors_neighbor, y_neighbors_neighbor) != (
                                    x_neighbor, y_neighbor):  # count neighbors of neighbors with distance 3
                                        neighbors_neighbor_count += 1
                            if neighbors_neighbor_count == 1:  # if one neighbor of distance 3 also only has one neighbor -> connect them together
                                print(f'neighbor: {(x_neighbor, y_neighbor)}')
                                x_dst = abs(x - x_neighbor)
                                print(f'xdst: {x_dst}')
                                y_dst = abs(y - y_neighbor)
                                print(f'ydst: {y_dst}')
                                for i in range(1, x_dst + 1):
                                    for j in range(1, y_dst + 1):
                                        if x > x_neighbor:
                                            if y > y_neighbor:
                                                edges[x - i][y - j] = 255
                                                print(f'corrected: {((x - i), (y - j))}')
                                            else:
                                                edges[x - i][y + j] = 255
                                                print(f'corrected: {((x - i), (y + j))}')
                                        else:
                                            if y > y_neighbor:
                                                edges[x + i][y - j] = 255
                                                print(f'corrected: {((x + i), (y - j))}')
                                            else:
                                                edges[x + i][y + j] = 255
                                                print(f'corrected: {((x + i), (y + j))}')
            # if neighbor_count == 2:
        y += 1
    x += 1
count2 = x = 0
for row in edges:
    y = 0
    for element in row:
        if element == 255:
            count2 += 1
        y = y + 1
    x = x + 1
print(f'count2: {count2}')
print(f'start point: {start_point}')
'''

# thinning lines -> muss nicht Pfad folgen
# if px hat 2 neighbors, und 1 dieser neighbor hat 3 connections -> entferne px
x = 0
for row in edges:
    y = 0
    for element in row:
        if element == 255:

            neighbor_count = 0
            for x_neighbor in range(x - 1, x + 2):
                for y_neighbor in range(y - 1, y + 2):
                    if edges[x_neighbor][y_neighbor] == 255 and (x_neighbor, y_neighbor) != (x, y):
                        neighbor_count += 1
            # check how many neighbors current point has
            # if it has 2 neighbors:

            if neighbor_count == 2:  # and mode == 'thinning'

                # check how many neighbors the neighbors have
                amount_3_neighbors = 0
                for x_neighbor in range(x - 1, x + 2):
                    for y_neighbor in range(y - 1, y + 2):
                        if edges[x_neighbor][y_neighbor] == 255 and (x_neighbor, y_neighbor) != (x, y):

                            neighbors_neighbor_count = 0

                            for x_neighbors_neighbor in range(x_neighbor - 1, x_neighbor + 2):
                                for y_neighbors_neighbor in range(y_neighbor - 1, y_neighbor + 2):
                                    if edges[x_neighbors_neighbor][y_neighbors_neighbor] == 255 \
                                            and (x_neighbors_neighbor, y_neighbors_neighbor) != (x_neighbor, y_neighbor):  # if one of neighbors with distance 3 also only has 1 neighbor
                                        neighbors_neighbor_count += 1
                            # if one neighbor has 3 neighbors, count amount
                            if neighbors_neighbor_count == 3:  # and mode == 'thinning'
                                amount_3_neighbors += 1
                if amount_3_neighbors == 2:
                    print(x, y)  # current point with only 2 neighbor
                    edges[x][y] = 0
        y += 1
    x += 1
# if px hat mehr als 2 connection?

x = 0
for row in edges:
    y = 0
    for element in row:
        if element == 255:

            no_neighbor_top_count = False
            no_neighbor_bottom_count = False
            no_neighbor_left_count = False
            no_neighbor_right_count = False

            # scan top and bottom
            i = 0
            for x_neighbor in range(x - 1, x + 2, 2):
                neighbor_count = 0
                for y_neighbor in range(y - 1, y + 2):
                    if edges[x_neighbor][y_neighbor] == 255:
                        neighbor_count += 1

                if not neighbor_count:
                    if not i:
                        no_neighbor_top_count = True
                    if i:
                        no_neighbor_bottom_count = True
                i += 1

            # scan left and right
            i = 0
            for y_neighbor in range(y - 1, y + 2, 2):
                neighbor_count = 0
                for x_neighbor in range(x - 1, x + 2):
                    if edges[x_neighbor][y_neighbor] == 255:
                        neighbor_count += 1
                if not neighbor_count:
                    if not i:
                        no_neighbor_left_count = True
                    if i:
                        no_neighbor_right_count = True
                i += 1



        y += 1
    x += 1
displayimage('corrected Image', edges)
input('in:')

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

'''
# if not using image correction
start_point = (-1, -1)

x = 0
flag = False
for row in edges:
    y = 0
    for element in row:
        if element == 255:
            start_point = (x, y)
            flag = True
            break
        y = y + 1
    x = x + 1
    if flag:
        break
print(start_point)
'''

# set start_point for track finding
current_point = start_point
point_lst = [start_point]

# set scan_width for scanning neighbor range
scan_width = 1

while True:

    print(point_lst)
    flag = False
    stop_flag = False
    neighbor_count = 0
    (x, y) = current_point

    # iterate through neighbors of current_point within scan_width
    for x_neighbor in range(x - scan_width, x + scan_width + 1):
        for y_neighbor in range(y - scan_width, y + scan_width + 1):

            try:

                neighbor_point = (x_neighbor, y_neighbor)

                # if neighbor == 255 (white px), i.e. part of track and not current_point
                if edges[x_neighbor][y_neighbor] == 255 and neighbor_point != current_point:

                    same = False
                    neighbor_count += 1

                    # check if neighbor is one of previous points stored in points_lst
                    for i in range(len(point_lst) - 1, -1, -1):  # 0 oder -1?

                        if (x_neighbor, y_neighbor) == point_lst[i]:
                            same = True
                            break

                    # if neighbor is a new point
                    if not same:

                        # make neighbor as current_point and add to points_lst
                        current_point = (x_neighbor, y_neighbor)
                        point_lst.append(current_point)
                        print(current_point)

                        # display current_point
                        my_point = edges.copy()
                        cv.circle(my_point, (current_point[1], current_point[0]), 4, (255, 255, 255), -1)
                        cv.imshow('Current Path', my_point)
                        displayimage('Current Path', my_point)

                        flag = True  # new neighbor was found, set flag for stop iterating through neighbors
                        # break

                    #  if neighbor of current_point == start point (gone full circle)
                    if len(point_lst) > 9 and (x_neighbor, y_neighbor) == point_lst[0]:
                        stop_flag = True  # set flag for stop track finding
                        break

            except IndexError:
                current_point = (x_neighbor, y_neighbor)
                point_lst.append(current_point)

        if flag:
            # stop iterating through neighbors, new current_point is start_point for next loop
            break

    if stop_flag:

        # stop track finding
        print('end')
        break

    # if no new neighbor was found
    if not flag:

        print(f'no neighbor found: {current_point}')
        #  is track start == end? if yes -> while current_point != points_lst[0]
        #  thinning
        #  connect lines
        '''
        user_input = input(f'is end? [y/n]')
        if user_input == 'y':
            break
        if user_input == 'n':
        '''

        # if current_point has no neighbors besides previous points (is open ended)
        if neighbor_count > 0:
            edges[current_point[0]][current_point[1]] = 0  # delete current_point from image
            del point_lst[-1]  # delete current_point from list
            current_point = point_lst[-1]  # go back to last point

cv.waitKey(0)

'''
# own algo
edges_coordinates = []

x = 0
for i in range(0, len(edges), x_step):
    # print(row)
    row_list = []
    y = 0
    row = edges[i]
    for element in row:
        if element == 255:
            row_list.append([x, y])
        y = y + 1
    edges_coordinates.append(row_list)
    x = x + x_step

# print(edges_coordinates)
# print(len(edges_coordinates))

edges_average_coordinates = []

for row in edges_coordinates:
    row_avg_list = []
    if neighbor_amount_threshold > len(row) > 1:
        row_groups_list = []
        start_point = element_count = y_prev = 0

        for (x, y_current) in row:
            element_count = element_count + 1
            if y_prev != 0:
                if y_current - y_prev > edge_split_dst_threshold or element_count == len(row):
                    split_point = element_count
                    row_groups_list.append(row[start_point:split_point])
                    start_point = split_point
            else:
                y_prev = y_current

        for edge in row_groups_list:
            # row_avg_list.append(average(edge))
            row_avg_list.append(edge[0])

    if row_avg_list:
        edges_average_coordinates.append(row_avg_list)

print(f'res: {edges_average_coordinates}')

line_average_coordinates = []
for row in edges_average_coordinates:
    line_average_coordinates.append(average(row))

print(f'res: {line_average_coordinates}')

# invert x- / y-coordinates
for i in range(0, len(line_average_coordinates)):
    (y, x) = line_average_coordinates[i]
    line_average_coordinates[i] = [x, y]

track = edges.copy()
# cv.circle(track, (0, 69), 4, (255, 255, 255), -1)

for (x, y) in line_average_coordinates:
    cv.circle(track, (x, y), 4, (255, 255, 255), -1)

displayimage('track markings', track)

# convert2realdimension()

track_coordinates = []

for i in range(0, len(line_average_coordinates)):
    (x, y) = line_average_coordinates[i]
    track_coordinates.append([round(x / factorX, 2), round(y / factorY, 2)])
print(track_coordinates)

# sortieren
# add angle between point (line2class)
vector_table = []
x_prev = y_prev = -1
for (x, y) in track_coordinates:
    if x_prev >= 0 and y_prev >= 0:
        vector_table.append(l2c.RoadPoint(x, y, x_prev, y_prev))
    else:
        x_prev, y_prev = x, y

for rp in vector_table:
    rp.printinfo()
'''
