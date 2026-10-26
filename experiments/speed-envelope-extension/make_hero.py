"""One-message view of existing common upper brackets. No model is executed."""
from pathlib import Path
import hashlib,json,re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
H=Path(__file__).resolve().parent
def update():
    results=json.loads((H/'RESULTS.json').read_text());data=[]
    for adverse in [False,True]:
        rows=[r for r in results['upper_brackets'] if r['adverse']==adverse]
        passed=min(r['last_sampled_pass_m_s'] for r in rows)
        failed=min(r['next_sampled_fail_m_s'] for r in rows)
        limiting=[r['L_uH'] for r in rows if r['next_sampled_fail_m_s']==failed]
        data.append(dict(condition='Adverse' if adverse else 'Nominal',last_common_sampled_pass_m_s=passed,
            next_limiting_sampled_fail_m_s=failed,limiting_inductances_uH=limiting,
            operational_or_reset_qualification=False))
    plt.rcParams.update({'font.family':'DejaVu Sans','svg.fonttype':'none','pdf.fonttype':42})
    fig=plt.figure(figsize=(11,5.3),facecolor='white')
    ax=fig.add_axes([.27,.25,.68,.47])
    fig.text(.055,.91,'CURRENT-MODEL UPPER SPEED BRACKETS',fontsize=23,weight='bold',color='#17242d')
    fig.text(.055,.83,'Common upper brackets across 3, 20 and 100 µH cases',fontsize=15,color='#52606b')
    colors=['#087f81','#b56b12']
    for i,row in enumerate(data):
        y=1-i;passed=row['last_common_sampled_pass_m_s'];failed=row['next_limiting_sampled_fail_m_s'];col=colors[i]
        fig.text(.055,.61-i*.22,row['condition'],fontsize=22,weight='bold',color=col)
        label='100 µH sets bound' if not i else '3 / 100 µH set bound'
        fig.text(.055,.555-i*.22,label,fontsize=11,color='#52606b')
        ax.plot([passed,failed],[y,y],color=col,lw=4)
        ax.scatter([passed],[y],s=105,color=col,marker='o',zorder=5)
        ax.scatter([failed],[y],s=110,color=col,marker='x',linewidths=2.5,zorder=5)
        ax.annotate(f'{passed:.2f} m/s',xy=(passed,y),xytext=(-45,27),textcoords='offset points',ha='center',fontsize=21,weight='bold',color=col,
            arrowprops=dict(arrowstyle='-',color=col,lw=.8))
        ax.annotate(f'{failed:.2f} m/s',xy=(failed,y),xytext=(45,-34),textcoords='offset points',ha='center',fontsize=16,color='#52606b',
            arrowprops=dict(arrowstyle='-',color=col,lw=.8))
    ax.set(xlim=(3.5,4.85),ylim=(-.6,1.6),yticks=[],xlabel='Requested command [m/s]')
    ax.xaxis.label.set_fontsize(13);ax.tick_params(axis='x',labelsize=12)
    ax.set_xticks([3.5,3.75,4.,4.25,4.5,4.75])
    ax.grid(axis='x',color='#dbe2e6',lw=.8);ax.set_axisbelow(True)
    for side in ['top','right','left']:ax.spines[side].set_visible(False)
    ax.spines['bottom'].set_color('#aab6be')
    fig.text(.055,.12,'● Last common tested pass     × Next tested failure',fontsize=13,color='#17242d')
    fig.text(.055,.055,'Modeled release/arrest gates. Operational lower floor, clearance and reset remain unverified.',fontsize=11,color='#52606b')
    for suffix in ['png','pdf','svg']:fig.savefig(H/f'ENVELOPE_HERO.{suffix}',dpi=180)
    svg=H/'ENVELOPE_HERO.svg'
    svg.write_text(''.join(line.rstrip()+'\n' for line in svg.read_text().splitlines()))
    plt.close(fig)
    (H/'HERO_DATA.json').write_text(json.dumps(dict(results_sha256=hashlib.sha256((H/'RESULTS.json').read_bytes()).hexdigest(),rows=data,no_resimulation=True),indent=2)+'\n')
    p=H/'README.md';text=p.read_text()
    if '<!-- SIMPLE_HERO -->' not in text:
        heading,rest=text.split('\n',1)
        hero='''

<!-- SIMPLE_HERO -->
![Nominal common tested pass 4.60 m/s, next limiting failure 4.65 m/s; adverse common pass 3.70 m/s, next limiting failure 3.75 m/s.](ENVELOPE_HERO.png)

| Source condition | Common tested upper pass | Next limiting failure | Limiting sensitivity |
|---|---:|---:|---|
| Nominal | **4.60 m/s** | 4.65 m/s | 100 µH |
| Adverse | **3.70 m/s** | 3.75 m/s | 3 / 100 µH |

These are sampled modeled launch/arrest gates. Current published command points remain 1, 2 and 3 m/s; operational lower speed, full clearance and powered reset are unverified.

[Editable SVG](ENVELOPE_HERO.svg) · [PDF](ENVELOPE_HERO.pdf)
<!-- END_SIMPLE_HERO -->

'''
        text=heading+hero+rest.lstrip('\n')
    text=text.replace('[Sampled source-model gates](SAMPLED_ENVELOPE.svg) · [Separate geometry and inventory requirements](GEOMETRY_AND_INVENTORY.svg). Editable SVG text and Type42-font PDF exports accompany each PNG.',
        '''<details>
<summary>Detailed three-panel evidence and architecture requirements</summary>

![Detailed modeled contact-release, arrest-position and inductance-boundary results.](SAMPLED_ENVELOPE.png)

[Editable detailed plot](SAMPLED_ENVELOPE.svg) · [Geometry and inventory requirements](GEOMETRY_AND_INVENTORY.svg)

</details>''')
    text=text.replace(' Only this new folder is written. Accepted files, repositories outside this new folder and current academic outputs are untouched. No commit or push is performed.','')
    p.write_text(text)
    print('PASS:one-message hero and result table;technical plot optional;no resimulation.')
if __name__=='__main__':update()
