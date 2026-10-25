"""Shared orthographic Workbench scene for preserved FDR09 concept geometry."""
from pathlib import Path
import bpy,json,gzip,math,hashlib
from itertools import product
from mathutils import Vector,Matrix
from bpy_extras.object_utils import world_to_camera_view
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[1];OUT=HERE/'renders'
W,H=1800,1350
COLORS={'fixed':(.64,.67,.68,1),'moving':(.30,.35,.38,1),'drive':(.61,.40,.25,1),'payload':(.25,.46,.62,1),'gate':(.37,.42,.45,1),'latch':(.37,.42,.45,1),'clamp':(.37,.42,.45,1),'docking':(.37,.42,.45,1),'receiver':(.46,.51,.53,1),'passive_insert':(.77,.79,.75,1),'unselected_actuator':(.76,.77,.78,1),'unselected_sensor':(.76,.77,.78,1),'default':(.57,.61,.63,1)}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
provenance=json.loads((HERE/'MESH_PROVENANCE.json').read_text());payloads=[]
for entry in provenance['exports']:
 p=REPO/entry['mesh_path'];assert sha(p)==entry['mesh_sha256'];payloads.append(json.loads(gzip.decompress(p.read_bytes())))
vertices=[Vector(v)for data in payloads for part in data['parts']for v in part['vertices_m']]
low=Vector([min(v[i]for v in vertices)for i in range(3)]);high=Vector([max(v[i]for v in vertices)for i in range(3)])
direction=Vector((1,-1,1)).normalized();rotation=(-direction).to_track_quat('-Z','Y');right=rotation@Vector((1,0,0));up=rotation@Vector((0,1,0));target=(low+high)/2
x=[(v-target).dot(right)for v in vertices];y=[(v-target).dot(up)for v in vertices]
target+=right*((min(x)+max(x))/2)+up*((min(y)+max(y))/2)
height=max((max(y)-min(y))/.78,(max(x)-min(x))/((W/H)*.86));width=height*W/H
bpy.ops.wm.read_factory_settings(use_empty=True);materials={}
for key,value in COLORS.items():
 m=bpy.data.materials.new('Display role / '+key);m.diffuse_color=value;materials[key]=m
