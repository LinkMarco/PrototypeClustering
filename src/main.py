from time import time
import inspect
import os
import traceback

from input.config_reader import ConfigReader

"""
Marco Link
"""

def main():
    """
    Processes one config file and its resulting clustering process after another.
    """

    # get the actual path of the prototyp
    # http://stackoverflow.com/questions/50499/how-do-i-get-the-path-and-name-of-the-file-that-is-currently-executing#
    path = os.path.dirname(os.path.realpath(inspect.getfile(inspect.currentframe())))  # script directory

    # looking for the configSpecification, the config folder and the output path
    path = os.path.split(path)[0]
    path_spec = os.path.join(path, 'configSpecification')
    path_configs = os.path.join(path, 'config')
    path_out = os.path.join(path, 'out')

    # iterate over all configuration file in the config folder and execute it
    # http://stackoverflow.com/questions/3964681/find-all-files-in-directory-with-extension-txt-in-python
    for config in os.listdir(path_configs):
        if config.endswith('.conf'):
            # http://stackoverflow.com/questions/678236/how-to-get-the-filename-without-the-extension-from-a-path-in-python
            clustering_process_path_out = os.path.join(path_out, os.path.splitext(config)[0])
            clustering_process = None
            try:
                # create clustering process on the basis of the config file
                clustering_process = ConfigReader(clustering_process_path_out).read_config(
                    os.path.join(path_configs, config), path_spec)
            except Exception as exception:
                # http://stackoverflow.com/questions/3702675/how-to-print-the-full-traceback-without-halting-the-program
                traceback.print_tb(exception.__traceback__)
            try:
                if clustering_process is not None:
                    t0 = time()
                    print("Start clustering process: " + str(config))
                    # start the clustering process
                    clustering_process.start()
                    print("Finished clustering process in %fs" % (time() - t0))
                    print('_________________________________________')
            except Exception as exception:
                # http://stackoverflow.com/questions/3702675/how-to-print-the-full-traceback-without-halting-the-program
                traceback.print_tb(exception.__traceback__)
                print("Failed clustering process: " + str(config))
                print('_________________________________________')

# https://docs.python.org/2/library/__main__.html
if __name__ == "__main__":
    main()
