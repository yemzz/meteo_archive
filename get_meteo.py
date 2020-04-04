import subprocess
import time
import re
import grib
import json 



def get_meteo(start_date, end_date, directory, param, levels):
    """Downloads GFS meteo data

    Parameters
    ----------
    start_date : str
        Download meteo data starting from this date. Format is '20190101'.
    end_date : str
        Download meteo data until this date. Format is '20190101'.
    directory : str
        Download meteo data to this path.
    param : str
        Which meteo data's parameter to include. Only ONE parameter!
    levels : dict
        Which levels and their values for the ONLY param to download.
        See meteo_archive_info.json for correct dictionary format.

    Returns
    -------
    str
        path to the downloaded file
    """
    print("start_date; {}".format(start_date))
    print("end_date; {}".format(end_date))
    print("directory; {}".format(directory))
    print("param; {}".format(param))
    print("levels {}".format(levels))
    # levels = {
    #     "SFC": {
    #         "descr": "Ground or water surface",
    #         "values": [
    #             "0"
    #         ]
    #     }
    # }

    formatted_levels = ""

    # Constructing a subset request
    with open('ds084.1_control_file', 'w') as control_file:
        print("dataset=ds084.1", file=control_file)
        print("date={}0000/to/{}0000".format(start_date, end_date), file=control_file)
        print("datetype=init", file=control_file)
        print("param={}".format(param), file=control_file)

        for level in levels.keys():
            formatted_levels += level + ":"
            formatted_levels += '/'.join(levels[level]["values"])
            formatted_levels += ";"

        print("level={}".format(formatted_levels), file=control_file)
        print("#oformat=netCDF", file=control_file)
        print("nlat=60.7", file=control_file)
        print("slat=45.2", file=control_file)
        print("wlon=54.7", file=control_file)
        print("elon=78.46", file=control_file)
        print("product=6-hour Forecast/3-hour Forecast/18-hour Forecast/Analysis", file=control_file)
        print("targetdir=/glade/scratch", file=control_file)

    output1 = subprocess.Popen(['python3', 'rdams-client.py', '-submit', 'ds084.1_control_file'],
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output1.wait()
    stdout1, stderr1 = output1.communicate()
    if stderr1:
        raise ValueError(stderr1)
    stdout1 = stdout1.decode("utf-8")

    # print(stdout1)
    start_indx = stdout1.find("Request Index") + 14
    rqst_indx = stdout1[start_indx:start_indx + 6]

    if re.match('^[0-9]{6}$', rqst_indx) is None:
        # raise ValueError(stdout1)
        raise ValueError('Request Index must be entirely numeric. But it is: {}'.format(rqst_indx))

    file_ready = False

    while not file_ready:
        time.sleep(30)
        output = subprocess.Popen(['python3', 'rdams-client.py', '-get_status', rqst_indx], stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT)
        output.wait()
        stdout, stderr = output.communicate()
        if stderr:
            raise ValueError(stderr)
        stdout = stdout.decode('utf-8')

        if "Q - building" in stdout:
            print("Building data... for the request {}".format(rqst_indx))
        elif "Q -  queued" in stdout:
            print("Request in queue... for the request {}".format(rqst_indx))
        elif "O - Online" in stdout:
            file_ready = True
            print("Downloading data... for the request {}".format(rqst_indx))
        elif "E - Error" in stdout:
            raise ValueError(
                "The data server could not prepare the requested meteo data. The -get_status output: \n".format(stdout))
            # raise ValueError(stdout)
        output.stdout.close()

    output1 = subprocess.Popen(['python3', 'rdams-client.py', '-download', rqst_indx, directory],
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output1.wait()
    stdout1, stderr1 = output1.communicate()
    if stderr1:
        raise ValueError(stderr1)
    stdout1 = stdout1.decode('utf-8')

    # print("STDOUT1 : %s", stdout1)

    path_indx = stdout1.find("Request to ") + 12
    path_end_indx = stdout1.find(" directory.")
    data_path = stdout1[path_indx:path_end_indx-1]

    print("DATA_PATH: %s", data_path)

    print("Successfully downloaded meteo data into this directory: {}".format(data_path))
    print("Time period is from {} to {} with these parameter {} for these levels: {}:\n".format(start_date, end_date,
                                                                                                param, levels))
    if param == "TMP":
        grib.convert_to_raster(data_path)