cache={};scenes=[];metadata=[]
for index,data in enumerate(payloads):
 scene=bpy.context.scene if index==0 else bpy.data.scenes.new(data['concept']);scene.name=data['concept'];scenes.append(scene);bpy.context.window.scene=scene;bpy.context.window.view_layer=scene.view_layers[0];scene.frame_set(1)
 collection=bpy.data.collections.new(data['concept']+' / native CAD');scene.collection.children.link(collection);objects=[]
 for part in data['parts']:
  origin=[min(v[i]for v in part['vertices_m'])for i in range(3)]
  local=[[round(v[i]-origin[i],7)for i in range(3)]for v in part['vertices_m']]
  geometry_key=hashlib.sha256(json.dumps([local,part['faces']],separators=(',',':')).encode()).hexdigest()
  # Object-local coordinates permit identical native instances to share one mesh.
  # The0.1um display grid is finer than both tessellation and Blender world precision.
  if geometry_key not in cache:
   mesh=bpy.data.meshes.new('Native tessellation '+geometry_key[:12]);mesh.from_pydata(local,[],part['faces']);mesh.update();cache[geometry_key]=mesh
  obj=bpy.data.objects.new(part['label'],cache[geometry_key]);collection.objects.link(obj);obj.location=origin;objects.append(obj)
  # Material slots belong to the object to preserve a source part’s role across scenes.
  if not obj.data.materials:obj.data.materials.append(materials['default'])
  obj.material_slots[0].link='OBJECT';obj.material_slots[0].material=materials.get(part['role'],materials['default'])
  obj['cad_name']=part['cad_name'];obj['cad_label']=part['label'];obj['cad_role']=part['role'];obj['geometry_source']='preserved FDR09-R1 native CAD'
 camdata=bpy.data.cameras.new(data['concept']+' orthographic camera');camdata.type='ORTHO';camdata.ortho_scale=width;camdata.clip_start=.01;camdata.clip_end=100
 case_vertices=[Vector(v)for part in data['parts']for v in part['vertices_m']]
 case_x=[(v-target).dot(right)for v in case_vertices];case_y=[(v-target).dot(up)for v in case_vertices]
 case_target=target+right*((min(case_x)+max(case_x))/2)+up*((min(case_y)+max(case_y))/2)
 cam=bpy.data.objects.new(data['concept']+' orthographic camera',camdata);scene.collection.objects.link(cam);cam.location=case_target+direction*6;cam.rotation_euler=rotation.to_euler();scene.camera=cam
 scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=W;scene.render.resolution_y=H;scene.render.resolution_percentage=100
 shade=scene.display.shading;shade.light='STUDIO';shade.studiolight_rotate_z=.3;shade.color_type='MATERIAL';shade.show_shadows=False;shade.show_cavity=True;shade.cavity_type='WORLD';shade.curvature_ridge_factor=1.2;shade.curvature_valley_factor=1.0;shade.show_object_outline=True;shade.object_outline_color=(.14,.18,.20);shade.background_type='WORLD';scene.world=bpy.data.worlds.new(data['concept']+' white studio');scene.world.color=(1,1,1)
 scene.view_settings.view_transform='Standard';scene.view_settings.look='Medium High Contrast';scene.view_settings.exposure=0;scene.view_settings.gamma=1
 scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False;scene.render.filepath=str(OUT/(data['concept']+'_geometry.png'))
 bpy.context.window.scene=scene;bpy.context.window.view_layer=scene.view_layers[0];cam.update_tag(refresh={'OBJECT'});scene.view_layers[0].update()
 projected=[world_to_camera_view(scene,cam,obj.matrix_world@Vector(c))for obj in objects for c in obj.bound_box]
 box=[min(p.x for p in projected),max(p.x for p in projected),min(p.y for p in projected),max(p.y for p in projected)]
 print('Camera',data['concept'],'width',width,'target',list(target),'matrix',list(cam.matrix_world.translation),'bounds',box,flush=True)
 assert min(box)>=0 and max(box)<=1,(data['concept'],box)
 bpy.ops.render.render(write_still=True)
 metadata.append({'concept':data['concept'],'path':str(Path(scene.render.filepath).relative_to(REPO)),'sha256':sha(Path(scene.render.filepath)),'evidence_class':'native-CAD-derived Blender render','geometry_revision':data['configuration'],'state':data['state'],'rendered_CAD_objects':len(objects),'omitted_CAD_objects':[],'camera':{'projection':'orthographic','direction':list(direction),'location_m':list(cam.location),'rotation_euler_rad':list(cam.rotation_euler),'target_m':list(case_target),'field_width_m':width,'field_height_m':height,'geometry_frame_uv':box},'dimensions_px':[W,H],'software':'Blender '+bpy.app.version_string+' / Workbench','object_local_display_grid_m':1e-7,'material_policy':'Display categories by declared CAD Role; no physical material qualification inferred.','mesh_source':provenance['exports'][index]})
 # A source-only drive detail complements the common-scale complete assembly.
 selected=[o for o in objects if(o['cad_label'].startswith('Drum_')if data['concept']=='indexed_drum'else(o['cad_label'].startswith('B_3U__')and(o['cad_role']in ['drive','moving','unselected_actuator','unselected_sensor']or any(t in o['cad_label']for t in ['Guide_shaft','Power_off_capture_rack','Storage_gate','Second_escapement_gate']))))]
 assert selected,data['concept']
 detail=bpy.data.scenes.new(data['concept']+'_drive_detail');scenes.append(detail);bpy.context.window.scene=detail;bpy.context.window.view_layer=detail.view_layers[0];detail.frame_set(1)
 detail_collection=bpy.data.collections.new(data['concept']+' / original-position drive detail');detail.collection.children.link(detail_collection)
 for o in selected:copy=o.copy();copy.data=o.data;detail_collection.objects.link(copy);copy.location=o.location.copy()
 selected_labels={o['cad_label']for o in selected}
 corners=[]
 for part in data['parts']:
  if part['label']not in selected_labels:continue
  lo=[min(v[i]for v in part['vertices_m'])for i in range(3)];hi=[max(v[i]for v in part['vertices_m'])for i in range(3)]
  corners.extend(Vector(v)for v in product(*[(lo[i],hi[i])for i in range(3)]))
 detail_target=Vector([sum(v[i]for v in corners)/len(corners)for i in range(3)])
 dx=[(v-detail_target).dot(right)for v in corners];dy=[(v-detail_target).dot(up)for v in corners]
 detail_target+=right*((min(dx)+max(dx))/2)+up*((min(dy)+max(dy))/2)
 detail_height=max((max(dy)-min(dy))/.78,(max(dx)-min(dx))/((W/H)*.86));detail_width=detail_height*W/H
 cd=bpy.data.cameras.new(data['concept']+' detail camera');cd.type='ORTHO';cd.ortho_scale=detail_width;cd.clip_start=.01;cd.clip_end=100
 camera=bpy.data.objects.new(data['concept']+' detail camera',cd);detail.collection.objects.link(camera);camera.location=detail_target+direction*6;camera.rotation_euler=rotation.to_euler();detail.camera=camera
 detail.render.engine='BLENDER_WORKBENCH';detail.render.resolution_x=W;detail.render.resolution_y=H;detail.render.resolution_percentage=100;detail.world=scene.world
 shading=detail.display.shading;shading.light='STUDIO';shading.studiolight_rotate_z=.3;shading.color_type='MATERIAL';shading.show_shadows=False;shading.show_cavity=True;shading.cavity_type='WORLD';shading.curvature_ridge_factor=1.2;shading.curvature_valley_factor=1.;shading.show_object_outline=True;shading.object_outline_color=(.14,.18,.20);shading.background_type='WORLD'
 detail.view_settings.view_transform='Standard';detail.view_settings.look='Medium High Contrast';detail.render.image_settings.file_format='PNG';detail.render.filepath=str(OUT/(data['concept']+'_detail.png'))
 bpy.context.window.scene=detail;bpy.context.window.view_layer=detail.view_layers[0];detail.frame_set(1);camera.update_tag(refresh={'OBJECT'});detail.view_layers[0].update()
 projected_detail=[world_to_camera_view(detail,camera,v)for v in corners]
 detail_box=[min(v.x for v in projected_detail),max(v.x for v in projected_detail),min(v.y for v in projected_detail),max(v.y for v in projected_detail)]
 assert min(detail_box)>=0 and max(detail_box)<=1,(data['concept'],'detail',detail_box)
 assert(camera.matrix_world.translation-camera.location).length<1e-5,(data['concept'],'camera matrix')
 actual_points=[world_to_camera_view(detail,camera,o.matrix_world@Vector(c))for o in detail_collection.objects for c in o.bound_box]
 actual_box=[min(v.x for v in actual_points),max(v.x for v in actual_points),min(v.y for v in actual_points),max(v.y for v in actual_points)]
 assert min(actual_box)>=0 and max(actual_box)<=1,(data['concept'],'actual detail bounds',actual_box)
 bpy.ops.render.render(write_still=True)
 metadata[-1]['detail']={'path':str(Path(detail.render.filepath).relative_to(REPO)),'sha256':sha(Path(detail.render.filepath)),'evidence_class':'native-CAD-derived original-position geometry detail','rendered_CAD_objects':[o['cad_label']for o in selected],'omitted_CAD_objects':[o['cad_label']for o in objects if o not in selected],'camera':{'projection':'orthographic','direction':list(direction),'target_m':list(detail_target),'field_width_m':detail_width,'field_height_m':detail_height,'geometry_frame_uv':actual_box,'location_m':list(camera.location),'rotation_euler_rad':list(camera.rotation_euler)},'scope':'Drum rotor and axle only'if data['concept']=='indexed_drum'else'B_3U drive, pusher, guide and retention parts; payload and cassette shell omitted for access','original_CAD_positions_preserved':True}
 print('Rendered',data['concept'],'complete assembly and original-position drive detail',flush=True)
bpy.context.preferences.filepaths.save_version=0
bpy.context.window.scene=scenes[0];bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'FDR09_seven_concepts.blend'),compress=True)
(HERE/'RENDER_PROVENANCE.json').write_text(json.dumps({'revision':'FDR09-CONCEPT-VISUALS-R1','path_base':'repository_root','shared_camera':'same orthographic direction and field; individually centered on projected geometry','shared_material_roles':COLORS,'shared_physical_scale':True,'display_role_policy':'blue=payload proxy; copper=drive; graphite=moving/retention; aluminium-grey=fixed; pale=unselected actuator/sensor envelopes','scene_path':str((HERE/'FDR09_seven_concepts.blend').relative_to(REPO)),'scene_sha256':sha(HERE/'FDR09_seven_concepts.blend'),'render_script_path':str(Path(__file__).relative_to(REPO)),'render_script_sha256':sha(Path(__file__)),'renders':metadata},indent=2))
