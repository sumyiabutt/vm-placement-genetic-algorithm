import json, numpy as np, vmp, time
EV="/tmp/real/events-part-*"; US="/tmp/real/usage-part-*"
S={"small":(1350,1000),"medium":(2242,2000)}
RUNS=5; out={}
def seeds2d(cpu,mem,n_pm):
    return [vmp.ffd(cpu,mem,n_pm,True,k) for k in (None,mem,np.maximum(cpu,mem),cpu+mem)]
def metr(a,cpu,mem,n_pm,uc,um):
    return dict(energy=vmp.energy_kwh(a,cpu,n_pm),pms=int((np.bincount(a,minlength=n_pm)>0).sum()),sla=vmp.sla_violation(a,uc,um,n_pm))
t0=time.time()
for sc,(nv,npm) in S.items():
    out[sc]={"alpha":[],"w":[],"abl":[]}
    for r in range(RUNS):
        cpu,mem,uc,um=vmp.load_joined(EV,US,nv,r,demand="request")
        ffd_cpu=vmp.ffd(cpu,mem,npm); s2=seeds2d(cpu,mem,npm)
        fit=vmp.make_fit_proposed(0.5)
        prop,_=vmp.ga(cpu,mem,npm,fit,r,min(s2,key=lambda x:fit(x,cpu,mem,npm)),use_mem=True,extra_seeds=s2[1:])
        # alpha sensitivity: re-evaluate energy of fixed placements
        row={}
        for al in (2.0,3.0,4.0):
            vmp.ALPHA=al
            row[al]={n:vmp.energy_kwh(a,cpu,npm) for n,a in (("FFD CPU",ffd_cpu),("FFD 2D",s2[0]),("Proposed",prop))}
        vmp.ALPHA=3.0; out[sc]["alpha"].append(row)
        # w sensitivity
        wr={}
        for w in (0.3,0.5,0.7):
            f=vmp.make_fit_proposed(w); best=min(s2,key=lambda x:f(x,cpu,mem,npm))
            a,_=vmp.ga(cpu,mem,npm,f,r,best,use_mem=True,extra_seeds=s2[1:]); wr[w]=metr(a,cpu,mem,npm,uc,um)
        out[sc]["w"].append(wr)
        # ablation
        ab={}
        ab["FFD 2D (single seed, no GA)"]=metr(s2[0],cpu,mem,npm,uc,um)
        a,_=vmp.ga(cpu,mem,npm,fit,r,s2[0],use_mem=True); ab["Single seed + GA operators"]=metr(a,cpu,mem,npm,uc,um)
        best=min(s2,key=lambda x:fit(x,cpu,mem,npm)); ab["Multi seed selection only (no GA)"]=metr(best,cpu,mem,npm,uc,um)
        a,_=vmp.ga(cpu,mem,npm,fit,r,best,use_mem=True,extra_seeds=s2[1:],p_cons=0.0); ab["Multi seed + GA, no consolidation"]=metr(a,cpu,mem,npm,uc,um)
        ab["Full proposed GA"]=metr(prop,cpu,mem,npm,uc,um)
        out[sc]["abl"].append(ab)
        print(sc,r+1,round(time.time()-t0),flush=True)
json.dump(out,open("/home/claude/vmp_code/extra_out.json","w"),indent=1)
