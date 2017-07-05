#!/usr/bin/env python
# coding=utf-8
from __future__ import print_function
# from classes import ExperimentalDrop
# from subprocess import call
# import numpy as np
import cv2
import numpy as np
import matplotlib.pyplot as plt
# import time
# import datetime
# from Tkinter import *
# import tkFileDialog
import sys

import os
import csv
MAX_IMAGE_TO_SCREEN_RATIO = 0.8


def set_drop_region(experimental_drop, experimental_setup):
    # select the drop and needle regions in the image
    if (experimental_setup.auto_test_parameters != None):
        if os.path.exists(experimental_setup.auto_test_parameters):

            data = []
            writer = csv.reader(open(experimental_setup.auto_test_parameters, 'r'))
            for row in writer:
                data.append(row)
        screen_size = experimental_setup.screen_resolution
        image_size = experimental_drop.image.shape
        scale = set_scale(image_size, screen_size)
        screen_position = set_screen_position(screen_size)
        min_x = min(np.int64(data[0][1]), np.int64(data[2][1])) / scale
        max_x = max(np.int64(data[0][1]), np.int64(data[2][1])) / scale
        min_y = min(np.int64(data[1][1]), np.int64(data[3][1])) / scale
        max_y = max(np.int64(data[1][1]), np.int64(data[3][1])) / scale
        experimental_setup.drop_region = [(min_x, min_y), (max_x, max_y)]


    else:
        screen_size = experimental_setup.screen_resolution
        image_size = experimental_drop.image.shape
        scale = set_scale(image_size, screen_size)
        screen_position = set_screen_position(screen_size)
        experimental_setup.drop_region = user_ROI(experimental_drop.image, 'Select drop region', scale, screen_position)

def set_surface_line(experimental_drop, experimental_setup):
    # select the drop and needle regions in the image
    screen_size = experimental_setup.screen_resolution
    image_size = experimental_drop.image.shape
    scale = set_scale(image_size, screen_size)
    screen_position = set_screen_position(screen_size)

    experimental_drop.contact_angles = user_line(experimental_drop.image, experimental_drop.drop_data,
                                                     'Define surface line', scale, screen_position,
                                                     experimental_drop.surface_data, experimental_setup.drop_region,
                                                     experimental_setup)

def set_scale(image_size, screen_size):
    x_ratio = image_size[1] / float(screen_size[0])
    y_ratio = image_size[0] / float(screen_size[1])
    max_ratio = max(x_ratio, y_ratio)
    scale = 1
    if max_ratio > MAX_IMAGE_TO_SCREEN_RATIO:
        scale = MAX_IMAGE_TO_SCREEN_RATIO / max_ratio
    return scale


def set_screen_position(screen_size):
    prec_free_space = 0.5 * (1 - MAX_IMAGE_TO_SCREEN_RATIO)  # percentage room free
    x_position = int(prec_free_space * screen_size[0])
    y_position = int(0.5 * prec_free_space * screen_size[1])  # 0.5 moves window a little bit higher
    return [x_position, y_position]


def user_ROI(raw_image, title, scale, screen_position):  # , line_colour=(0, 0, 255), line_thickness=2):
    global drawing
    global ix, iy
    global fx, fy
    global image_TEMP
    global img
    # raw_image = raw_image2
    # raw_image = np.flipud(cv2.cvtColor(raw_image2,cv2.COLOR_GRAY2BGR))
    # raw_image = np.flipud(raw_image2)
    drawing = False  # true if mouse is pressed
    ix, iy = -1, -1
    fx, fy = -1, -1

    cv2.namedWindow(title, cv2.WINDOW_AUTOSIZE)
    cv2.moveWindow(title, screen_position[0], screen_position[1])
    cv2.setMouseCallback(title, draw_rectangle)
    # scale =1
    image_TEMP = cv2.resize(raw_image, (0, 0), fx=scale, fy=scale)

    img = image_TEMP.copy()

    while (1):
        cv2.imshow(title, img)

        k = cv2.waitKey(1) & 0xFF
        if k != 255:
            if (k == 13) or (k == 32) or (k == 10):
                # either 'return' or 'space' pressed
                # break
                if ((fx - ix) * (fy - iy)) != 0:  # ensure there is an enclosed region
                    break
            if (k == 27):
                # 'esc'
                kill()
    cv2.destroyAllWindows()
    min_x = min(ix, fx) / scale
    max_x = max(ix, fx) / scale
    min_y = min(iy, fy) / scale
    max_y = max(iy, fy) / scale
    return [(min_x, min_y), (max_x, max_y)]


