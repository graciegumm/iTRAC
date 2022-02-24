#!/usr/bin/env python
# coding: utf-8

# Author : Matthew Nice
# Initial Date: Feb 21, 2021
# About: trajectory analysis is for functions/methods/classes which are used to analyze the tracjectories compiled from the ITCAN algorithm.
# Read associated README for full description
# License: MIT License

#   Permission is hereby granted, free of charge, to any person obtaining
#   a copy of this software and associated documentation files
#   (the "Software"), to deal in the Software without restriction, including
#   without limitation the rights to use, copy, modify, merge, publish,
#   distribute, sublicense, and/or sell copies of the Software, and to
#   permit persons to whom the Software is furnished to do so, subject
#   to the following conditions:

#   The above copyright notice and this permission notice shall be
#   included in all copies or substantial portions of the Software.

#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
#   ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
#   TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
#   PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
#   SHALL THE AUTHORS, COPYRIGHT HOLDERS OR ARIZONA BOARD OF REGENTS
#   BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN
#   AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
#   OR OTHER DEALINGS IN THE SOFTWARE.


__author__ = 'Mathew Nice'
__email__  = 'matthew.nice@vanderbilt.edu'

## general import for data manipulation, file gathering

import numpy as np
import matplotlib.pyplot as pt
import csv
import pandas as pd
import cantools
import matplotlib.animation as animation
from matplotlib import style
from haversine import haversine, Unit
import itertools
import math
import strym as s
import networkx as nx
import os
import cv2

#creating a video in 2D
def create_plots(video_data, plot_folderhz = 20, lMax = 200, lanes=2):
    path = plot_folder.encode('unicode-escape').decode()

    data_sec = video_data
    t0= int(data_sec.head(1).t)
    tf= int(data_sec.tail(1).t)

    for second in range(t0,tf,1):
        for i in range(0,hz):
            data_t = data_sec.loc[ #find the data between the time between this frame and the next
                (data_sec.t >= second + i*(1/hz)) & #the hz is the FPS
                (data_sec.t <= second + (i+1)*(1/hz))
            ]

            fig, ax = pt.subplots()
            ax.scatter(x=data_t.x, y=data_t.y, s=10)

            for j in range(0,len(data_t)):
                cir = pt.Circle([data_t.iloc[j].x,data_t.iloc[j].y], radius = 1, fill = False, color = 'r')
                ax.add_patch(cir)

                if lanes >= 0:
                    #lane of travel
                    pt.hlines(-3.65/2,0,lMax,linestyles='dashed')
                    pt.hlines(3.65/2,0,lMax,linestyles='dashed')
                if lanes >= 1:
                    #approximate lanes to left and right
                    pt.hlines(3*(-3.65/2),0,lMax,linestyles='dashed')
                    pt.hlines(3*(3.65/2),0,lMax,linestyles='dashed')
                if lanes >= 2:
                    #approximate lanes to 2 to left and 2 to right
                    pt.hlines(5*(-3.65/2),0,lMax,linestyles='dashed')
                    pt.hlines(5*(3.65/2),0,lMax,linestyles='dashed')

                plt.xlabel('Lateral Distance (m)')
                plt.ylabel('Longitudinal Distance (m)')
                plt.ylim(-13,13)
                plt.xlim(0,lMax)
                plt.title(str(second)+' to '+str(second+1))
                plt.gca().invert_yaxis()

                plt.savefig(os.path.join(path,"time"+format(second,"03d")+format(i,"03d")+".png"),bbox_inches='tight')
                plt.show()
                plt.close()


def video_publisher(plot_folder,name):

    """Create plots from create_plots, and make those plots into a video with video_publisher."""
    image_folder = plot_folder.encode('unicode-escape').decode() #encode as raw string in case of weird pathnames
    video_name = name

    images = [img for img in os.listdir(image_folder) if img.endswith(".png")]
    images.sort()
    frame = cv2.imread(os.path.join(image_folder, images[len(images)-1]))
    height, width, layers = frame.shape
    fourcc = cv2.VideoWriter_fourcc(*'MP4V')
    video = cv2.VideoWriter(video_name,fourcc, hz,(width,height))

    for image in images:
        video.write(cv2.imread(os.path.join(image_folder, image)))

    cv2.destroyAllWindows()
    video.release()

#creating a video in 3D from Homography -- should I add here?


#common useful plots to look at

#add tracediffs stuff
