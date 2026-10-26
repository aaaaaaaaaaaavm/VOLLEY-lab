from pathlib import Path
import hashlib,json
P=Path(__file__).parent
for r in json.loads((P/'MANIFEST.json').read_text())['files']:
 assert hashlib.sha256((P/r['path']).read_bytes()).hexdigest()==r['sha256'],r['path']

r=json.loads((P/'RESULTS.json').read_text())
train=[x for x in r['rows'] if x['role']=='calibration']
k=sum(x['current_A']*x['force_N'] for x in train)/sum(x['current_A']**2 for x in train)
assert abs(k-r['calibrated_k_N_A'])<1e-12
assert len([x for x in r['rows'] if x['role']=='holdout'])==2

print("PASS: published-force-benchmark identities and declared independent arithmetic")
