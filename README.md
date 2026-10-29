# Multi-Resource Accelerated Genetic Algorithm for Energy-Efficient VM Placement in Cloud Data Centers

A Python-based research implementation investigating multi-resource fitness computation for energy-efficient Virtual Machine (VM) placement in cloud data centers.

1. Project Overview

Virtual Machine placement is a fundamental resource-management problem in cloud computing. It involves assigning virtual machines to physical machines while satisfying resource-capacity constraints and managing the energy consumed by active hosts.

Inefficient VM placement can leave physical hosts underutilized, increase the number of active machines, and raise data-center energy consumption. Although Genetic Algorithms (GAs) can explore different placement configurations, their effectiveness depends on the fitness function, initial population, optimization operators, and evaluation methodology.

This repository implements and evaluates a multi-resource accelerated Genetic Algorithm approach inspired by the published research of Hormozi et al. (2022), Energy-Efficient Virtual Machine Placement in Data Centers via Accelerated Genetic Algorithm with Improved Fitness Computation.

The implementation extends the CPU-focused fitness formulation by considering both CPU and memory utilization when evaluating candidate VM placements. It compares the proposed approach with several baseline placement methods using selected workloads derived from Google cluster usage traces.

The experimental findings indicate that the multi-resource approach can improve modeled energy consumption relative to a two-resource First Fit Decreasing baseline in the evaluated workloads. However, it does not consistently outperform CPU-only placement methods, and the genetic algorithm operators did not provide additional measurable gains in the reported ablation experiments.

2. Research Problem

The VM placement problem requires assigning a set of virtual machines to a set of physical hosts while satisfying resource constraints.

Each VM has CPU and memory requirements, and each physical host has finite CPU and memory capacity. A placement strategy must account for both resources to avoid overloaded hosts and inefficient resource allocation.

The main research questions investigated in this implementation are:

- How does including both CPU and memory in the fitness function affect VM placement?
- How does the proposed method compare with CPU-based and two-resource FFD baselines?
- What differences occur in modeled energy consumption and active host count?
- Do crossover, mutation, and consolidation operations provide measurable improvements beyond selecting among different initial placements?
- How sensitive are the observed results to the power-model shape parameter and fitness-function weighting?

3. Research Objectives

The objectives of this implementation are to:

1. Implement multiple VM placement algorithms within a common evaluation framework.
2. Investigate a multi-resource fitness function incorporating CPU and memory utilization.
3. Compare the proposed method with baseline heuristics and Genetic Algorithm variants.
4. Evaluate energy consumption, active host count, execution time, and SLA-related capacity violations.
5. Analyze the contribution of initialization strategies and genetic algorithm operators through ablation experiments.
6. Investigate the sensitivity of the results to selected power-model parameters and fitness weights.

4. Proposed Methodology

4.1 VM Placement Representation

The implementation represents a placement solution by assigning each VM to a physical host. Host utilization is calculated from the resource requirements of the VMs assigned to it.

CPU and memory capacities are normalized to 1. A placement must respect the capacity limits of both resources.

4.2 Multi-Resource Fitness Computation

The proposed fitness function considers both CPU and memory residual resources, rather than evaluating CPU residuals alone.

The implementation also includes a capacity-violation penalty to discourage assignments that exceed the available CPU or memory capacity.

This approach is intended to evaluate candidate placements using information about multiple resources. Its effectiveness is assessed experimentally rather than assumed in advance.

4.3 Initial Population and Genetic Algorithm

The implementation includes multiple initialization strategies based on different First Fit Decreasing orderings. Candidate initial placements are evaluated, and the multi-resource fitness function is used to select promising candidates.

The implementation also includes:

- Tournament selection
- Elitism
- Uniform crossover
- Mutation
- A targeted consolidation procedure
- A stopping condition based on stagnation and a maximum generation limit

Ablation experiments evaluate whether these genetic algorithm operations improve the outcomes beyond the gains obtained through multi-seed initialization and fitness-based selection.

4.4 Energy Evaluation

Energy consumption is estimated using a CPU-utilization-based host power model. The placement of VMs influences energy consumption through the number of active hosts and their CPU utilization.

