import json, numpy as np, time, sys, platform
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
import vmp
EV="/tmp/real/events-part-*"; US="/tmp/real/usage-part-*"
out={}
# dataset characteristics over 5 small samples
st=[]
for r in range(5):
    c,m,uc,um=vmp.load_joined(EV,US,1350,r,demand="request")
    st.append(dict(cpu_req=c.mean(),mem_req=m.mean(),cpu_use=uc.mean(),mem_use=um.mean(),cpu_gt=float((uc.mean(1)>c).mean()),mem_gt=float((um.mean(1)>m).mean()),
                   cpu_med=float(np.median(uc.mean(1)/c)),mem_med=float(np.median(um.mean(1)/m)),corr=float(np.corrcoef(c,m)[0,1]),cpu_max=c.max(),mem_max=m.max()))
out['data']={k:float(np.mean([s[k] for s in st])) for k in st[0]}
c,m,uc,um=vmp.load_joined(EV,US,1350,0,demand="request"); npm=1000
plt.rcParams.update({'font.size':7.5,'axes.spines.top':False,'axes.spines.right':False})
fig,ax=plt.subplots(1,3,figsize=(6.8,2.3))
ax[0].scatter(c,m,s=4,alpha=0.35,color='#4c78a8'); ax[0].set_xlabel('CPU request'); ax[0].set_ylabel('Memory request'); ax[0].set_title('Requests per task',fontsize=8)
ax[1].hist(np.clip(uc.mean(1)/c,0,3),bins=40,color='#4c78a8'); ax[1].axvline(1,color='#c0392b',ls=':'); ax[1].set_xlabel('Mean CPU usage / request'); ax[1].set_title('CPU usage ratio',fontsize=8)
ax[2].hist(np.clip(um.mean(1)/m,0,3),bins=40,color='#2ca02c'); ax[2].axvline(1,color='#c0392b',ls=':'); ax[2].set_xlabel('Mean memory usage / request'); ax[2].set_title('Memory usage ratio',fontsize=8)
fig.tight_layout(); fig.savefig('/home/claude/paper/figs/fig_data.png',dpi=220); plt.close(fig)
# host utilisation for three placements
a0=vmp.ffd(c,m,npm); s2=[vmp.ffd(c,m,npm,True,k) for k in (None,m,np.maximum(c,m),c+m)]
fit=vmp.make_fit_proposed(); best=min(s2,key=lambda x:fit(x,c,m,npm))
fig,ax=plt.subplots(1,3,figsize=(6.8,2.2),sharey=True)
for a,(nm,asg) in zip(ax,(('FFD CPU',a0),('FFD 2D',s2[0]),('Proposed',best))):
    lc,lm=vmp.pm_loads(asg,c,m,npm); act=np.bincount(asg,minlength=npm)>0
    a.hist(lm[act],bins=np.linspace(0,1.6,33),color='#2ca02c' if nm=='Proposed' else '#8c8c8c'); a.axvline(1,color='#c0392b',ls=':'); a.set_title(nm,fontsize=8); a.set_xlabel('Requested memory per active host')
ax[0].set_ylabel('Hosts'); fig.tight_layout(); fig.savefig('/home/claude/paper/figs/fig_hostmem.png',dpi=220); plt.close(fig)
lc0,lm0=vmp.pm_loads(a0,c,m,npm); act0=np.bincount(a0,minlength=npm)>0
out['hostmem']=dict(max_cpuonly=float(lm0[act0].max()),over_cpuonly=int((lm0>1).sum()),mean_util_cpu_cpuonly=float(lc0[act0].mean()))
lcb,lmb=vmp.pm_loads(best,c,m,npm); actb=np.bincount(best,minlength=npm)>0
out['hostmem'].update(mean_cpu_prop=float(lcb[actb].mean()),mean_mem_prop=float(lmb[actb].mean()),mean_mem_ffd2d=float(vmp.pm_loads(s2[0],c,m,npm)[1][np.bincount(s2[0],minlength=npm)>0].mean()))
# fitness timing (microseconds per evaluation)
tm={}
for sc,(nv,npm_) in {'small':(1350,1000),'medium':(2242,2000),'large':(5365,3000)}.items():
    c_,m_,_,_=vmp.load_joined(EV,US,nv,0,demand="request"); a=vmp.ffd(c_,m_,npm_,True); res={}
    for nm,f in (('standard',vmp.fit_standard),('base',vmp.fit_paper),('proposed',vmp.make_fit_proposed())):
        f(a,c_,m_,npm_); t0=time.perf_counter()
        for _ in range(300): f(a,c_,m_,npm_)
        res[nm]=(time.perf_counter()-t0)/300*1e6
    tm[sc]=res
out['timing']=tm; out['env']=dict(py=platform.python_version(),np=np.__version__)
json.dump(out,open('/home/claude/paper/analysis_extra.json','w'),indent=1); print(json.dumps(out,indent=1))
