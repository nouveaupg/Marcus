import time
import io
import json
import logging
import threading
import requests
import uuid
import os
from picamera import PiCamera

LOG_FORMAT = '%(asctime)-15s %(levelname)s %(message)s'

class UploadWorkerThread(threading.Thread):
    def __init__(self,upload_bytes,logger):
        threading.Thread.__init__(self)
        self.logger = logger
        # load config dict
        self.config = json.load(file("remote-config.json","r"))
        self.uploadUrl = self.config['remote-host'] + "/upload/"
        # stream to upload
        self.uploadStream = io.BytesIO()
        self.uploadStream.write(upload_bytes)
        self.uploadStream.seek(0)
    def run(self):
        start_time = time.time()
        output_data = {"camera_uuid":self.config['uuid']}
        upload_files = [
        ('jpeg_upload', ('jpeg_upload',self.uploadStream,"image/jpeg"))]

        r = requests.post(self.uploadUrl,files=upload_files,data=output_data)
        elapsed = time.time() - start_time
        self.logger.info("Uploaded image to server in %0.2f seconds. (tid %d)" % (elapsed,self.ident))

class CameraMonitor(threading.Thread):
    def __init__(self,timeout=None):
        threading.Thread.__init__(self)
        self.timeout = timeout
        #logging
        FORMAT = '%(asctime)-15s %(message)s'
        self.logger = logging.getLogger(__name__ + ".CameraMonitor")
        fh = logging.FileHandler("CameraMonitor.log")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(logging.Formatter(LOG_FORMAT))
        sh = logging.StreamHandler()
        sh.setLevel(logging.INFO)
        self.logger.addHandler(fh)
        self.logger.addHandler(sh)
        self.logger.setLevel(logging.DEBUG)
        # load config dict
        self.config = json.load(file("remote-config.json","r"))
        self.uploadUrl = self.config['remote-host'] + "/upload/"
    def run(self):
        camera = PiCamera()
        camera.resolution = (640, 480)

        self.logger.info("Activating camera module with resolution (%d,%d)" % camera.resolution)

        # Start a preview and let the camera warm up for 2 seconds
        camera.start_preview()
        time.sleep(2)

        # Note the start time and construct a stream to hold image data
        # temporarily (we could write it directly to connection but in this
        # case we want to find out the size of each capture first to keep
        # our protocol simple)
        start = time.time()
        self.logger.info("Camera ready - beginning capture...")
        stream = io.BytesIO()
        frames = 0
        for foo in camera.capture_continuous(stream, 'jpeg'):
            # Write the length of the capture to the stream and flush to
            # ensure it actually gets sent
            # self.logger.debug("Uploading image...")
            stream.seek(0)
            # copy last image to local cache
            self.last_image = io.BytesIO()
            upload_bytes = stream.read()
            stream.seek(0)
            self.last_image.write(upload_bytes)
            self.last_image.seek(0)
            # upload to AWS
            self.logger.info("Uploading image...")
            start_time = time.time()
            output_data = {"camera_uuid":self.config['uuid']}
            upload_files = {'jpeg_upload':('jpeg_upload',last_image,"image/jpeg")}
            r = requests.post(self.uploadUrl,files=upload_files,data=output_data)
            elapsed = time.time() - start_time
            self.logger.info("Uploaded image to server in %0.2f seconds. (tid %d)" % (elapsed,self.ident))
            #newWorker.start()
            frames += 1
            if frames > 5:
                import sys;sys.exit(0)
            if time.time() - start > 5:
                fps = float(frames) / 30.0
                self.logger.info("Avg framerate: %0.2f fps" % fps)
                if self.timeout and time.time() - start > self.timeout:
                    break

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
    print "Starting camera thread with 30 second timeout..."
    monitor = CameraMonitor(30)
    monitor.start()
