import time
import io
import json
import logging
import threading
import requests
import uuid
import os
from fractions import Fraction
from exceptions import Exception
from picamera import PiCamera

LOG_FORMAT = '%(asctime)-15s %(levelname)s %(message)s'

if __name__ == '__main__':
    try:
        f = file("remote-config.json","r")
        config_data = json.load(f)
        if 'uuid' not in config_data:
            config_data['uuid'] = str(uuid.uuid4())
            f.close()
            f = file("remote-config.json","w+")
            f.seek()
            json.dump(config_data,f)
            f.close()
    except IOError:
        # couldn't open file
        print "Couldn't open remote-config.json make sure it exits..."
        os.exit(3)
    print "Starting camera thread with 30 second timeout..."
    FORMAT = '%(asctime)-15s %(message)s'
    logger = logging.getLogger(__name__ + ".CameraMonitor")
    fh = logging.FileHandler("CameraMonitor.log")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(LOG_FORMAT))
    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter(LOG_FORMAT))
    sh.setLevel(logging.INFO)
    logger.addHandler(fh)
    logger.addHandler(sh)
    logger.setLevel(logging.DEBUG)
    # load config dict
    config = json.load(file("remote-config.json","r"))
    uploadUrl = config['remote-host'] + "/upload/"
    # starting the camera
    camera = PiCamera(resolution=(640,480),framerate=Fraction(1,10),sensor_mode=3)
    camera.iso = 100
    logger.info("Activating camera module with resolution (%d,%d)" % camera.resolution)
    time.sleep(2)
    logger.info("Camera ready - beginning capture...")
    stream = io.BytesIO()
    frames = 0

    while 1:
        try:
            camera.capture(stream,"jpeg")
            logger.info("Captured image, uploading to %s..." % config['remote-host'])
            output_data = {"camera_uuid":config['uuid']}
            output_files = {"jpeg_upload":('jpeg_upload',stream,"image/jpeg")}
            stream.seek(0)
            r = requests.post(uploadUrl,files=output_files,data=output_data)
            request_data = r.json()
            if "success" in request_data and request_data['success'] == False:
                logger.error("Failed to upload image: %s" % )
                os.exit(2)
                break
            stream.seek(0)
            stream.truncate()
            frames += 1
            if frames < 5:
                os.exit(0)
                break
        except Exception as e:
            print str(e)
            os.exit(1)
            break
