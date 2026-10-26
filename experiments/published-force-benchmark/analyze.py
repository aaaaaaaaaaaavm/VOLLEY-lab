"""Traceable Figure19a data extraction; fitted observable, not geometry validation."""
from pathlib import Path
import json,csv
P=Path(__file__).parent
# Coordinates from publisher PDF p14 rendered1600px long edge with Poppler.
# Five red experimental markers, local red-pixel median centre.
POINTS=[(.5,277,536),(1.,337,495),(1.5,397,454),(2.,457,413),(2.5,515,374)]
def calculate():
 rows=[dict(current_A=i,pixel_x=x,pixel_y=y,force_N=(578-y)*40/240,force_reading_uncertainty_N=2*40/240,current_axis_reading_uncertainty_A=2*2.5/(516-218),role='calibration' if i in [.5,1.5,2.] else 'holdout') for i,x,y in POINTS]
 train=[r for r in rows if r['role']=='calibration'];slope=sum(r['current_A']*r['force_N'] for r in train)/sum(r['current_A']**2 for r in train)
 for r in rows:r.update(predicted_force_N=slope*r['current_A'],residual_N=r['force_N']-slope*r['current_A'])
 return dict(source=dict(doi='10.3390/rs14174205',url='https://www.mdpi.com/2072-4292/14/17/4205',publisher_pdf_sha256='c996e1768abfcbb85f97155acbe3871a4b69246079dcbb0b9b80abdb39782b9f',page=14,figure='19a',observable='Experimental ejection force versus coil current',render='pdftoppm -f14 -l14 -scale-to1600 -singlefile -png',axes_pixels=dict(x0=218,xmax=516,y0=578,ymax=338),red_marker_selection='Median red pixels in local7x19 windows; nominal centres(277,536),(337,495),(397,455),(457,414),(515,375); R>170,G<135,B<150'),model='F=k I; zero-intercept empirical Lorentz-form fit, no reconstructed magnetic geometry',calibrated_k_N_A=slope,holdout_max_absolute_error_N=max(abs(r['residual_N']) for r in rows if r['role']=='holdout'),rows=rows,limitations=['Five points digitized from plotted published experiments, not raw author data or VOLLEY measurements.','Uncertainty is an assumed two-pixel reading allocation; excludes original test uncertainty and systematic axis/rendering error.','Calibration and held-out currents share one experiment; this is limited out-of-sample checking, not independent apparatus validation.','No external field/geometry reconstruction or transfer to ACR1 high currents established.','Published force equation14 alone does not specify the finite Halbach topology or high-speed source/thermal behaviour.'])
def main():
 r=calculate();(P/'RESULTS.json').write_text(json.dumps(r,indent=2)+'\n')
 with (P/'DIGITIZED_POINTS.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(r['rows'][0]),lineterminator="\n");w.writeheader();w.writerows(r['rows'])
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 plt.rcParams.update({"svg.fonttype":"none","pdf.fonttype":42})
 fig,ax=plt.subplots(figsize=(6.6,4.3),layout='constrained')
 for role,mark in [('calibration','o'),('holdout','s')]:
  a=[x for x in r['rows'] if x['role']==role];ax.errorbar([x['current_A'] for x in a],[x['force_N'] for x in a],yerr=[x['force_reading_uncertainty_N'] for x in a],fmt=mark,color='#146c80' if role=='calibration' else '#a3642f',label=role.capitalize()+' digitized points',capsize=3)
 ax.plot([0,2.5],[0,2.5*r['calibrated_k_N_A']],color='#333333',label='Fitted F = kI');ax.set(xlabel='Coil current (A)',ylabel='Published experimental force (N)',title='Published deployer force–current observable');ax.spines[['top','right']].set_visible(False);ax.legend(fontsize=8)
 for ext in ['png','pdf','svg']:fig.savefig(P/('force_current_benchmark.'+ext),dpi=180)
 svg=P/"force_current_benchmark.svg";svg.write_text("\n".join(line.rstrip() for line in svg.read_text().splitlines())+"\n")
 print(json.dumps({k:r[k] for k in ['calibrated_k_N_A','holdout_max_absolute_error_N']}))
if __name__=='__main__':main()
