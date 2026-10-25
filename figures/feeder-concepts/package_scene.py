"""Losslessly package the editable Blender scene; native CAD and render pixels are untouched."""
from pathlib import Path
import hashlib,lzma,json,subprocess
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
source=HERE/'FDR09_seven_concepts.blend';out=HERE/'FDR09_seven_concepts.blend.xz'
process=subprocess.Popen(['zstd','-d','-c',str(source)],stdout=subprocess.PIPE);digest=hashlib.sha256();size=0
with lzma.open(out,'wb',preset=6)as archive:
 while True:
  data=process.stdout.read(1024*1024)
  if not data:break
  digest.update(data);size+=len(data);archive.write(data)
assert process.wait()==0
check=hashlib.sha256()
with lzma.open(out,'rb')as stream:
 assert stream.read(7)==b'BLENDER';stream.seek(0)
 for data in iter(lambda:stream.read(1024*1024),b''):check.update(data)
assert check.hexdigest()==digest.hexdigest()
record={'path_base':'repository_root','archive_path':str(out.relative_to(REPO)),'archive_sha256':sha(out),'archive_bytes':out.stat().st_size,'uncompressed_scene_sha256':digest.hexdigest(),'uncompressed_scene_bytes':size,'saved_scene_sha256':sha(source),'method':'Lossless decompression of Blender Zstandard save followed by XZ compression; scene bytes are preserved.','restore':'xz --decompress --keep figures/feeder-concepts/FDR09_seven_concepts.blend.xz','renderer':'Blender4.3.2 / Workbench'}
(HERE/'SCENE_ARCHIVE.json').write_text(json.dumps(record,indent=2))
prov=HERE/'RENDER_PROVENANCE.json';data=json.loads(prov.read_text())
if 'scene_path'in data:
 capture=HERE/'RENDER_CAPTURE.json';capture.write_bytes(prov.read_bytes())
 data['source_capture_path']=str(capture.relative_to(REPO));data['source_capture_sha256']=sha(capture)
 data.pop('scene_path');data['saved_scene_sha256']=data.pop('scene_sha256')
 data['scene_archive_path']=str(out.relative_to(REPO));data['scene_archive_manifest']='figures/feeder-concepts/SCENE_ARCHIVE.json'
 data['uncompressed_scene_sha256']=digest.hexdigest();prov.write_text(json.dumps(data,indent=2))
assert out.stat().st_size<30000000
print('Lossless scene archive:',out.stat().st_size,'bytes; decompressed identity verified.')
