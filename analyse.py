import json, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
D = json.load(open('/mnt/user-data/outputs/results.json'))
scales = ['small','medium','large']
names = [r['method'] for r in D['small'][0]]
short = ['FFD CPU','FFD 2D','Standard GA','Base paper GA','Proposed GA']
col = ['#8c8c8c','#4c78a8','#b0b0b0','#f58518','#2ca02c']
def stat(sc, i, k):
    v = np.array([run[i][k] for run in D[sc]]); return v.mean(), v.std(ddof=1)
out = {}
for sc in scales:
    out[sc] = {n: {k: stat(sc,i,k) for k in ('energy_kwh','active_pms','sla_violation_pct','seconds','gens','fitness_calls','mem_overload_pms')} for i,n in enumerate(names)}
json.dump(out, open('summary.json','w'), indent=1)
# paired differences proposed vs FFD2D and vs FFD CPU
def paired(sc, a, b, k):
    d = np.array([run[a][k]-run[b][k] for run in D[sc]]); return d.mean(), d.std(ddof=1), len(d)
for sc in scales:
    print(sc, 'E prop-ffd2d', paired(sc,4,1,'energy_kwh'), 'SLA prop-ffd2d', paired(sc,4,1,'sla_violation_pct'), 'SLA prop-ffdcpu', paired(sc,4,0,'sla_violation_pct'), 'PM prop-ffd2d', paired(sc,4,1,'active_pms'))
plt.rcParams.update({'font.size':9,'font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False})
def bars(key, ylabel, fn, idx=range(5)):
    fig, ax = plt.subplots(figsize=(6.2,3.2)); w = 0.16; x = np.arange(3)
    for j,i in enumerate(idx):
        m = [out[sc][names[i]][key][0] for sc in scales]; s = [out[sc][names[i]][key][1] for sc in scales]
        ax.bar(x+(j-2)*w, m, w, yerr=s, capsize=2, label=short[i], color=col[i], edgecolor='white', linewidth=0.5)
    ax.set_xticks(x); ax.set_xticklabels(['Small (1350 VMs)','Medium (2242 VMs)','Large (5365 VMs)'])
    ax.set_ylabel(ylabel); ax.legend(ncol=3, fontsize=7.5, frameon=False, loc='upper left'); ax.grid(axis='y', alpha=0.25)
    fig.tight_layout(); fig.savefig(fn, dpi=200); plt.close(fig)
bars('energy_kwh','Energy over 24 h (kWh)','figs/fig_energy.png')
bars('active_pms','Active PMs','figs/fig_pms.png')
bars('sla_violation_pct','SLA violation (%)','figs/fig_sla.png')
# trade-off scatter (per run points, all scales)
fig, axs = plt.subplots(1,3, figsize=(6.6,2.6))
for ax,sc in zip(axs,scales):
    for i in (0,1,4):
        e=[run[i]['energy_kwh'] for run in D[sc]]; s=[run[i]['sla_violation_pct'] for run in D[sc]]
        ax.scatter(e,s,s=18,color=col[i],label=short[i],edgecolor='white',linewidth=0.4)
    ax.set_title(sc.capitalize(), fontsize=9); ax.set_xlabel('Energy (kWh)'); ax.grid(alpha=0.25)
axs[0].set_ylabel('SLA violation (%)'); axs[0].legend(fontsize=7, frameon=False)
fig.tight_layout(); fig.savefig('figs/fig_tradeoff.png', dpi=200); plt.close(fig)
# architecture diagram
fig, ax = plt.subplots(figsize=(7.0,3.6)); ax.set_xlim(0,100); ax.set_ylim(0,52); ax.axis('off')
def box(x,y,w,h,t,fc='#e8eef7',ec='#34495e'):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.3,rounding_size=1.2',fc=fc,ec=ec,lw=1.1)); ax.text(x+w/2,y+h/2,t,ha='center',va='center',fontsize=7.6)
def arrow(x1,y1,x2,y2): ax.annotate('',xy=(x2,y2),xytext=(x1,y1),arrowprops=dict(arrowstyle='->',lw=1.1,color='#34495e'))
box(1,36,17,11,'Google cluster\ntask_events\n(requests)'); box(1,19,17,11,'Google cluster\ntask_usage\n(5 min windows)')
box(24,27,17,14,'Task sampling\nand join by\njob, task index'); arrow(18,41,24,36); arrow(18,25,24,31)
box(47,36,18,11,'Seeding\nFFD CPU, FFD 2D\nand key variants'); arrow(41,34,47,40)
box(47,10,18,12,'Placement demand\n(CPU, memory)'); arrow(41,29,47,18)
box(72,29,26,17,'GA loop\nselection, crossover,\nmutation, consolidation',fc='#f4f4f4'); arrow(65,41,72,40); arrow(65,16,75,29)
box(72,5,26,13,'Evaluation\nenergy, active PMs,\nSLA, run time',fc='#f4f4f4'); arrow(85,29,85,18)
ax.add_patch(Rectangle((44.5,1.5),55,47.5,fill=False,ls=(0,(2,3)),lw=1.4,ec='#c0392b'))
ax.text(46,49.6,'Novelty: multi seed start, CPU+memory residual fitness, consolidation mutation',fontsize=7.4,color='#c0392b',va='bottom')
fig.tight_layout(); fig.savefig('figs/fig_arch.png', dpi=200); plt.close(fig)
