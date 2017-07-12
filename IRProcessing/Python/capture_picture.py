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
import v4l2
import fcntl
import os


def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]

def main():

    # Open the video device.
    video = v4l2capture.Video_device('/dev/video0')
    #fmt = v4l2.v4l2_format()
    #fmt.type = v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE
    #fcntl.ioctl(video, v4l2.VIDIOC_G_FMT, fmt)
    #print("width:", fmt.fmt.pix.width)
    #print("height", fmt.fmt.pix.height)
    #print hex(fmt.fmt.pix.pixelformat)

    # Suggest an image size to the device. The device may choose and
    # return another size if it doesn't support the suggested one.
    size_x, size_y = (160, 120)
    #video.set_format(size_x, size_y, 1)
    #fcntl.ioctl(video, v4l2.VIDIOC_G_FMT, fmt)
    #print("width:", fmt.fmt.pix.width)
    #print("height", fmt.fmt.pix.height)
    #print hex(fmt.fmt.pix.pixelformat)

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
    fh = open('OUTPUT.txt', 'w')
    image_pairs = chunks(image_data, 2)
    #image_nums = to_num(image_pairs)
    #print image_nums
    count = 0
    image_values = []
    for i in image_pairs:
      fh.write('')
      fh.write( ".".join("{:02x}".format(ord(c)) for c in i))
      fh.write('\n')
      values = []
      sum = 0
      num = 0
      for c in i:
         values.append("{:02x}".format(ord(c)))
         sum += ord(c)*2**(8*num)
         num += 1
      print sum
      count += 1
    print count
    #image = Image.frombytes("RGB", (size_x, size_y), image_data)
    #image.save(options.output_path)
    print "Saved file '%s' (Size: %s x %s)" % (
            'OUTPUT.txt', size_x, size_y)

if __name__ == "__main__":
    main()
