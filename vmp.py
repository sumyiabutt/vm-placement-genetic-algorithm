"""Multi-resource accelerated GA for energy-efficient VM placement.
Baselines: FFD (CPU only), standard GA (energy fitness), base-paper GA (CPU residual),
FFD 2D (CPU+memory). Proposed: GA with CPU+memory residual fitness.
"""
import numpy as np, time, glob, csv, json, argparse, os

# ---------- configuration (assumptions are stated in README) ----------
PMIN, PMAX, ALPHA = 160.0, 220.0, 3.0   # watt, watt, shape constant (Eq. 3 of base paper)
HOURS = 24.0
POP, TOURN, CX, MUT, RUNS_STALL, MAX_GEN = 64, 16, 0.5, 0.015, 50, 999
PENALTY = 1e3

# ---------- data ----------
def load_google_tasks(folder, n_vm, seed=0):
    """Read Google 2011 task_events part files (CSV, may be .gz). Columns:
    0 time,1 missing,2 job,3 task,4 machine,5 event,6 user,7 class,8 prio,
    9 cpu request,10 memory request. Uses SUBMIT events (event=0)."""
    import gzip
    rows = []
    seen = set()
    for f in sorted(glob.glob(os.path.join(folder, "*part-*"))):
        with open(f, "rb") as probe: gz = probe.read(2) == b"\x1f\x8b"
        op = gzip.open if gz else open
        with op(f, "rt") as fh:
            for r in csv.reader(fh):
                if len(r) > 10 and r[5] == "0" and r[9] and r[10] and (r[2], r[3]) not in seen:
                    c, m = float(r[9]), float(r[10])
                    if c > 0 and m > 0:
                        seen.add((r[2], r[3])); rows.append((c, m))
        if len(rows) >= n_vm * 3:
            break
    rows = np.array(rows)
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(rows), n_vm, replace=False)
    return rows[idx, 0], rows[idx, 1]


def load_joined(ev_glob, us_glob, n_vm, seed=0, T=12, demand="request"):
    """Join task_events (requests) with task_usage (real 5-minute usage) by (job, task).
    Keeps tasks with at least T usage windows. Returns placement demand and evaluation usage.
    demand='request': place by requests, evaluate on first T windows of real usage.
    demand='usage'  : place by mean usage of first T/2 windows, evaluate on the last T/2 windows."""
    import pandas as pd
    ev = pd.concat([pd.read_csv(f, header=None, usecols=[2, 3, 5, 9, 10], compression="infer") for f in sorted(glob.glob(ev_glob))])
    ev.columns = ["job", "task", "event", "cr", "mr"]
    ev = ev[(ev.event == 0) & ev.cr.notna() & ev.mr.notna() & (ev.cr > 0) & (ev.mr > 0)].drop_duplicates(["job", "task"])
    us = pd.concat([pd.read_csv(f, header=None, usecols=[0, 2, 3, 5, 6], compression="infer") for f in sorted(glob.glob(us_glob))])
    us.columns = ["start", "job", "task", "cpu", "mem"]
    us = us.sort_values("start")
    us["k"] = us.groupby(["job", "task"]).cumcount()
    us = us[us.k < T]
    cnt = us.groupby(["job", "task"]).size()
    keep = cnt[cnt == T].reset_index()[["job", "task"]]
    ev = ev.merge(keep, on=["job", "task"])
    ev = ev.sample(n_vm, random_state=seed)
    us = us.merge(ev[["job", "task"]], on=["job", "task"])
    uc = us.pivot_table(index=["job", "task"], columns="k", values="cpu")
    um = us.pivot_table(index=["job", "task"], columns="k", values="mem")
    ev = ev.set_index(["job", "task"]).loc[uc.index]
    ucpu, umem = uc.to_numpy(), um.to_numpy()
    if demand == "request":
        return ev.cr.to_numpy(), ev.mr.to_numpy(), ucpu, umem
    h = T // 2
    return ucpu[:, :h].mean(1), umem[:, :h].mean(1), ucpu[:, h:], umem[:, h:]

def synthetic_tasks(n_vm, seed=0):
    """FOR CODE TESTING ONLY. Never report results from this generator."""
    rng = np.random.default_rng(seed)
    cpu = np.clip(rng.lognormal(-3.2, 0.7, n_vm), 0.005, 0.5)
    mem = np.clip(0.6 * cpu + rng.lognormal(-3.6, 0.8, n_vm), 0.005, 0.5)
    return cpu, mem

