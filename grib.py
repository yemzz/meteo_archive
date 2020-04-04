import pygrib, os, glob
import matplotlib.pyplot as plt
import matplotlib.colors as colors
# from mpl_toolkits.basemap import Basemap
# from mpl_toolkits.basemap import shiftgrid
import numpy as np
import numpy as np
import matplotlib.pylab as plt
from osgeo import gdal
from osgeo import gdal_array
from osgeo import osr
from os import listdir
from os.path import isfile, join
import tarfile
from subprocess import call

LAT2 = 60.7
LAT1 = 45.2
LON1 = 54.7
LON2 = 78.46

cnt = 0


def create_raster(lat, lon, array, outfile):
    outfile += ".tif"
    print(np.shape(lat))
    print(np.shape(lon))
    print(np.shape(array))
    xmin, ymin, xmax, ymax = [lon.min(), lat.min(), lon.max(), lat.max()]
    nrows, ncols = np.shape(array)
    xres = (xmax - xmin) / float(ncols)
    yres = (ymax - ymin) / float(nrows)
    geotransform = (xmin, xres, 0, ymax, 0, -yres)
    # That's (top left x, w-e pixel resolution, rotation (0 if North is up),
    #         top left y, rotation (0 if North is up), n-s pixel resolution)
    # I don't know why rotation is in twice???
    output_raster = gdal.GetDriverByName('GTiff').Create(outfile, ncols, nrows, 1,
                                                         gdal.GDT_Float32)  # Open the file
    output_raster.SetGeoTransform(geotransform)  # Specify its coordinates
    srs = osr.SpatialReference()  # Establish its coordinate encoding
    srs.ImportFromEPSG(4326)  # This one specifies WGS84 lat long.
    # Anyone know how to specify the
    # IAU2000:49900 Mars encoding?
    output_raster.SetProjection(srs.ExportToWkt())  # Exports the coordinate system
    # to the file
    output_raster.GetRasterBand(1).WriteArray(array)  # Writes my array to the raster

    output_raster.FlushCache()


def process_message(grb, outfile):
    tmps = "%s" % grb
    temp = tmps.split(':')
    wtitle = temp[1]
    wtime = tmps.split(':')[len(tmps.split(':')) - 1].split(' ')[1]
    data, lat, lons = grb.data(LAT1, LAT2, LON1, LON2)
    rast_lats = []
    rast_lons = []
    rast_array = []
    for i in iter(range(len(data))):
        tdata = data[i]
        tlat = lat[i]
        tlon = lons[1]
        one_lats = []
        one_lons = []
        one_array = []
        for j in iter(range(len(tdata))):
            wdata = tdata[j]
            # print(type(wdata))
            # print(wdata)
            # return
            wlat = tlat[j]
            wlon = tlon[j]
            # cnt+=1
            # print(cnt)
            one_lats.append(wlat)
            one_lons.append(wlon)
            one_array.append(wdata)
        rast_array.append(one_array)
        rast_lons.append(one_lons)
        rast_lats.append(one_lats)
    # print(rast_lons)
    # print(rast_lats)
    # print(rast_array)
    create_raster(np.array(rast_lats), np.array(rast_lons), np.array(rast_array), outfile)


def convert_file(filename, raster_name):
    grbs = pygrib.open(filename)
    grbs.seek(0)
    for g in grbs:
        if (g.typeOfLevel == "surface"):
            print(g.typeOfLevel, g.level, g.name, g.validDate, g.analDate, g.forecastTime)
            process_message(g, raster_name)


def convert_to_raster(data_path):
    onlyfiles = [f for f in listdir(data_path) if isfile(join(data_path, f))]
    path = data_path + '/' + onlyfiles[0]
    my_tar = tarfile.open(path)
    files_path = data_path + '/' + 'grib_files'
    my_tar.extractall(files_path)
    all_files = [f for f in listdir(files_path) if isfile(join(files_path, f))]
    date = data_path.split('/')[-1]
    new_path = "./raster_images/" + date
    if not os.path.exists(new_path):
        os.makedirs(new_path)
    for grib_file in all_files:
        parts = grib_file.split('.')
        outfile_name = './raster_images/' + date + "/" + parts[2] + '-' + parts[3]
        file = files_path + '/' + grib_file
        # print("FILE ", file)
        # print("OUT ", outfile_name)
        convert_file(file, outfile_name)

def main():
    convert_to_raster('./archive_files/TMP/2019-06')
    # convert_file(
    #     './archive_files/TMP/2016-01/gfs.0p25.2016010100.f000-2016013100.f018.grib2.spasub.asmatullayev415102/gfs.0p25.2016010100.f018.grib2.spasub.asmatullayev415102')


if __name__ == '__main__':
    main()
