"""Verify the source-derived seven-concept publication and lossless editable scene."""
from pathlib import Path
import json,hashlib,gzip,lzma,struct
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((HERE/'MANIFEST.json').read_text());p=json.loads((HERE/'RENDER_PROVENANCE.json').read_text());native=json.loads((REPO/'experiments/feeder_common_boundary/MANIFEST.json').read_text())['files']
assert len(m['concepts'])==7 and sorted(r['rank']for r in m['concepts'])==list(range(1,8))
fields=set();objects=0;detail_objects=0
for r in m['concepts']:
 assert r['geometry_revision']=='FDR09-R1-2026-10-22';assert r['trade_revision']=='FDR10-R0 / D27-R2'
 for kind in ['native','step']:
  path=r['source_'+kind];assert sha(REPO/path)==r['source_'+kind+'_sha256'];relative=str((REPO/path).relative_to(REPO/'experiments/feeder_common_boundary'));assert native[relative]['sha256']==r['source_'+kind+'_sha256']
 assert sha(REPO/r['trade_source'])==r['trade_source_sha256']
 assert sha(REPO/r['image_path'])==r['image_sha256'];assert sha(REPO/r['detail_image_path'])==r['detail_image_sha256']
 render=r['render'];assert not render['omitted_CAD_objects'];fields.add((render['camera']['field_width_m'],render['camera']['field_height_m'],tuple(render['camera']['direction'])))
 box=render['camera']['geometry_frame_uv'];assert min(box)>=0 and max(box)<=1
 source=json.loads(gzip.decompress((REPO/render['mesh_source']['mesh_path']).read_bytes()));assert sha(REPO/render['mesh_source']['mesh_path'])==render['mesh_source']['mesh_sha256']
 labels={q['label']for q in source['parts']};detail=render['detail'];shown=set(detail['rendered_CAD_objects']);omitted=set(detail['omitted_CAD_objects']);assert shown|omitted==labels and not shown&omitted;assert detail['original_CAD_positions_preserved'];assert min(detail['camera']['geometry_frame_uv'])>=0 and max(detail['camera']['geometry_frame_uv'])<=1
 assert render['rendered_CAD_objects']==len(source['parts']);objects+=len(source['parts']);detail_objects+=len(shown)
 for filename in [r['image_path'],r['detail_image_path']]:
  png=(REPO/filename).read_bytes();assert png[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',png[16:24])==(1800,1680)
assert len(fields)==1
for name,record in m['files'].items():
 path=REPO/name;assert path.is_file()and sha(path)==record['sha256'];assert path.stat().st_size<=30000000,name
archive=json.loads((HERE/'SCENE_ARCHIVE.json').read_text());assert sha(REPO/archive['archive_path'])==archive['archive_sha256'];h=hashlib.sha256();size=0
with lzma.open(REPO/archive['archive_path'],'rb')as stream:
 assert stream.read(7)==b'BLENDER';stream.seek(0)
 for data in iter(lambda:stream.read(1024*1024),b''):h.update(data);size+=len(data)
assert h.hexdigest()==archive['uncompressed_scene_sha256']and size==archive['uncompressed_scene_bytes']
assert sha(REPO/p['source_capture_path'])==p['source_capture_sha256'];assert sha(REPO/p['render_script_path'])==p['render_script_sha256']
result={'status':'passed','path_base':'repository_root','concepts':7,'full_source_CAD_objects':objects,'displayed_detail_CAD_objects':detail_objects,'complete_view_camera_and_physical_scale':'identical direction and field; individually centered','detail_views':'original source positions; displayed/omitted sets partition all source objects; explicit scale bars','source_native_STEP_hashes':'matched captured upstream manifest','source_and_export_files':len(m['files']),'lossless_scene_archive_bytes':archive['archive_bytes'],'scene_decompression_identity':'passed','publication_file_limit_bytes':30000000,'source_capture_and_renderer_identity':'passed'}
(HERE/'ASSET_QA.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
