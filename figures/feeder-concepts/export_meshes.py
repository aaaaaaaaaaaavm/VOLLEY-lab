"""Read preserved FDR09 native CAD without saving it; export visualization-only meshes."""
from pathlib import Path
import json,gzip,hashlib
import FreeCAD as App
import MeshPart
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[1]
PACKAGE=REPO/'experiments/feeder_common_boundary';RELEASE=PACKAGE/'release'
NAMES=['lead_screw','rack_pawl','spring_dual_gate','belt_shuttle','indexed_drum','telescopic','pantograph']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((PACKAGE/'MANIFEST.json').read_text())['files'];exports=[]
for key in NAMES:
 stem=key+'_four_carrier_stowed_R1';native=RELEASE/(stem+'.FCStd');step=RELEASE/(stem+'.step')
 before={str(p.relative_to(REPO)):sha(p)for p in [native,step]}
 for p in [native,step]:assert sha(p)==manifest[str(p.relative_to(PACKAGE))]['sha256'],str(p)
 doc=App.openDocument(str(native));parts=[]
 for obj in doc.Objects:
  if not hasattr(obj,'Shape')or obj.Shape.isNull():continue
  mesh=MeshPart.meshFromShape(Shape=obj.Shape,LinearDeflection=.3,AngularDeflection=.15,Relative=False)
  vertices,faces=mesh.Topology
  parts.append({'cad_name':obj.Name,'label':obj.Label,'role':str(getattr(obj,'Role','unspecified')),'material_basis':str(getattr(obj,'MaterialBasis','')),'source_visibility':bool(getattr(obj,'Visibility',True)),'vertices_m':[[round(v.x/1000,9),round(v.y/1000,9),round(v.z/1000,9)]for v in vertices],'faces':[list(f)for f in faces]})
 App.closeDocument(doc.Name)
 for p in [native,step]:assert sha(p)==before[str(p.relative_to(REPO))]
 out=HERE/'meshes'/(key+'.json.gz');payload={'configuration':'FDR09-R1-2026-10-22','concept':key,'state':'four_carrier_stowed_R1','coordinate_units':'m, converted from native mm','source_files':before,'tessellation':{'software':'FreeCAD MeshPart.meshFromShape','FreeCAD_version':list(App.Version()),'linear_deflection_mm':.3,'angular_deflection_rad':.15,'relative':False,'purpose':'visualization only'},'parts':parts}
 out.write_bytes(gzip.compress(json.dumps(payload,separators=(',',':')).encode(),mtime=0))
 record={'concept':key,'native_path':str(native.relative_to(REPO)),'native_sha256':sha(native),'step_path':str(step.relative_to(REPO)),'step_sha256':sha(step),'mesh_path':str(out.relative_to(REPO)),'mesh_sha256':sha(out),'CAD_objects':len(parts),'triangles':sum(len(p['faces'])for p in parts),'all_source_parts_exported':True,'native_source_unchanged':True}
 exports.append(record);print(key,record['CAD_objects'],'parts',record['triangles'],'triangles',flush=True)
(HERE/'MESH_PROVENANCE.json').write_text(json.dumps({'revision':'FDR09-CONCEPT-VISUALS-R1','path_base':'repository_root','source_package_manifest':'experiments/feeder_common_boundary/MANIFEST.json','source_package_manifest_sha256':sha(PACKAGE/'MANIFEST.json'),'exports':exports},indent=2))
