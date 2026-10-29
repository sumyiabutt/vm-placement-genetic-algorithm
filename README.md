# vm-placement-genetic-algorithm
# Code for: Multiresource Accelerated Genetic Algorithm for Energy Efficient VM Placement

Files
- vmp.py: loader, algorithms (FFD CPU, FFD 2D, standard GA, base paper GA, proposed GA) and evaluation
- analyse.py: builds summary statistics and figures from results.json
- results.json: raw per run results reported in the paper (5 runs, three scales)
- extra.py, results_extra.json: ablation, shape constant and fitness weight sensitivity (small and medium scale, 5 runs)
- extra2.py, analysis_extra.json: workload statistics, host memory distribution figure and fitness evaluation timing

Data (not redistributed): Google cluster usage traces 2011, part-00000-of-00500 of task_events and task_usage
(https://github.com/google/cluster-data).

Run
    pip install -r requirements.txt
    python vmp.py --events "events-part-*" --usage "usage-part-*" --scales small,medium,large --runs 5 --out results.json

Notes
- Placement uses requested CPU and memory; SLA violation uses measured usage over the first 12 five minute windows of each task.
- Alpha = 3, Pmin = 160 W, Pmax = 220 W are assumptions (alpha is not given in the base paper).
- The synthetic option exists for code testing only and was not used for any reported result.

