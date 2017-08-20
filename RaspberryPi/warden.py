import subprocess
import time

FAILURE_RESET = 600 # reset failures to 0 after 10 minutes
MAX_FAILURES = 5
failures = 0

if __name__ == '__main__':
    epoch = time.time()
    retry = True
    while retry:
        exit_code = subprocess.call("python camera_upload_single_thread.py",shell=True)
        if time.time() - epoch > FAILURE_RESET:
            failures = 0
            epoch = time.time()
        if exit_code != 0:
            failures += 1
        if failures > MAX_FAILURES:
            retry = False
