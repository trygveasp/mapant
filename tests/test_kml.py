import unittest
import mapant
import os
import shutil

class RunKLM(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        if os.path.exists("doc.kml"):
            os.unlink("doc.kml")
        if os.path.exists("files"):
            shutil.rmtree("files")
        if os.path.exists("test.kmz"):
            os.unlink("test.kmz")

    def test_kml_vestre_spone(self):
        kwargs = {
            "world_filename": "examples/mapant-export-211859-6656711-215781-6660648.pgw",
            "filename": "examples/mapant-export-211859-6656711-215781-6660648.png",
            "nx": 4016,
            "ny": 4031,
            "dx": 1536,
            "dy": 1536,
            "name_of_data": "name_of_data",
            "description_of_data": "description_of_data",
            "mode": "LatLonBox",
            "output": "test.kmz"
        }
        mapant.mapant2kml(**kwargs)
