from pathlib import Path
import hashlib,json
P=Path(__file__).parent
for r in json.loads((P/'MANIFEST.json').read_text())['files']:
 assert hashlib.sha256((P/r['path']).read_bytes()).hexdigest()==r['sha256'],r['path']

r=json.loads((P/'RESULTS.json').read_text())
assert 3000<r['departure_delta_v_m_s']<3100
assert 800<r['lunar_capture_delta_v_m_s']<850
assert json.loads((P/'CHECKS.json').read_text())['endpoint_radius_error_km']<.002

print("PASS: lunar-delivery-design-space identities and declared independent arithmetic")

t=json.loads((P/'THREE_BODY_RESULTS.json').read_text())
assert abs(t['lunar_arrival_altitude_km']-100)<.01
assert t['last_12h_minimum_sampled_lunar_altitude_km']>99.9 and t['prearrival_radial_velocity_negative']
assert t['independent_integrator_position_difference_km']<.001
assert 0<t['capture_delta_v_m_s']<900
assert all(0<v<200 for v in t['post_capture_24h_sampled_altitude_km'])
