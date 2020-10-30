import mapant
import argparse
import os
import sys
import shutil


def parse_mapant2kml(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", dest="world_filename", type=str, required=True, help="World (pwg) file")
    parser.add_argument("-i", dest="filename", type=str, required=True, help="Input png file")
    parser.add_argument("-nx", dest="nx", type=int, required=True, help="Pixels in x direction")
    parser.add_argument("-ny", dest="ny", type=int, required=True, help="Pixels in y direction")
    parser.add_argument("-dx", dest="dx", type=int, required=False, default=None,
                        help="Size of individual tiles in x direction. Default is no tiling")
    parser.add_argument("-dy", dest="dy", type=int, required=False, default=None,
                        help="Size of individual tiles in y direction. Default is no tiling")
    parser.add_argument("-o", dest="output", type=str, required=True,
                        help="Name of output file. Garmin expects doc.kml")
    parser.add_argument("--mode", dest="mode", default="LatLonBox", choices=["LatLonBox", "LatLonQuad"],
                        help="What kind of overlay to create in kml file", required=False)
    parser.add_argument("-q", dest="quality", type=int, required=False, default=None, help="Convert quality")
    parser.add_argument("-n", dest="name_of_data", type=str, required=False, default=None, help="Name of data")
    parser.add_argument("-d", dest="description_of_data", type=str, required=False, default=None,
                        help="Description of data")

    if len(argv) == 0:
        parser.print_help()
        print("\nExample: mapant2kml" +
              " -w /home/trygveasp/Documents/kart/mapant/mapant-export-211859-6656711-215781-6660648.pgw" +
              " -i /home/trygveasp/Documents/kart/mapant/mapant-export-211859-6656711-215781-6660648.png" +
              " -o /home/trygveasp/Documents/kart/mapant/vestre_spone_tiles/doc.kml" +
              " -nx 4016 -ny 4031 -dx 512 -dy 512")
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

            # Rotate center
            # cx, cy = rotate_coordinate(cx, cy, gox, goy, olat, -rot)
            # print("rotated center points", cx, cy)

            # North
            x_north = cx
            y_north = cy + (this_slice_sixe_y * 0.5)
            # lon, north = get_mid_box_point(x_north, y_north, gox, goy, olat, rot)
            lon, north = image.get_mid_box_point(x_north, y_north, cx, cy)
            # print(lon, north)

            # South
            x_south = cx
            y_south = cy - (this_slice_sixe_y * 0.5)
            # lon, south = get_mid_box_point(x_south, y_south, gox, goy, olat, rot)
            lon, south = image.get_mid_box_point(x_south, y_south, cx, cy)
            # print(lon, south)

            # West
            x_west = cx - (this_slice_sixe_x * 0.5)
            y_west = cy
            # print("x_west, y_west", x_west, y_west)
            # west, lat = get_mid_box_point(x_west, y_west, gox, goy, olat, rot)
            west, lat = image.get_mid_box_point(x_west, y_west, cx, cy)
            # print(west, lat)

            # East
            x_east = cx + (this_slice_sixe_x * 0.5)
            y_east = cy
            # east, lat = get_mid_box_point(x_east, y_east, gox, goy, olat, rot)
            east, lat = image.get_mid_box_point(x_east, y_east, cx, cy)
            # print(east, lat)

            im_start_x = str(ix)
            im_start_y = str(jy)
            im_end_x = str(ix + this_slice_sixe_pixels_x)
            im_end_y = str(jy + this_slice_sixe_pixels_y)

            os.makedirs(im_path_root + "/files", exist_ok=True)
            if convert:
                im_name = "tile_x_" + im_start_x + "_" + im_end_x + "_y_" + im_start_y + "_" + im_end_y + ".jpg"
                cmd = "convert " + quality + "-extract " + str(this_slice_sixe_pixels_x) + "x" + \
                      str(this_slice_sixe_pixels_y) + \
                    "+" + im_start_x + "+" + im_start_y + " " + filename + " " + im_path_root + "/files/" + im_name
                print(cmd)
                os.system(cmd)
            else:
                im_name = im_path_root + "/files/" + os.path.basename(filename)
                if not os.path.exists(im_name):
                    os.makedirs(im_path_root + "/files", exist_ok=True)
                    shutil.copy(filename, im_name)

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
            # Add tile
            tiles.append(mapant.ImageTile(im_name, **kwargs))

    mapant.KMLGroundOverlay(image, name=name_of_data, desc=descripton_of_data).write_kml(output, tiles, mode=mode)
