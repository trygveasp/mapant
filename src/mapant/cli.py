import mapant
import argparse
import os
import sys


def parse_mapant2kml(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", dest="world_filename", type=str, required=True, help="World (pwg) file")
    parser.add_argument("-i", dest="filename", type=str, required=True, help="Input png file")
    parser.add_argument("-nx", dest="nx", type=int, required=True, help="Pixels in x direction")
    parser.add_argument("-ny", dest="ny", type=int, required=True, help="Pixels in y direction")
    parser.add_argument("-dx", dest="dx", type=int, required=False, default=None,
                        help="Size of individual tiles in x direction. Defualt is no tiling")
    parser.add_argument("-dy", dest="dy", type=int, required=False, default=None,
                        help="Size of individual tiles in y direction. Defualt is no tiling")
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
    nnx = kwargs["nx"]
    nny = kwargs["ny"]
    dx = kwargs["dx"]
    if dx is None:
        dx = nnx
    dy = kwargs["dy"]
    if dy is None:
        dy = nny
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
    p_full = mapant.MapantProjectionFromWorldfile(world_filename, nnx, nny)
    world_file_full = p_full.world_file
    mapant_imgs = []
    im_path_root = os.path.dirname(output)
    
    for x in range(0, nnx, dx):
        for y in range(0, nny, dy):
            st_x = (int(x/dx) * dx)
            st_y = (int(y/dy) * dy)
            # print(st_x, st_y)
            nx = dx
            ny = dy
            if (st_x + dx) > nnx:
                nx = nnx - st_x
            if (st_y + dy) > nny:
                ny = nny - st_y
            nx = nx
            ny = ny
            im_name = "tile_" + str(x) + "_" + str(y) + ".jpg"
            cmd = "convert " + quality + "-extract " + str(nx) + "x" + str(ny) + "+" + str(st_x) + "+" + \
                  str(st_y) + " " + filename + " " + im_path_root + "/files/" + im_name
            print(cmd)
            os.system(cmd)
            b = world_file_full.b
            d = world_file_full.d
            a = world_file_full.a
            e = world_file_full.e
            c = p_full.start_x + (st_x * world_file_full.a)
            f = p_full.start_y + (st_y * world_file_full.e)
            # print(c, f)
            # print(x, y)
            # print(p_full.dx, p_full.dy)
            # print("nx", nx, "ny", ny)
            world_file = mapant.WorldFile(a, b, c, d, e, f)
            p = mapant.MapantProjection(world_file, nx, ny)
            mapant_imgs.append(mapant.MapantImage(im_name, p))

    mapant.KMLGroundOverlay(name=name_of_data, desc=descripton_of_data).write_kml(output, mapant_imgs, mode=mode)
