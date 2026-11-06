"""Synthetic geometry regressions; no real trail is created or published."""
import tempfile
import unittest
from pathlib import Path
from gpx import validate_track


class TrackValidation(unittest.TestCase):
    def check_track(self, points, expected=1.0, loop=True, start=(0, 0), elevations=None):
        nodes = ''.join(f'<trkpt lat="{lat}" lon="{lon}">' + (f'<ele>{elevations[i]}</ele>' if elevations else '') + '</trkpt>' for i, (lat, lon) in enumerate(points))
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'synthetic.gpx'
            path.write_text('<gpx><trk><trkseg>' + nodes + '</trkseg></trk></gpx>',encoding='utf-8')
            return validate_track(path, expected, start, loop)

    def square(self):
        # 4 x approximately 250 m, with 25 m between points.
        side = .00225
        corners = [(0,0),(0,side),(side,side),(side,0),(0,0)]
        points = []
        for a,b in zip(corners,corners[1:]):
            points.extend((a[0]+(b[0]-a[0])*i/10,a[1]+(b[1]-a[1])*i/10) for i in range(10))
        return points+[corners[-1]]

    def test_valid_loop_and_missing_elevation(self):
        result = self.check_track(self.square())
        self.assertTrue(result['passed'], result)
        self.assertIsNone(result['ascent_m'])

    def test_wrong_length_and_start(self):
        result = self.check_track(self.square(), expected=2, start=(1,1))
        self.assertFalse(result['checks']['length'])
        self.assertFalse(result['checks']['start'])

    def test_gap_and_open_loop(self):
        result = self.check_track([(0,0),(0,.005),(0,.01)])
        self.assertFalse(result['checks']['gaps'])
        self.assertFalse(result['checks']['loop'])

    def test_repeated_branch_over_200_m(self):
        branch = [(0, i*.00025) for i in range(13)]
        result = self.check_track(branch+branch[-2::-1], expected=.667)
        self.assertFalse(result['checks']['repeated_section'])

    def test_linear_compares_one_way_and_elevation_threshold(self):
        line = [(0, i*.00025) for i in range(13)]
        result = self.check_track(line, expected=.334, loop=False, elevations=[100,101,102,103,104,106,107,108,109,110,111,112,113])
        self.assertTrue(result['passed'], result)
        self.assertEqual(result['ascent_m'],11)

    def test_nan_rejected(self):
        with self.assertRaises(ValueError):
            self.check_track([(0,0),(float('nan'),1)])


if __name__ == '__main__':
    unittest.main()