def usage_matrix(cpu, mem, slots=288, seed=1):
    """Per slot utilisation = request * factor. Replace with real task_usage
    data when available (see README)."""
    rng = np.random.default_rng(seed)
    n = len(cpu)
    base = rng.uniform(0.3, 0.9, (n, 1))
    wave = 1 + 0.25 * np.sin(np.linspace(0, 4 * np.pi, slots) + rng.uniform(0, 6.28, (n, 1)))
    noise = rng.normal(1, 0.1, (n, slots))
    f = np.clip(base * wave * noise, 0.05, 1.3)
    return cpu[:, None] * f, mem[:, None] * f

# ---------- models ----------
def pm_loads(assign, cpu, mem, n_pm):
    return (np.bincount(assign, cpu, n_pm), np.bincount(assign, mem, n_pm))

def power(u):  # Eq. 3
    return PMAX - (PMAX - PMIN) / np.exp(ALPHA * u)

def energy_kwh(assign, cpu, n_pm):
    uc = np.bincount(assign, cpu, n_pm)
    act = np.bincount(assign, minlength=n_pm) > 0
    return float(power(np.minimum(uc[act], 1.0)).sum() * HOURS / 1000.0)

def fit_standard(a, cpu, mem, n_pm):
    uc, um = pm_loads(a, cpu, mem, n_pm); act = np.bincount(a, minlength=n_pm) > 0
    return power(uc[act]).sum() + PENALTY * np.maximum(uc - 1, 0).sum()

def fit_paper(a, cpu, mem, n_pm):   # base paper: residual resources, CPU only
    uc, um = pm_loads(a, cpu, mem, n_pm); act = np.bincount(a, minlength=n_pm) > 0
    return (1 - uc[act] ** 2).sum() + PENALTY * np.maximum(uc - 1, 0).sum()

def make_fit_proposed(w=0.5):       # proposed: CPU + memory residual
    def f(a, cpu, mem, n_pm):
        uc, um = pm_loads(a, cpu, mem, n_pm); act = np.bincount(a, minlength=n_pm) > 0
        res = 1 - (w * uc[act] ** 2 + (1 - w) * um[act] ** 2)
        pen = np.maximum(uc - 1, 0).sum() + np.maximum(um - 1, 0).sum()
        return res.sum() + PENALTY * pen
    return f

# ---------- algorithms ----------
def ffd(cpu, mem, n_pm, use_mem=False, key=None):
    order = np.argsort(-(cpu if key is None else key))
    lc, lm = np.zeros(n_pm), np.zeros(n_pm)
    a = np.zeros(len(cpu), dtype=int); used = 0
    for i in order:
        for j in range(used + 1):
            if lc[j] + cpu[i] <= 1 and (not use_mem or lm[j] + mem[i] <= 1):
                a[i] = j; lc[j] += cpu[i]; lm[j] += mem[i]; used = max(used, j + 1); break
    return a

def consolidate(child, cpu, mem, use_mem, rng):
    """Targeted mutation: empty one lightly loaded PM by moving its VMs to other active PMs that fit."""
    n_pm = int(child.max()) + 1
    lc = np.bincount(child, cpu, n_pm); lm = np.bincount(child, mem, n_pm)
    act = np.flatnonzero(np.bincount(child, minlength=n_pm) > 0)
    if len(act) < 2: return child
    load = lc[act] + (lm[act] if use_mem else 0)
    src = rng.choice(act[np.argsort(load)[:5]])
    others = act[act != src]
    moved = {}
    for i in np.flatnonzero(child == src):
        ok = others[(lc[others] + cpu[i] <= 1) & ((lm[others] + mem[i] <= 1) if use_mem else True)]
        if len(ok) == 0: return child  # cannot empty it, keep original
        j = ok[np.argmax(lc[ok])]; lc[j] += cpu[i]; lm[j] += mem[i]; moved[i] = j
    for i, j in moved.items(): child[i] = j
    return child

def ga(cpu, mem, n_pm, fit, seed=0, seed_assign=None, max_gen=MAX_GEN, use_mem=False, p_cons=0.3, extra_seeds=()):
    rng = np.random.default_rng(seed); n = len(cpu)
    base = seed_assign.copy()
    pop = np.tile(base, (POP, 1))
    for k, sd in enumerate(extra_seeds, start=1): pop[k] = sd
    for k in range(1 + len(extra_seeds), POP):  # perturb copies of the FFD seed
        m = rng.random(n) < 0.05
        pop[k, m] = rng.choice(np.unique(base), m.sum())
    t0 = time.perf_counter(); best, stall, g = np.inf, 0, 0; fcalls = 0
    fv = np.array([fit(p, cpu, mem, n_pm) for p in pop]); fcalls += POP
    while g < max_gen and stall < RUNS_STALL:
        new = [pop[fv.argmin()].copy()]  # elitism
        while len(new) < POP:
            par = []
            for _ in range(2):
                t = rng.choice(POP, TOURN, replace=False); par.append(pop[t[fv[t].argmin()]])
            mask = rng.random(n) < CX
            child = np.where(mask, par[0], par[1])
            mm = rng.random(n) < MUT
            if mm.any():
                child[mm] = rng.choice(np.unique(child), mm.sum())
            if rng.random() < p_cons:
                child = consolidate(child, cpu, mem, use_mem, rng)
            new.append(child)
        pop = np.array(new); fv = np.array([fit(p, cpu, mem, n_pm) for p in pop]); fcalls += POP
        cur = fv.min(); g += 1
        if cur < best - 1e-9: best, stall = cur, 0
        else: stall += 1
    return pop[fv.argmin()], dict(gens=g, seconds=time.perf_counter() - t0, fitness_calls=fcalls)

