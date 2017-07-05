#!/usr/bin/env python
# coding=utf-8
from __future__ import print_function
import numpy as np
import cv2
import matplotlib.pyplot as plt

# import time
# import datetime

BLUR_SIZE = 3
VERSION_CV2 = cv2.__version__

class ContactExtractProfile:

    def extract_drop_profile(self, raw_experiment, user_inputs):
        profile_crop = self.image_crop(raw_experiment.image, user_inputs.drop_region)
        # profile_edges = detect_edges(profile_crop, raw_experiment, user_inputs.drop_region)
        # profile, raw_experiment.ret = detect_edges(profile_crop, raw_experiment, user_inputs.drop_region)
        profile, surface, raw_experiment.ret = self.detect_edges(profile_crop, raw_experiment, user_inputs.drop_region, -1, 1,
                                                            user_inputs.threshold_val)
        raw_experiment.drop_data = profile  # [0]
        raw_experiment.surface_data = surface


    #    needle_crop = image_crop(raw_experiment.image, user_inputs.needle_region)
    #    raw_experiment.needle_data, ret = detect_edges(needle_crop, raw_experiment, user_inputs.needle_region, raw_experiment.ret, 2)



    # # detect needle edges
    # needle_crop = image_crop(raw_experiment.image, user_inputs.needle_region)
    # raw_experiment.needle_data = detect_edges(needle_crop, user_inputs.needle_region)



    def image_crop(self, image, points):
        # return image[points[0][0]:points[0][1], points[1][0]:points[1][1]]
        # return image[points[0][1]:points[1][1], points[0][0]:points[1][0]]
        # imageUD = np.flipud(image)
        # pixels are referenced as image[y][x] - row major order

        return image[np.int64(points[0][1]):np.int64(points[1][1]), np.int64(points[0][0]):np.int64(points[1][0])]


    def detect_edges(self, image, raw_experiment, points, ret, n_contours, threshValue):
        # image = np.flipud(imageUD)
        if len(image.shape) != 2:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        blur = cv2.GaussianBlur(image, (BLUR_SIZE, BLUR_SIZE), 0)  # apply Gaussian blur to drop edge
        #    if ret == -1:
        ret, thresh = cv2.threshold(blur, threshValue, 255, cv2.THRESH_BINARY)  # +cv2.THRESH_OTSU) # calculate thresholding
        #print(ret)

        # cv2.imshow('img',thresh)
        # cv2.waitKey(0)

        # else:
        #     ret, thresh = cv2.threshold(blur,ret,255,cv2.THRESH_BINARY) # calculate thresholding
        # these values seem to agree with
        # - http://www.academypublisher.com/proc/isip09/papers/isip09p109.pdf
        # - http://stackoverflow.com/questions/4292249/automatic-calculation-of-low-and-high-thresholds-for-the-canny-operation-in-open
        # edges = cv2.Canny(thresh,0.5*ret,ret) # detect edges using Canny edge detection

        # error in PDT code - shouldn't threshold before Canny - otherwise Canny is useless
        # edges = cv2.Canny(blur,0.5*ret,ret) # detect edges using Canny edge detection
        if float(VERSION_CV2[0]) > 2:  # Version 3 of opencv returns an extra argument
            _, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        else:
            contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

        contour_lengths = []  # list to hold all areas

        for contour in contours:
            length = cv2.arcLength(contour, 0)
            contour_lengths.append(length)

        indexed_contour_lengths = np.array(contour_lengths).argsort()[::-1]
        indexed_contours_to_return = indexed_contour_lengths[:n_contours]

        # print (indexed_contour_lengths)

        # print (indexed_contours_to_return)

        image_height = raw_experiment.image.shape[0]

        offset = [0, 0]  # [0, image.shape[1]]
        points = []
        for index in indexed_contours_to_return:
            current_contour = contours[index][:, 0]
            # print(current_contour)
            # print(contours)

            for i in range(current_contour.shape[0]):
                current_contour[i, 1] = current_contour[i, 1]
                current_contour[i, :] = current_contour[i, :] + offset
                #        points.append(current_contour[current_contour[:,1].argsort()])

        size = 0
        cropped_image_height = image.shape[0]
        cropped_image_width = image.shape[1]

        #print(cropped_image_height)

        #print(cropped_image_width)

        # version 3 begin with 0
        # should change the parameters to minus 1
        if float(VERSION_CV2[0]) > 2:
            # version 3
            startIndex = 0
            endIndex = 1
        else:
            # version 2
            startIndex = 1
            endIndex = 2
        for i in range(current_contour.shape[0]):  # Trim edges from contour
            if current_contour[i, 0] != startIndex:
                if current_contour[i, 0] != cropped_image_width - endIndex:
                    if current_contour[i, 1] != startIndex:
                        if current_contour[i, 1] != (cropped_image_height - endIndex):
                            size = size + 1

                            #    print(current_contour.shape[0])
                            #    print(size)
        current_contour_trimmed = np.zeros((size, 2))

        index = 0
        for i in range(current_contour.shape[0]):
            if current_contour[i, 0] != startIndex:
                if current_contour[i, 0] != cropped_image_width - endIndex:
                    if current_contour[i, 1] != startIndex:
                        if current_contour[i, 1] != (cropped_image_height - endIndex):
                            current_contour_trimmed[index, :] = current_contour[i, :]
                            index = index + 1

        contour_x = current_contour_trimmed[:, 0]
        contour_y = current_contour_trimmed[:, 1]
        N = np.shape(contour_x)[0]

        # print N
        #plt.axis('equal')
        #plt.plot(contour_x, contour_y, 'r-')
        #plt.show()
        # cv2.imshow('img',image)
        # cv2.drawContours(image,current_contour_trimmed)
        # cv2.drawContours(image,contours,0,(0,255,0),10)
        # cv2.drawContours(image,contours,1,(255,255,0),10)
        # cv2.waitKey(0)

        A = 50
        xx = np.concatenate((contour_x[0:A], contour_x[N - A:N + 1]))
        yy = np.concatenate((contour_y[0:A], contour_y[N - A:N + 1]))

        coefficients = np.polyfit(xx, yy, 1)
        line = np.poly1d(coefficients)
        # plt.plot(contour_x,line(contour_x),'r-',linewidth=2.0)
        # plt.plot(xx,yy,'o',markeredgecolor="hotpink",markerfacecolor="hotpink",markersize = 10.0)

        # plt.imshow(image, origin='upper', cmap = 'gray')
        # plt.plot(contour_x,contour_y,"--",color="white",linewidth = 2.0)
        # plt.show()


        return current_contour_trimmed, line, ret
        # points = largest_contour[largest_contour[:,1].argsort()]


        # # determines the largest contour.
        # # hierarchy describes parent-child relationship
        # # this routine determines the length of each contour
        # # and returns the largest
        # drop_index = 0
        # maxLength = 0.0
        # for i in range(np.max(hierarchy+1)):
        #     length = cv2.arcLength(contours[i],0)
        #     # print(i, length)
        #     if length > maxLength:
        #         maxLength = length
        #         drop_index = i


        # # the largest contour
        # largest_contour = contours[drop_index][:,0]

        # # converts the data to (x, y) data where (0, 0) is the lower-left pixel
        # image_height = raw_experiment.image.shape[0]
        # offset = [points[0][0], image_height - points[0][1]]
        # for i in range(largest_contour.shape[0]):
        #     largest_contour[i,1] = - largest_contour[i,1]
        #     largest_contour[i,:] = largest_contour[i,:] + offset
        # points = largest_contour[largest_contour[:,1].argsort()]

        # return points, ret

    # def calculate_needle_diameter(raw_experiment, fitted_drop_data, tolerances):
