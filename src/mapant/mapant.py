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
            # print(line_text)
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
    def __init__(self, world_file, rotation=None):
        self.world_file = world_file
        proj_string = "+proj=utm +zone=33N +ellps=WGS84 +datum=WGS84 +units=m +no_defs"
        self.projection = pyproj.Proj(proj_string)
        self.rotation_x = self.world_file.b
        self.rotation_y = self.world_file.d
        self.start_x = self.world_file.c
        self.start_y = self.world_file.f
        self.dx = self.world_file.a
        self.dy = self.world_file.e
        self.rotation = rotation
        # print("Constructed MapantProjection ", self.start_x, self.start_y)

    # Transform UTM projection to target projection
    def transform(self, proj_string, xx, yy):
        out_projection = pyproj.Proj(proj_string)
        positions = pyproj.transform(self.projection, out_projection, xx, yy)
        return positions


class MapantProjectionFromWorldfile(MapantProjection):
    def __init__(self, fname):
        wf = WorldFileFromFile(fname)
        MapantProjection.__init__(self, wf)


class MapantImage(object):
    def __init__(self, image, mapant_proj, nx, ny):
        self.name = image
        self.proj = mapant_proj
        self.description = ""
        self.nx = nx
        self.ny = ny

        self.gox = self.proj.start_x + self.proj.dx * 0.5
        self.goy = self.proj.start_y - abs(self.proj.dy) * 0.5

        # print("ox", self.gox)
        # print("oy", self.goy)
        self.olat, self.olon = self.proj.transform("EPSG:4326", self.gox, self.goy)
        # print(self.olon, self.olat)

        north_x = self.gox
        north_y = self.goy + abs(self.proj.dy) * 0.5
        self.north_lat, self.north_lon = self.proj.transform("EPSG:4326", north_x, north_y)
        # print(self.north_lon, self.north_lat)
        self.rotation = math.degrees(math.atan((self.olon - self.north_lon) / (self.north_lat - self.olat) / 2))

        self.ll_lon, self.ll_lat, self.lr_lon, self.lr_lat, self.ur_lon, self.ur_lat, self.ul_lon, self.ul_lat = \
            self.get_corners(self.gox, self.goy, self.proj.dx, abs(self.proj.dy))

    def get_corners(self, gox, goy, dx, dy):
        xx = []
        yy = []

        # Start in lower left, propagate counter-clockwise
        # LL
        xx.append(gox - (dx * 0.5))
        yy.append(goy - (dy * 0.5))
        # LR
        xx.append(gox + (dx * 0.5))
        yy.append(goy - (dy * 0.5))
        # UR
        xx.append(gox + (dx * 0.5))
        yy.append(goy + (dy * 0.5))
        # UL
        xx.append(gox - (dx * 0.5))
        yy.append(goy + (dy * 0.5))

        pos = self.proj.transform("EPSG:4326", xx, yy)
        return pos[1][0], pos[0][0], pos[1][1], pos[0][1], pos[1][2], pos[0][2], pos[1][3], pos[0][3],

    def transform_grid(self, proj_string):
        xx = []
        yy = []
        for y in range(0, self.ny):
            for x in range(0, self.nx):
                xx.append(self.proj.start_x + (float(x) * self.proj.dx))
                yy.append(self.proj.start_y + (float(y) * self.proj.dy))

        positions = self.proj.transform(proj_string, xx, yy)
        return positions

    @staticmethod
    def rotate_coordinate(cx, cy, ox, oy, rotation):

        # print("Rotating")
        # Convert to radians
        rotation = math.radians(rotation)

        # Transform to origo
        # squish = math.cos(latc)
        cx = cx - ox
        cy = cy - oy

        # Rotate coordinates:
        cxr = cx * math.cos(rotation) - cy * math.sin(rotation)
        cyr = cx * math.sin(rotation) + cy * math.cos(rotation)

        # Adjust for origo
        cxr = cxr + ox
        cyr = cyr + oy
        return cxr, cyr

    def get_mid_box_point(self, cx, cy, gox, goy):

        cxr1, cyr1 = self.rotate_coordinate(cx, cy, gox, goy, -self.rotation)
        pos = self.proj.transform("EPSG:4326", cxr1, cyr1)
        lat = pos[0]
        lon = pos[1]
        # print("rotated geographic mid point", lon, lat)
        return lon, lat


class ImageTile(object):
    def __init__(self, filename, name="", description="", north=None, south=None, east=None, west=None,
                 rotation=None, ll_lon=None, ll_lat=None, lr_lon=None, lr_lat=None, ur_lon=None, ur_lat=None,
                 ul_lon=None, ul_lat=None):
        self.filename = filename
        self.name = name
        self.description = description
        self.north = north
        self.south = south
        self.west = west
        self.east = east
        self.rotation = rotation
        self.ll_lon = ll_lon
        self.ll_lat = ll_lat
        self.lr_lon = lr_lon
        self.lr_lat = lr_lat
        self.ur_lon = ur_lon
        self.ur_lat = ur_lat
        self.ul_lon = ul_lon
        self.ul_lat = ul_lat


class KMLGroundOverlay(object):
    def __init__(self, image, name=None, desc=None):
        if name is None:
            name = "Name of data"
        if desc is None:
            desc = "Description of the data"
        self.image = image
        self.name = name
        self.description = desc

    def write_kml(self, fname, tiles, mode="LatLonBox"):

        fh = open(fname, "w")
        fh.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        if mode == "LatLonQuad":
            fh.write('<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2">\n')
        else:
            fh.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
        fh.write('  <Folder>\n')
        fh.write('    <name>' + self.name + '</name>\n')
        fh.write('    <description>' + self.description + '</description>\n')

        for tile in tiles:
            fh.write('    <GroundOverlay>\n')
            fh.write('      <name>' + tile.name + '</name>\n')
            fh.write('      <description>' + tile.description + '</description>\n')
            fh.write('      <drawOrder>50</drawOrder>\n')
            fh.write('      <Icon>\n')
            fh.write('         <href>files/' + tile.filename + '</href>\n')
            fh.write('      </Icon>\n')
            fh.write('      <altitudeMode>clampToGround</altitudeMode>\n')
            if mode == "LatLonQuad":
                corner_string = str(tile.ll_lon) + "," + str(tile.ll_lat) + " " +\
                                str(tile.lr_lon) + "," + str(tile.lr_lat) + " " +\
                                str(tile.ur_lon) + "," + str(tile.ur_lat) + " " +\
                                str(tile.ul_lon) + "," + str(tile.ul_lat)
                print("String:", corner_string)
                fh.write('      <gx:LatLonQuad>\n')
                fh.write('        <coordinates>' + corner_string + '</coordinates>\n')
                fh.write('      </gx:LatLonQuad>\n')
            elif mode == "LatLonBox":
                fh.write('      <LatLonBox>\n')
                fh.write('        <north>' + str(tile.north) + '</north>\n')
                fh.write('        <south>' + str(tile.south) + '</south>\n')
                fh.write('        <east>' + str(tile.east) + '</east>\n')
                fh.write('        <west>' + str(tile.west) + '</west>\n')
                fh.write('        <rotation>' + str(tile.rotation) + '</rotation>\n')
                fh.write('      </LatLonBox>\n')
            else:
                raise NotImplementedError
            fh.write('    </GroundOverlay>\n')
        fh.write('  </Folder>\n')
        fh.write('</kml>\n')
        fh.close()