def user_line(raw_image, drop_data, title, scale, screen_position, line,
              region, userinputs):  # , line_colour=(0, 0, 255), line_thickness=2):
    global drawing
    global ix, iy
    global fx, fy
    global image_TEMP
    global img
    # raw_image = raw_image2
    # raw_image = np.flipud(cv2.cvtColor(raw_image2,cv2.COLOR_GRAY2BGR))
    # raw_image = np.flipud(raw_image2)
    drawing = True  # true if mouse is pressed
    ix, iy = -1, -1
    fx, fy = -1, -1

    region = np.floor(region)
    # print(region)

    # print(region[0,0])
    # print(region[1,0])
    # print(region[0,1])
    # print(region[1,1])

    #    cv2.setMouseCallback(title, draw_line)

    scale = 1
    image_TEMP = cv2.resize(raw_image[np.int64(region[0, 1]):np.int64(region[1, 1]),
                            np.int64(region[0, 0]):np.int64(region[1, 0])], (0, 0), fx=scale, fy=scale)

    img = image_TEMP.copy()

    xx = np.array([0, img.shape[1]])
    yy = line(xx)

    ix0, fx0 = xx.astype(int)
    iy0, fy0 = yy.astype(int)

    ix, fx = ix0, fx0
    iy, fy = iy0, fy0
    if userinputs.auto_test_parameters != None:
        if os.path.exists(userinputs.auto_test_parameters):

            data = []
            writer = csv.reader(open(userinputs.auto_test_parameters, 'r'))
            for row in writer:
                data.append(row)
        ix, fx = np.int64(data[5][1]), np.int64(data[7][1])
        iy, fy = np.int64(data[6][1]), np.int64(data[8][1])

    cv2.namedWindow(title, cv2.WINDOW_AUTOSIZE)
    cv2.moveWindow(title, screen_position[0], screen_position[1])

    #    for i in drop_data:
    #        cx,cy = i
    #        print(cx,cy)
    # cv2.circle(raw_image,(int(cx),int(-cy)),10,(255,255,255),0)

    while (1):
        cv2.imshow(title, img)
        # cv2.circle(img,(200,200),5,(255,255,0),2)
        #print((ix,iy),(fx,fy))
        cv2.line(img, (ix, iy), (fx, fy), (0, 255, 0), 2)  # #line_colour,line_thickness)
        # Plot pixels above line

        v1 = (ix - fx, iy - fy)  # (1,coefficients[1])   # Vector 1

        drop = []
        for i in drop_data:
            cx, cy = i
            v2 = (cx - ix, cy - iy)  # Vector 1
            xp = v1[0] * v2[1] - v1[1] * v2[0]  # Cross product
            if xp > 0:
                drop.append((cx, cy))
                cv2.circle(img, (int(cx), int(cy)), 2, (255, 255, 255), 2)

        drop = np.asarray(drop)

        delta = 1
        Npts = 30
        Ndrop = np.shape(drop)[0]
        pts1 = np.zeros((Npts, 2))
        pts2 = np.zeros((Npts, 2))

        for i in range(Npts):
            pts1[i, :] = drop[delta * i, :]
            pts2[i, :] = drop[Ndrop - 1 - delta * i, :]
            cv2.circle(img, (int(pts1[i, 0]), int(pts1[i, 1])), 2, (0, 0, 255), 2)
            cv2.circle(img, (int(pts2[i, 0]), int(pts2[i, 1])), 2, (0, 0, 255), 2)

        fit_local1 = np.polyfit(pts1[:, 0], pts1[:, 1], 2)
        fit_local2 = np.polyfit(pts2[:, 0], pts2[:, 1], 2)

        line_local1 = np.poly1d(fit_local1)
        line_local2 = np.poly1d(fit_local2)

        x_local1 = np.array([min(pts1[:, 0]) - 10, max(pts1[:, 0]) + 10])
        f_local1 = line_local1(x_local1)
        f_local1_prime = line_local1.deriv(1)

        x_local2 = np.array([min(pts2[:, 0]) - 10, max(pts2[:, 0]) + 10])
        f_local2 = line_local2(x_local2)
        f_local2_prime = line_local2.deriv(1)

        tangent1 = f_local1_prime(pts1[0, 0]) * (x_local1 - pts1[0, 0]) + pts1[0, 1]
        tangent2 = f_local2_prime(pts2[0, 0]) * (x_local2 - pts2[0, 0]) + pts2[0, 1]

        cv2.line(img, (np.int(x_local1[0]), np.int(tangent1[0])), (np.int(x_local1[1]), np.int(tangent1[1])), (255, 0, 0), 2)
        cv2.line(img, (np.int(x_local2[0]), np.int(tangent2[0])), (np.int(x_local2[1]), np.int(tangent2[1])), (255, 0, 0), 2)

        m1 = f_local1_prime(pts1[0, 0])
        m2 = f_local2_prime(pts2[0, 0])

        m_surf = float(iy - fy) / float(ix - fx)

        if (m1 > 0):
            contact_angle1 = np.pi - np.arctan((m1 - m_surf) / (1 + m1 * m_surf))
        elif (m1 < 0):
            contact_angle1 = -np.arctan((m1 - m_surf) / (1 + m1 * m_surf))
        else:
            contact_angle1 = np.pi / 2

        if (m2 < 0):
            contact_angle2 = np.pi + np.arctan((m2 - m_surf) / (1 + m2 * m_surf))
        elif (m2 > 0):
            contact_angle2 = np.arctan((m2 - m_surf) / (1 + m2 * m_surf))
        else:
            contact_angle2 = np.pi / 2

        contact_angle1 = contact_angle1 * 180 / np.pi
        contact_angle2 = contact_angle2 * 180 / np.pi

        if (userinputs.auto_test_parameters == None):
            k = cv2.waitKey(1) & 0xFF
        else:
            k = 13

        if k != 255:

            if (k == 13) or (k == 32):
                # either 'return' or 'space' pressed
                # break
                if ((fx - ix) * (fy - iy)) != 0:  # ensure there is an enclosed region
                    break
            if (k == 27):
                # 'esc'
                kill()
            if (k == -1):
                continue

            if (k == ord('w')) or (k == 82):  # up key (down on image)
                fy = fy + 1
                iy = iy + 1

                image_TEMP = cv2.resize(raw_image[np.int64(region[0, 1]):np.int64(region[1, 1]),
                            np.int64(region[0, 0]):np.int64(region[1, 0])], (0, 0), fx=scale, fy=scale)
                img = image_TEMP.copy()
                cv2.line(img, (ix, iy), (fx, fy), (0, 255, 0), 2)  # #line_colour,line_thickness)    cv2.line
            if (k == ord('s')) or (k == 84):  # down key (up on image)
                fy = fy - 1
                iy = iy - 1

                image_TEMP = cv2.resize(raw_image[np.int64(region[0, 1]):np.int64(region[1, 1]),
                            np.int64(region[0, 0]):np.int64(region[1, 0])], (0, 0), fx=scale, fy=scale)
                img = image_TEMP.copy()
                cv2.line(img, (ix, iy), (fx, fy), (0, 255, 0), 2)  # #line_colour,line_thickness)    cv2.line

            if (k == ord('o')) or (k == 111):  # "o" key
                fx, fy = fx0, fy0
                ix, iy = ix0, iy0

                image_TEMP = cv2.resize(raw_image[np.int64(region[0, 1]):np.int64(region[1, 1]),
                            np.int64(region[0, 0]):np.int64(region[1, 0])], (0, 0), fx=scale, fy=scale)
                img = image_TEMP.copy()
                cv2.line(img, (ix, iy), (fx, fy), (0, 255, 0), 2)  # #line_colour,line_thickness)    cv2.line

            if (k == ord('a')) or (k == ord('d')) or (k == 81) or (k == 83):  # 83: right key (Clockwise)
                x0 = np.array([ix, iy])
                x1 = np.array([fx, fy])
                xc = 0.5 * (x0 + x1)
                theta = 1.0 / 180 * np.pi
                if (k == ord('a')) or (k == 81):  # left key
                    theta = -theta

                rotation = np.zeros((2, 2))
                rotation[0, 0] = np.cos(theta)
                rotation[0, 1] = -np.sin(theta)
                rotation[1, 0] = np.sin(theta)
                rotation[1, 1] = np.cos(theta)

                x0r = np.dot(rotation, (x0 - xc).T) + xc
                x1r = np.dot(rotation, (x1 - xc).T) + xc

                ix, iy = x0r.astype(int)
                fx, fy = x1r.astype(int)

                image_TEMP = cv2.resize(raw_image[np.int64(region[0, 1]):np.int64(region[1, 1]),
                            np.int64(region[0, 0]):np.int64(region[1, 0])], (0, 0), fx=scale, fy=scale)
                img = image_TEMP.copy()
                cv2.line(img, (ix, iy), (fx, fy), (0, 255, 0), 2)  # #line_colour,line_thickness)    cv2.line

            if (k == ord('p')) or (k == 112):  # 'p' key
                print(contact_angle1, contact_angle2)
                # print(m1,m2)

            if (k == -1):
                continue
            else:
                print(k)


    if userinputs.auto_test_parameters != None and userinputs.conAn_type == 1:
        cv2.imwrite(os.path.dirname(os.path.dirname(__file__)) + '/outputs/contactAnDrop.jpg', img)

        img1 = open(os.path.dirname(os.path.dirname(__file__)) + '/standard_outputs/contactAnDrop.jpg', "r")
        img2 = open(os.path.dirname(os.path.dirname(__file__)) + '/outputs/contactAnDrop.jpg', "r")

        if img1.read() == img2.read():
            print("the drop region and surface line are correct")
        else:
            print("the drop region and surface line are incorrect")

    if userinputs.auto_test_parameters != None and userinputs.conAn_type == 2:
        cv2.imwrite(os.path.dirname(os.path.dirname(__file__)) + '/outputs/contactAnNeedleDrop.jpg', img)

        img1 = open(os.path.dirname(os.path.dirname(__file__)) + '/standard_outputs/contactAnNeedleDrop.jpg', "r")
        img2 = open(os.path.dirname(os.path.dirname(__file__)) + '/outputs/contactAnNeedleDrop.jpg', "r")

        if img1.read() == img2.read():
            print("the drop region and surface line are correct")
        else:
            print("the drop region and surface line are incorrect")

    cv2.destroyAllWindows()
    min_x = min(ix, fx) / scale
    max_x = max(ix, fx) / scale
    min_y = min(iy, fy) / scale
    max_y = max(iy, fy) / scale
    #print((ix,iy), (fx,fy))
    return [contact_angle1, contact_angle2]


