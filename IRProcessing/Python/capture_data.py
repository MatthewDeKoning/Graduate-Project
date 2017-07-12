#!/usr/bin/python
#
# python-v4l2capture
#
# This file is an example on how to capture a picture with
# python-v4l2capture.
#
# 2009, 2010, 2015, 2016 Fredrik Portstrom <https://portstrom.com>
#
# I, the copyright holder of this file, hereby release it into the
# public domain. This applies worldwide. In case this is not legally
# possible: I grant anyone the right to use this work for any
# purpose, without any conditions, unless such conditions are
# required by law.

import select
import time
import v4l2capture
import sys
import os

def to_num(image_pairs):
    ret = []
    i = 19200
    for j in range(0, i, 2):
        ret[j] = ord(image_pairs[j*2+1])<<8 + ord(image_pairs[j*2])
    return ret

def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]

def get_data(device):
    # Open the video device.
    video = v4l2capture.Video_device(device)
    
    os.system("v4l2-ctl --set-fmt-video=width=160,height=120,pixelformat=1")
    # Create a buffer to hold image data. This must be done before calling
    # 'start' if v4l2capture is compiled with libv4l2. Otherwise raises IOError.
    video.create_buffers(1)
    # Send the buffer to the device. Some devices require this to be done
    # before calling 'start'.
    video.queue_all_buffers()

    # Start the device. This lights the LED if it's a camera that has one.
    video.start()
    # Wait for the device to fill the buffer.
    select.select((video,), (), ())

    # The rest is easy :-)
    image_data = video.read()
    video.close()
    image_pairs = chunks(image_data, 2)
    image_values = []
    for i in image_pairs:
      sum = 0
      num = 0
      for c in i:
         sum += ord(c)*2**(8*num)
         num += 1
      image_values.append(sum)
      
    return image_values

if __name__ == "__main__":
    get_data('/dev/video0')