Memory utilization affects placement feasibility and host activation, but it is not directly used as an input to the power equation.

The reported energy results should therefore be interpreted as estimates under the specified power-model assumptions, not direct measurements from a physical data center.

4.5 SLA-Related Evaluation

The implementation uses requested CPU and memory resources for placement, while measured resource usage is used to calculate an SLA-related capacity-violation metric.

The metric considers measured usage over the first 12 five-minute windows of each task. It serves as a proxy for resource-capacity violations and is not a complete simulation of real-world cloud SLA behavior.

5. Algorithms Implemented

The main implementation file, "vmp.py", includes the following methods:

Algorithm| Description
CPU-based FFD| First Fit Decreasing placement based on CPU requirements
Two-resource FFD| FFD placement considering CPU and memory
Standard GA| A standard Genetic Algorithm baseline
Base-paper GA| An implementation of the baseline approach associated with the original research
Proposed GA| Multi-resource fitness computation with multi-seed initialization and additional optimization operators

The algorithms are evaluated within the same experimental framework to facilitate comparisons across the selected workloads.

6. Dataset

The experiments use selected workloads derived from the publicly available Google cluster usage traces (2011).

Dataset source:

"Google Cluster Data — Official Repository" (https://github.com/google/cluster-data)

The experiment uses data from the "task_events" and "task_usage" tables, including the "part-00000-of-00500" files.

The dataset is not redistributed in this repository. Users must obtain the data from its original source and prepare the required input files before running the experiments.

The reported workloads use sampled tasks that satisfy the study's task-window selection criteria. Results should be interpreted in the context of the selected trace files and sampling procedure.

7. Experimental Configuration

The main experiments evaluate three workload scales.

Scale| Number of VMs| Configured host count
Small| 1,350| 1,000
Medium| 2,242| 2,000
Large| 5,365| 3,000

The reported main experiments use five independent runs for each scale.

Power-Model Assumptions

The reported configuration uses:

- Shape parameter: (\alpha = 3)
- Minimum host power: (P_{\min} = 160) W
- Maximum host power parameter: (P_{\max} = 220) W

These values are experimental assumptions. In particular, the selected value of (\alpha) is not specified in the original base paper and is therefore documented explicitly rather than presented as a parameter copied from that study.

8. Experimental Results

The following results summarize the experiments reported in the accompanying manuscript.

8.1 Energy Consumption

Compared with the two-resource FFD baseline, the proposed approach reduced modeled energy consumption by approximately 3.1–3.7% across the evaluated workload scales.

However, compared with CPU-only methods, the proposed approach consumed approximately 2.4–3.7% more energy.

These findings indicate a trade-off rather than a uniform improvement over every baseline.

8.2 Active Host Count

The proposed approach used approximately 3.4–11.8 fewer active hosts than the two-resource FFD baseline in the reported experiments.

The number of active hosts is an important placement metric because inactive hosts can be switched off under the assumptions of the energy model.

8.3 SLA-Related Capacity Violations

The differences in the SLA-related metric between the proposed approach and the two-resource FFD baseline remained within the observed run-to-run variation.

The results do not establish a consistent SLA advantage over the CPU-only methods. The metric is a proxy based on sampled resource usage and should not be interpreted as a complete assessment of production SLA violations.

8.4 Ablation Experiments

The ablation experiments found that the observed improvements came from selecting among multiple initial placements using the multi-resource fitness function.

Crossover, mutation, and the consolidation procedure did not provide additional measurable gains in the evaluated runs.

This finding is an important limitation and a direction for further algorithmic improvement.

8.5 Sensitivity Analysis

Additional experiments investigated selected power-model shape parameters and fitness-function weights.

The reported energy comparisons against the two-resource FFD baseline remained similar when the placement was evaluated under the tested shape parameters. The tested fitness weights also produced identical placements in the reported small and medium workloads.

8.6 Raw Results and Figures

The repository includes files for the reported experiment outputs and additional analyses:

- "results.json" contains raw per-run results for the main experiments.
- "analyse.py" generates summary statistics and figures from "results.json".
- "results_extra.json" and "analysis_extra.json" support additional analyses.
- "extra.py" and "extra2.py" contain supplementary experiment and analysis functionality.

The exact outputs should be reproduced using the implementation and the corresponding input data.

9. Repository Contents

File| Purpose
"vmp.py"| Data loading, placement algorithms, fitness computation, and evaluation
"analyse.py"| Summary statistics and figure generation from main experiment results
"results.json"| Raw per-run results reported in the manuscript
"extra.py"| Additional experiments, including ablation and sensitivity analysis
"results_extra.json"| Results from additional experiments
"extra2.py"| Workload statistics, host memory distribution, and fitness timing analysis
"analysis_extra.json"| Supporting outputs for supplementary analysis
"requirements.txt"| Python package dependencies

The Google cluster trace files are external inputs and are not included in the repository.

10. Requirements

The project requires Python 3 and the packages listed in "requirements.txt".

Install the dependencies using:

pip install -r requirements.txt

11. Running the Experiments

After obtaining the required Google cluster trace files and preparing the input prefixes expected by the implementation, run:

python vmp.py --events "events-part-" --usage "usage-part-" --scales small,medium,large --runs 5 --out results.json

The command specifies the event-file prefix, usage-file prefix, workload scales, number of independent runs, and output file.

Important: The input prefixes must match the actual locations and naming conventions of the prepared dataset files. Check the argument definitions in "vmp.py" if your file paths differ.

Generating Summary Statistics and Figures

After generating or obtaining the corresponding "results.json", run:

python analyse.py

This script is intended to generate summary statistics and figures from the main experiment results. Additional scripts can be run according to their argument definitions and the available supplementary input files.

12. Reproducibility and Data Availability

The main result files preserve the per-run outputs reported in the manuscript. Additional files support the reported ablation, sensitivity, workload-statistics, and fitness-timing analyses.

Reproducing the complete experiments requires the relevant Google cluster trace files, the required Python dependencies, and the corresponding input paths.

The synthetic-data option is provided for code testing only. Synthetic data was not used for the results reported in the manuscript.

13. Limitations

The findings should be interpreted in light of the following limitations:

- The experiments use selected portions of the Google cluster usage traces rather than the complete dataset.
- The evaluation is based on a custom placement and energy model rather than a full cloud infrastructure simulator.
- The SLA-related metric is a proxy based on measured resource usage and host capacity.
- The energy model uses specified power parameters and does not represent every physical data-center configuration.
- Only five independent runs are used for the main comparisons.
- The genetic algorithm operators did not provide additional measurable gains in the current ablation experiments.
- Additional workloads, broader sensitivity studies, and independent validation are needed to assess generalizability.

14. Future Work

Potential future work includes:

- Evaluating additional workload samples and configurations.
- Investigating alternative multi-resource fitness formulations.
- Improving the contribution of crossover, mutation, and consolidation operators.
- Validating the placement strategy with a cloud simulation framework.
- Extending the evaluation to include VM migration, host activation costs, and other operational factors.
- Assessing the robustness of the results under different power models and resource distributions.

15. Original Research Paper

This implementation builds on the following published research:

Hormozi, E., Hu, S., Ding, Z., Tian, Y.-C., Wang, Y.-G., Yu, Z.-G., & Zhang, W. (2022). Energy-efficient virtual machine placement in data centres via an accelerated Genetic Algorithm with improved fitness computation. Energy, 252, 123884.

Official publisher page:
https://www.sciencedirect.com/science/article/pii/S0360544222007873

DOI:
https://doi.org/10.1016/j.energy.2022.123884

The original paper provides the research foundation for the accelerated Genetic Algorithm and fitness-computation approach. The multi-resource formulation, implementation details, experimental comparisons, and findings documented in this repository should be evaluated according to the accompanying manuscript.

16. Research Manuscript

The associated manuscript describes the problem formulation, methodology, experimental design, results, and limitations of this implementation.

A public manuscript link can be added here once the authors have finalized a shareable version.

17. License

A license should be specified after confirming the intended terms for distributing the implementation. Unless a license is included in the repository, users should not assume that the code is available for unrestricted reuse.

18. Acknowledgment

The experiments use data derived from the publicly available Google cluster usage traces. The original research paper is cited above as the foundation for the research direction and baseline methodology.