# mouse callback function
def draw_rectangle(event, x, y, flags, param):
    global ix, iy, drawing
    global fx, fy
    global image_TEMP
    global img

    if event == cv2.EVENT_LBUTTONDOWN:
        img = image_TEMP.copy()
        drawing = True
        ix, iy = x, y

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing == True:
            img = image_TEMP.copy()
            cv2.rectangle(img, (ix, iy), (x, y), (0, 0, 255), 2)  # line_colour,line_thickness)

    elif event == cv2.EVENT_LBUTTONUP:
        img = image_TEMP.copy()
        drawing = False
        fx, fy = x, y
        cv2.rectangle(img, (ix, iy), (fx, fy), (0, 255, 0), 2)  # #line_colour,line_thickness)

        #print((ix,iy),(fx,fy))

# mouse callback function
def draw_line(event, x, y, flags, param):
    global ix, iy, drawing
    global fx, fy
    global image_TEMP
    global img

    if event == cv2.EVENT_LBUTTONDOWN:
        img = image_TEMP.copy()
        drawing = True
        ix, iy = x, y

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing == True:
            img = image_TEMP.copy()
            cv2.line(img, (ix, iy), (x, y), (0, 0, 255), 2)  # line_colour,line_thickness)

    elif event == cv2.EVENT_LBUTTONUP:
        img = image_TEMP.copy()
        drawing = False
        fx, fy = x, y
        cv2.line(img, (ix, iy), (fx, fy), (0, 255, 0), 2)  # #line_colour,line_thickness)



def kill():
    sys.exit()
