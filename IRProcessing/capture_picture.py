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

import argparse
import Image
import select
import time
import v4l2capture
import sys
import numpy as np

def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]

def main():

    # Open the video device.
    video = v4l2capture.Video_device('/dev/video0')

    # Suggest an image size to the device. The device may choose and
    # return another size if it doesn't support the suggested one.
    size_x, size_y = (160, 120)
    video.set_format(size_x, size_y, 1)

    # Create a buffer to hold image data. This must be done before calling
    # 'start' if v4l2capture is compiled with libv4l2. Otherwise raises IOError.
    video.create_buffers(1)
    '''
    if options.delay:
        # Start the device. This lights the LED if it's a camera that has one.
        video.start()

        # Wait a little. Some cameras take a few seconds to get bright enough.
        time.sleep(options.delay)

        # Send the buffer to the device.
        video.queue_all_buffers()
    else:
        # Send the buffer to the device. Some devices require this to be done
        # before calling 'start'.
        video.queue_all_buffers()

        # Start the device. This lights the LED if it's a camera that has one.
        video.start()
   '''
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
    for i in image_pairs:
      fh.write('')
      fh.write( ".".join("{:02x}".format(ord(c)) for c in i))
      fh.write('\n')
    #image = Image.frombytes("RGB", (size_x, size_y), image_data)
    #image.save(options.output_path)
    if not options.quiet:
        print "Saved file '%s' (Size: %s x %s)" % (
            options.output_path, size_x, size_y)

if __name__ == "__main__":
    main()
