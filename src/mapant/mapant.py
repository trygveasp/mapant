import pyproj
import math


class WorldFile(object):
    def __init__(self, a, b, c, d, e, f):
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.e = e
        self.f = f


class WorldFileFromFile(WorldFile):
    def __init__(self, fname):
        fh = open(fname)
        a = None
        b = None
        c = None
        d = None
        e = None
        f = None
        for line in range(1, 7):
            line_text = fh.readline().rstrip()
            print(line_text)
            factor = float(line_text)
            if line == 1:
                a = factor
            elif line == 3:
                b = factor
            elif line == 5:
                c = factor
            elif line == 2:
                d = factor
            elif line == 4:
                e = factor
            elif line == 6:
                f = factor
            else:
                raise Exception
        fh.close()
        WorldFile.__init__(self, a, b, c, d, e, f)


class MapantProjection(object):
    def __init__(self, world_file, nx, ny, zone="33N"):
        self.world_file = world_file
        self.zone = zone
        proj_string = "+proj=utm +zone=" + zone + " +ellps=WGS84 +datum=WGS84 +units=m +no_defs"
        self.projection = pyproj.Proj(proj_string)
        self.nx = nx
        self.ny = ny
        self.rotation_x = self.world_file.b
        self.rotation_y = self.world_file.d
        self.start_x = self.world_file.c
        self.start_y = self.world_file.f
        self.dx = self.world_file.a
        self.dy = self.world_file.e

        print("Constructed MapantProjection ", self.start_x, self.start_y)

    # Set UTM ccordinated in grid
    def transform(self, proj_string, xx, yy):
        out_projection = pyproj.Proj(proj_string)
        print(xx)
        print(yy)
        positions = pyproj.transform(self.projection, out_projection, xx, yy)
        print(positions)
        return positions

    def transform_grid(self, proj_string):
        xx = []
        yy = []
        for y in range(0, self.ny):
            for x in range(0, self.nx):
                xx.append(self.start_x + (float(x) * self.dx))
                yy.append(self.start_y + (float(y) * self.dy))

        positions = self.transform(proj_string, xx, yy)
        return positions

    def transform_to_kml_latlonquad_corners(self):
        xx = []
        yy = []

        if self.rotation_x != 0 or self.rotation_y != 0:
            raise NotImplementedError

        extra_x = float(self.dx) / 2.
        extra_y = float(self.dy) / 2.

        # Start in lower left, propagate counter-clockwise
        # LL
        xx.append(self.start_x - extra_x)
        yy.append(self.start_y - extra_y + ((self.ny + 1) * self.dy))
        # LR
        xx.append(self.start_x - extra_x + ((self.nx + 1) * self.dx))
        yy.append(self.start_y - extra_y + ((self.ny + 1) * self.dy))
        # UR
        xx.append(self.start_x - extra_x + ((self.nx + 1) * self.dx))
        yy.append(self.start_y - extra_y)
        # UL
        xx.append(self.start_x - extra_x)
        yy.append(self.start_y - extra_y)

        pos = self.transform("EPSG:4326", xx, yy)

        print(pos, len(pos))
        string = ""
        for p in range(0, len(pos[0])):
            string = string + " " + str(pos[1][p]) + "," + str(pos[0][p])
        print(string)
        return string

    def transform_to_kml_latlonbox(self):

        xx = []
        yy = []

        if self.rotation_x != 0 or self.rotation_y != 0:
            raise NotImplementedError

        extra_x = float(self.dx) * 0.5
        extra_y = float(self.dy) * 0.5
        # extra_x = -1
        # extra_y = -1
        nx = float(self.nx) * 0.5
        ny = float(self.ny) * 0.5

        center_x = self.start_x + (nx * self.dx)
        center_y = self.start_y + (ny * self.dy)

        x_west = self.start_x - extra_x
        x_east = self.start_x - extra_x + ((self.nx + 1) * self.dx)
        y_north = self.start_y - extra_y
        y_south = self.start_y - extra_y + ((self.ny + 1) * self.dy)

        # North
        xx.append(center_x)
        yy.append(y_north)

        # South
        xx.append(center_x)
        yy.append(y_south)

        # West
        xx.append(x_west)
        yy.append(center_y)

        # East
        xx.append(x_east)
        yy.append(center_y)

        # Center
        xx.append(center_x)
        yy.append(center_y)

        pos = self.transform("EPSG:4326", xx, yy)
        north = pos[0][0]
        south = pos[0][1]
        west = pos[1][2]
        east = pos[1][3]
        center_lon = pos[1][4]
        center_lat = pos[0][4]

        # atan(($nw_lng - $sw_lng) / ($sw_lat - $nw_lat) / 2)

        pos = self.transform("EPSG:4326", [x_west, x_west], [y_north, y_south])
        nw_lng = float(pos[1][0])
        nw_lat = float(pos[0][0])
        sw_lng = float(pos[1][1])
        sw_lat = float(pos[0][1])
        rotation = math.degrees(math.atan((nw_lng - sw_lng) / (sw_lat - nw_lat) / 2))
        # rotation = 0

        print("nx, ny", nx, ny, self.nx, self.ny)
        print("center", center_lon, center_lat, center_x, center_y)
        print("north, south, west, east, rotation: ", north, south, west, east, rotation)
        return north, south, west, east, rotation