# ---------- evaluation ----------
def sla_violation(assign, ucpu, umem, n_pm):
    """% of (active PM, slot) pairs where CPU or memory demand exceeds capacity."""
    T = ucpu.shape[1]
    lc = np.zeros((n_pm, T)); lm = np.zeros((n_pm, T))
    np.add.at(lc, assign, ucpu); np.add.at(lm, assign, umem)
    act = np.bincount(assign, minlength=n_pm) > 0
    viol = ((lc[act] > 1) | (lm[act] > 1))
    return 100.0 * viol.mean()

def evaluate(name, assign, cpu, mem, n_pm, ucpu, umem, extra):
    uc, um = pm_loads(assign, cpu, mem, n_pm)
    return dict(method=name, energy_kwh=energy_kwh(assign, cpu, n_pm),
                active_pms=int((np.bincount(assign, minlength=n_pm) > 0).sum()),
                sla_violation_pct=sla_violation(assign, ucpu, umem, n_pm),
                cpu_overload_pms=int((uc > 1).sum()), mem_overload_pms=int((um > 1).sum()), **extra)

def run_scale(cpu, mem, n_pm, seed, usage=None):
    ucpu, umem = usage if usage is not None else usage_matrix(cpu, mem, seed=seed + 100)
    res = []
    t = time.perf_counter(); a0 = ffd(cpu, mem, n_pm); dt = time.perf_counter() - t
    res.append(evaluate("FFD (CPU)", a0, cpu, mem, n_pm, ucpu, umem, dict(gens=0, seconds=dt, fitness_calls=0)))
    t = time.perf_counter(); a1 = ffd(cpu, mem, n_pm, True); dt = time.perf_counter() - t
    res.append(evaluate("FFD 2D (CPU+Mem)", a1, cpu, mem, n_pm, ucpu, umem, dict(gens=0, seconds=dt, fitness_calls=0)))
    for name, fit, seed_a, um_flag in [("Standard GA (energy fitness)", fit_standard, a0, False),
                              ("Base-paper GA (CPU residual)", fit_paper, a0, False),
                              ("Proposed GA (CPU+Mem residual)", make_fit_proposed(), a1, True)]:
        xs = ()
        if um_flag:
            xs = [ffd(cpu, mem, n_pm, True, k) for k in (mem, np.maximum(cpu, mem), cpu + mem)]
            fs = [fit(x, cpu, mem, n_pm) for x in [seed_a] + list(xs)]
            seed_a = ([seed_a] + list(xs))[int(np.argmin(fs))]
        a, ex = ga(cpu, mem, n_pm, fit, seed, seed_a, use_mem=um_flag, extra_seeds=xs)
        res.append(evaluate(name, a, cpu, mem, n_pm, ucpu, umem, ex))
    return res

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--events", default=None, help="glob of task_events part files")
    ap.add_argument("--usage", default=None, help="glob of task_usage part files")
    ap.add_argument("--demand", default="request", choices=["request", "usage"])
    ap.add_argument("--synthetic", action="store_true", help="code test only")
    ap.add_argument("--scales", default="small,medium,large")
    ap.add_argument("--runs", type=int, default=10)
    ap.add_argument("--out", default="results.json")
    a = ap.parse_args()
    S = {"small": (1350, 1000), "medium": (2242, 2000), "large": (5365, 3000)}
    out = {}
    for sc in a.scales.split(","):
        n_vm, n_pm = S[sc]; out[sc] = []
        for r in range(a.runs):
            if a.synthetic:
                cpu, mem = synthetic_tasks(n_vm, r); us = None
            else:
                cpu, mem, uc_, um_ = load_joined(a.events, a.usage, n_vm, r, demand=a.demand); us = (uc_, um_)
            out[sc].append(run_scale(cpu, mem, n_pm, r, us))
            print(sc, "run", r + 1, "done", flush=True)
    json.dump(out, open(a.out, "w"), indent=1)
