import Definitions
import unittest
import os
import sys
import shutil

# TODO: onerror function for rmtree.
#  def take_ownership()


test_directory = Definitions.TEST_OUT_DIR
# TODO: check if directory exists
if os.path.isdir(test_directory):
    # TODO: exists: delete contents
    with os.scandir(test_directory) as entries:
        for entry in entries:
            if os.path.isdir(entry):
                try:
                    shutil.rmtree(entry)
                except OSError:
                    # TODO change permisions of directory
                    for root, dirs, files in os.walk(entry):
                        for d in dirs:
                            os.chmod(os.path.join(root, d), 0o777)
                        for f in files:
                            os.chmod(os.path.join(root, f), 0o777)
                    # Try again
                    shutil.rmtree(entry)
            try:
                os.remove(entry)
            except:
            # TODO: handle exception regarding a file being used.
else:
    # TODO: Doesnt exists: create contents
    os.mkdir(test_directory, 0o777)



loader = unittest.defaultTestLoader
suite = loader.discover(Definitions.ROOT_DIR)
print(suite.__dict__)
runner = unittest.TextTestRunner(failfast=True)
runner.run(suite)
