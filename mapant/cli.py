import mapant
import argparse
import os
import sys
import shutil
try:
    import zipfile
except ImportError:
    zipfile = None


def parse_mapant2kml(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", dest="world_filename", type=str, required=True, help="World (pwg) file")
    parser.add_argument("-i", dest="filename", type=str, required=True, help="Input png file")
    parser.add_argument("-a", dest="no_abort_on_filesize" , action="store_true",
                        help="No abort on exceeding garmin file size limit")
    parser.add_argument("-nx", dest="nx", type=int, required=True, help="Pixels in x direction")
    parser.add_argument("-ny", dest="ny", type=int, required=True, help="Pixels in y direction")
    parser.add_argument("-dx", dest="dx", type=int, required=False, default=None,
                        help="Size of individual tiles in x direction. Default is no tiling")
    parser.add_argument("-dy", dest="dy", type=int, required=False, default=None,
                        help="Size of individual tiles in y direction. Default is no tiling")
    parser.add_argument("-o", dest="output", type=str, required=True,
                        help="Name of output file. Garmin expects doc.kml. If name has kmz extension a zipped kmz " +
                             "file with proper content will be generated")
    parser.add_argument("--mode", dest="mode", default="LatLonBox", choices=["LatLonBox", "LatLonQuad"],
                        help="What kind of overlay to create in kml file. Garmin only supports LatLonBox",
                        required=False)
    parser.add_argument("-q", dest="quality", type=int, required=False, default=None, help="Convert quality")
    parser.add_argument("-n", dest="name_of_data", type=str, required=False, default=None, help="Name of data")
    parser.add_argument("-d", dest="description_of_data", type=str, required=False, default=None,
                        help="Description of data")
    parser.add_argument('--version', action='version', version=mapant.__version__)

    if len(argv) == 0:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args(argv)
    kwargs = {}
    for arg in vars(args):
        kwargs.update({arg: getattr(args, arg)})
    return kwargs


def mapant2kml(**kwargs):

    world_filename = kwargs["world_filename"]
    filename = kwargs["filename"]
    npixelx = kwargs["nx"]
    npixely = kwargs["ny"]
    slice_size_x = kwargs["dx"]
    if slice_size_x is None:
        slice_size_x = npixelx
    slice_size_y = kwargs["dy"]
    if slice_size_y is None:
        slice_size_y = npixely
    output = kwargs["output"]
    name_of_data = kwargs["name_of_data"]
    descripton_of_data = kwargs["description_of_data"]
    quality = None
    if "quality" in kwargs:
        quality = kwargs["quality"]
    if quality is None:
        quality = ""
    else:
        quality = " -quality " + str(quality) + " "
    mode = kwargs["mode"]
    no_abort_on_filesize = False
    if "no_abort_on_filesize" in kwargs:
        no_abort_on_filesize = kwargs["no_abort_on_filesize"]
    proj = mapant.MapantProjectionFromWorldfile(world_filename)
    image = mapant.MapantImage(filename, proj, npixelx, npixely)
    im_path_root = os.path.dirname(output)

    # Check if we must convert
    if int(npixelx) <= int(slice_size_x) and int(npixely) <= int(slice_size_y):
        convert = False
        if not filename.endswith(".jpg"):
            convert = True
    else:
        convert = True

    tiles = []
    kml_file = output
    zip_file = False
    if output.endswith(".kmz"):
        kml_file = "doc.kml"
        zip_file = True

    files = [kml_file]
    for ix in range(0, npixelx, slice_size_x):
        for jy in range(0, npixely, slice_size_y):
            ix_counter = (ix / slice_size_x) + 1
            jy_counter = (jy / slice_size_y) + 1
            this_slice_sixe_pixels_x = slice_size_x
            if ix_counter * slice_size_x > npixelx:
                this_slice_sixe_pixels_x = npixelx - int((ix_counter - 1) * slice_size_x)
            this_slice_sixe_x = this_slice_sixe_pixels_x * proj.dx
            this_slice_sixe_pixels_y = slice_size_y
            if jy_counter * slice_size_y > npixely:
                this_slice_sixe_pixels_y = npixely - int((jy_counter - 1) * slice_size_y)
            this_slice_sixe_y = this_slice_sixe_pixels_y * abs(proj.dy)

            # print("x", ix_counter, npixelx, slice_size_x, this_slice_sixe_pixels_x)
            # print("y", jy_counter, npixely, slice_size_y, this_slice_sixe_pixels_y)
            # print(ix, jy, this_slice_sixe_x, this_slice_sixe_y)

            previous_offset_x = (ix_counter - 1) * slice_size_x * proj.dx
            previous_offset_y = (jy_counter - 1) * slice_size_y * abs(proj.dy)

            # print(previous_offset_x, previous_offset_y)
            cx = proj.start_x + previous_offset_x + (this_slice_sixe_x * 0.5)
            cy = proj.start_y - previous_offset_y - (this_slice_sixe_y * 0.5)
            # print("center points", cx, cy)

            # Corner points
            ll_lon, ll_lat, lr_lon, lr_lat, ur_lon, ur_lat, ul_lon, ul_lat = \
                image.get_corners(cx, cy, this_slice_sixe_x, this_slice_sixe_y)

            # North
            x_north = cx
            y_north = cy + (this_slice_sixe_y * 0.5)
            lon, north = image.get_mid_box_point(x_north, y_north, cx, cy)
            # print(lon, north)

            # South
            x_south = cx
            y_south = cy - (this_slice_sixe_y * 0.5)
            lon, south = image.get_mid_box_point(x_south, y_south, cx, cy)
            # print(lon, south)

            # West
            x_west = cx - (this_slice_sixe_x * 0.5)
            y_west = cy
            west, lat = image.get_mid_box_point(x_west, y_west, cx, cy)
            # print(west, lat)

            # East
            x_east = cx + (this_slice_sixe_x * 0.5)
            y_east = cy
            east, lat = image.get_mid_box_point(x_east, y_east, cx, cy)
            # print(east, lat)

            im_start_x = str(ix)
            im_start_y = str(jy)
            im_end_x = str(ix + this_slice_sixe_pixels_x)
            im_end_y = str(jy + this_slice_sixe_pixels_y)

            os.makedirs(im_path_root + "/files", exist_ok=True)
            if convert:
                im_name = im_path_root + "/files/tile_x_" + im_start_x + "_" + im_end_x + "_y_" + im_start_y + \
                          "_" + im_end_y + ".jpg"
                cmd = "convert " + quality + "-extract " + str(this_slice_sixe_pixels_x) + "x" + \
                      str(this_slice_sixe_pixels_y) + \
                    "+" + im_start_x + "+" + im_start_y + " " + filename + " " + im_name
                print(cmd)
                os.system(cmd)
            else:
                im_name = im_path_root + "/files/" + os.path.basename(filename)
                if not os.path.exists(im_name):
                    os.makedirs(im_path_root + "/files", exist_ok=True)
                    shutil.copy(filename, im_name)

            file_size_limit = 3072000
            if os.path.exists(im_name):
                file_size = os.path.getsize(im_name)
                print("percent of max size: " + str(int(100. * file_size / file_size_limit)) + "/100")
                if file_size > file_size_limit:
                    if no_abort_on_filesize:
                        print("Warning file size " + str(file_size) + " is larger than " + str(file_size_limit))
                    else:
                        raise Exception("Warning file size " + str(file_size) + " is larger than " +
                                        str(file_size_limit))
            else:
                raise FileNotFoundError(im_name)

            kwargs = {
                "name": "tile_x_" + str(ix) + "-" + im_end_x + "_y_" + str(jy) + "-" + im_end_y,
                "description": "Image size " + str(this_slice_sixe_pixels_x) + "x" + str(this_slice_sixe_pixels_y),
                "north": north,
                "south": south,
                "west": west,
                "east": east,
                "rotation": image.rotation,
                "ll_lon": ll_lon,
                "ll_lat": ll_lat,
                "lr_lon": lr_lon,
                "lr_lat": lr_lat,
                "ur_lon": ur_lon,
                "ur_lat": ur_lat,
                "ul_lon": ul_lon,
                "ul_lat": ul_lat
            }

            files.append(im_name)
            # Add tile
            tiles.append(mapant.ImageTile("tile_x_" + im_start_x + "_" + im_end_x + "_y_" + im_start_y + "_" +
                                          im_end_y + ".jpg", **kwargs))

    mapant.KMLGroundOverlay(image, name=name_of_data, desc=descripton_of_data).write_kml(kml_file, tiles, mode=mode)

    # Zip if we want kmz file
    if zip_file:
        if zip is None:
            raise Exception("zipfile module was not properly loaded and is needed to create kmz files")
        zipfh = zipfile.ZipFile(output, 'w')
        for file in files:
            print("Add file", file)
            zipfh.write(file)
        zipfh.close()

    print("Output " + output + " refers to " + str(len(tiles)) + " images")