class MapantProjectionFromWorldfile(MapantProjection):
    def __init__(self, fname, nx, ny):
        wf = WorldFileFromFile(fname)
        MapantProjection.__init__(self, wf, nx, ny)


class MapantImage(object):
    def __init__(self, image, mapant_proj):
        self.name = image
        self.proj = mapant_proj
        self.description = ""


class KMLGroundOverlay(object):
    def __init__(self):
        self.name1 = "Test1"
        self.name2 = "Test2"
        self.description1 = "Test description1"
        self.description2 = "Test description2"

    def write_kml(self, fname, mapant_images, mode="LatLonBox"):

        fh = open(fname, "w")
        fh.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        if mode == "LatLonQuad":
            fh.write('<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2">\n')
        else:
            fh.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
        fh.write('  <Folder>\n')
        fh.write('    <name>' + self.name1 + '</name>\n')
        fh.write('    <description>' + self.description1 + '</description>\n')

        for mapant_image in mapant_images:
            print(mapant_image.name)

            print(mapant_image.proj.world_file.c, mapant_image.proj.world_file.f)
            fh.write('    <GroundOverlay>\n')
            fh.write('      <name>' + mapant_image.name + '</name>\n')
            fh.write('      <description>' + mapant_image.description + '</description>\n')
            fh.write('      <drawOrder>50</drawOrder>\n')
            fh.write('      <Icon>\n')
            fh.write('         <href>files/' + mapant_image.name + '</href>\n')
            # fh.write('         <viewBoundScale>1</viewBoundScale>\n')
            fh.write('      </Icon>\n')
            fh.write('      <altitudeMode>clampToGround</altitudeMode>\n')
            if mode == "LatLonQuad":
                corner_string = mapant_image.proj.transform_to_kml_latlonquad_corners()
                print("String:", corner_string)
                fh.write('      <gx:LatLonQuad>\n')
                fh.write('        <coordinates>' + corner_string + '</coordinates>\n')
                fh.write('      </gx:LatLonQuad>\n')
            elif mode == "LatLonBox":
                north, south, west, east, rotation = mapant_image.proj.transform_to_kml_latlonbox()
                fh.write('      <LatLonBox>\n')
                fh.write('        <north>' + str(north) + '</north>\n')
                fh.write('        <south>' + str(south) + '</south>\n')
                fh.write('        <west>' + str(west) + '</west>\n')
                fh.write('        <east>' + str(east) + '</east>\n')
                fh.write('        <rotation>' + str(rotation) + '</rotation>\n')
                fh.write('      </LatLonBox>\n')
            else:
                raise NotImplementedError
            fh.write('    </GroundOverlay>\n')
        fh.write('  </Folder>\n')
        fh.write('</kml>\n')
        fh.close()
