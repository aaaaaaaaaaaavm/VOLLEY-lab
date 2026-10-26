"""Explicit new winding/support/source mass ledger and consistent release/guide coordinates."""
from pathlib import Path
import json
H=Path(__file__).resolve().parent
def main():
    home=json.loads((H/'provenance/VOLLEY_G5_ACR1_home.json').read_text())
    replace={'stator','stator_support','track','release_cam'}
    kept=[r for r in home['BOM'] if r['subsystem']!='payload' and not r['subsystem'].startswith('sled') and r['subsystem'] not in replace]
    legacy=sum(r['mass_kg'] for r in kept)
    for name,rail,parallel in [('R10',4.75,6),('F10',3.4,2)]:
        path=H/(name+'_DESIGN.json');d=json.loads(path.read_text())
        # Repair any in-progress earlier full-parameter capture to the minimal new schema.
        magnetic=d['parameters']['magnetic']
        launch=dict(home_aft_x=200,powered_travel=2500,drive_end_aft_x=2700,brake_travel=1300 if name=='R10' else 0,
            rail_length=rail*1000,release_aft_x=2700 if name=='R10' else None,arrest_aft_x=4000 if name=='R10' else None,
            full_free_exit_aft_x=3400 if name=='F10' else None,
            cam_ramp_aft_x_mm=[2645,2695] if name=='R10' else None,cam_hold_through_aft_x_mm=4000 if name=='R10' else None)
        d['parameters']=dict(configuration_id=name+'-R1',units='mm',magnetic=magnetic,launch=launch,
            schema_scope='New finite motor/guide coordinates only;not an accepted assembly/manufacturing definition.')
        bank=dict(series=32,parallel=parallel,cells=32*parallel,initial_V=86.4,
            nominal_F=100*parallel/32,nominal_ESR_ohm=.011*32/parallel,
            adverse_F=100*parallel/32*.9*.7,adverse_ESR_ohm=.011*32/parallel*2,bare_cell_mass_kg=.02*32*parallel)
        d['source_bank']=bank;path.write_text(json.dumps(d,indent=2)+'\n')
        cu=sum(r['copper_volume_m3'] for r in d['phases'])*8960
        length=d['parameters']['magnetic']['stator_pitch_span']/1000
        components=[dict(item='Legacy nonmoving nonrail hardware',kg=legacy,basis='Sum of retained source CAD BOM;forF10 only a storage/control allowance,no modified-payload fit accepted.'),
            dict(item='New finite copper winding including declared bus paths',kg=cu,basis='Actual new conductor centreline lengths×sections×8960kg/m³'),
            dict(item='Two38x8mm guide rails',kg=2*rail*.038*.008*2700,basis='Declared new rectangular aluminum primitives'),
            dict(item='Two30mm square3mm wall backbones',kg=2*rail*(.03**2-.024**2)*2700,basis='Declared new hollow aluminum primitives'),
            dict(item='Four156mm-wide2mm GFRP stator boards',kg=4*length*.156*.002*1900,basis='Declared new plate primitives'),
            dict(item='Crossmembers',kg=(6 if name=='R10' else 4)*.28*.03*.01*2700,basis='Declared new aluminum primitives'),
            dict(item='Power/control allocation',kg=7+(bank['bare_cell_mass_kg']-1.28),basis='Original7kg allocation adjusted for actual selected bare-cell mass;spatial placement/harness not released.')]
        moving=d['moving_carrier_or_shoe_kg'];count=1 if name=='R10' else 12
        components.append(dict(item='Retained carrier' if name=='R10' else 'Twelve attached shoes',kg=moving*count,
            basis='Existing CAD moving assembly' if name=='R10' else 'Each84magnets3.6288kg+1kg explicitly allocated support/retention.'))
        if name=='R10':components.append(dict(item='Long hold-cam allocation',kg=.3,basis='New scheduling2645–2695mm ramp/4000mm hold;not finalcamCAD.'))
        dry=sum(r['kg'] for r in components);total=500+dry+48;rest=total-moving-4
        mass=dict(configuration=name+'-R1',components=components,device_initial_dry_kg=dry,initial_bus_wet_kg=500,
            manifest_payload_kg=48,initial_combined_kg=total,first_shot_rest_host_kg=rest,moving_carrier_or_shoe_kg=moving,
            source_bank=bank,source_and_inverter_catalog_gates='ExistingEatonTVcell3V/IRFP4668200V92Ahot/600Ameanphase remain unchanged.',
            F10_shoe_support_budget_kg=dict(two430x120x2mm_GFRP_plates=.43*.12*.002*2*1900,
                four400x10x6mm_Al_members=4*.4*.01*.006*2700,brackets=.027,fasteners=.12,retention_pins=.12,guide_liners=.04,
                balance_to1kg=1-(.43*.12*.002*2*1900+4*.4*.01*.006*2700+.027+.12+.12+.04)) if name=='F10' else None,
            scope='Computed and allocated mass only;no CG/inertia,manufactured mass,structural/feeder compatibility or qualification claimed.')
        (H/(name+'_MASS.json')).write_text(json.dumps(mass,indent=2)+'\n')
        print(name,'dry',dry,'resthost',rest,'cells',bank['cells'],'copper',cu,flush=True)
if __name__=='__main__':main()
