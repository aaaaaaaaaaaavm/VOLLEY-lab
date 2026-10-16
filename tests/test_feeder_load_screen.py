import importlib.util
import math
from pathlib import Path
import unittest

path=Path(__file__).resolve().parents[1]/'analysis/gen6_feeder_load_screen.py'
spec=importlib.util.spec_from_file_location('feed',path)
feed=importlib.util.module_from_spec(spec);spec.loader.exec_module(feed)


class FeederLoadTests(unittest.TestCase):
    def test_triangular_profile_integrates_to_stroke(self):
        for stroke,duration in ((.2,2),(.2,5),(.2,10)):
            m=feed.motion(stroke,duration)
            self.assertAlmostEqual(.5*m['peak_velocity_m_s']*duration,stroke)
            self.assertAlmostEqual(m['acceleration_m_s2']*duration/2,m['peak_velocity_m_s'])

    def test_scissor_virtual_work_matches_geometric_derivative(self):
        for low in (5,10,20):
            p=feed.pantograph(.2,3,low,70,10)
            theta=math.radians(low);h=1e-6;L=p['half_link_length_m']
            dy=(6*L*math.sin(theta+h)-6*L*math.sin(theta-h))/(2*h)
            db=(2*L*math.cos(theta+h)-2*L*math.cos(theta-h))/(2*h)
            self.assertAlmostEqual(abs(10*dy/db),p['peak_ideal_input_force_N'],places=5)
            self.assertAlmostEqual(p['final_height_m']-p['initial_height_m'],.2)

    def test_common_cases_and_energy_bounds(self):
        d=feed.build(); self.assertEqual(d['case_count'],27)
        for c in d['cases']:
            self.assertGreaterEqual(c['positive_mechanical_work_lower_bound_J'],c['opposing_force_N']*.2)
            self.assertGreater(c['spring'][0]['released_energy_J'],0)
            self.assertGreater(c['pantograph'][0]['peak_force_multiplier'],c['pantograph'][2]['peak_force_multiplier'])
            for screw in c['screw']:
                work_per_turn=screw['torque_N_m']*2*math.pi*screw['assumed_efficiency']
                self.assertAlmostEqual(work_per_turn,c['peak_required_output_force_N']*.002)
        self.assertFalse(d['square_thread_static_backdrive_screen']['scenarios'][0]['ideal_self_locking'])

    def test_singular_or_invalid_geometry_rejected(self):
        with self.assertRaises(ValueError):feed.pantograph(.2,3,0,70,10)
        with self.assertRaises(ValueError):feed.motion(.2,0)
