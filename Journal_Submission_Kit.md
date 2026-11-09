# Journal Submission Kit (IEEE Transactions on Cloud Computing)
Do NOT submit before Sir approves. Copy and paste the fields below into the portal.

## 1. Title
Multiresource Accelerated Genetic Algorithm for Energy Efficient VM Placement in Cloud Data Centers

## 2. Abstract
Virtual machine placement strongly affects the energy use of cloud data centres. Genetic algorithms produce good placements but are costly, and recent accelerated variants simplify the fitness function to a residual resource term that looks at CPU only. This paper extends that idea to two resources. We study a multiresource accelerated genetic algorithm with three components: a multi seed initial population built from first fit decreasing variants, a fitness function that combines CPU and memory residual resources with a capacity penalty, and a targeted consolidation mutation. The method is evaluated on samples of the Google cluster usage traces at three scales (1350, 2242 and 5365 virtual machines). Placement uses requested resources, and SLA violations are assessed with measured usage over 5 minute windows, across five independent runs. Against a two resource first fit decreasing baseline, the proposed algorithm lowers energy by 3.1 to 3.7 percent and activates 3.4 to 11.8 fewer hosts, while SLA violations stay within run to run variation. Against CPU only methods it uses 2.4 to 3.7 percent more energy, and its SLA advantage is visible only at the small scale. An ablation study shows that the whole gain comes from selecting among the seeds with the multiresource fitness, while crossover, mutation and consolidation add nothing in any run. The energy saving is unchanged for power model shape constants of 2, 3 and 4.

## 3. Keywords
virtual machine placement, genetic algorithm, energy efficiency, multiresource fitness, SLA violation, cloud data centre

## 4. Authors (in this order)
1. Sumyia Butt, Faculty of Information Technology and Computer Science, University of Central Punjab, Lahore, Pakistan. Email: [YOUR EMAIL]. ORCID: https://orcid.org/0009-0009-2595-0102
2. Muhammad Zulkifl Hasan (CORRESPONDING AUTHOR), Faculty of Information Technology and Computer Science, University of Central Punjab, Lahore, Pakistan. Email: zulkifl.hasan@ucp.edu.pk. ORCID: https://orcid.org/0000-0002-2733-5527
3. Muhammad Zunnurain Hussain, Department of Computer Science, Bahria University Lahore Campus, Lahore, Pakistan. Email: zunnurain.bulc@bahria.edu.pk. ORCID: https://orcid.org/0000-0002-6071-1029

## 5. Publishing option
Choose the traditional (subscription) route. Do NOT choose open access or any option with an APC.

## 6. Declarations
- Funding: This research received no specific funding.
- Conflict of interest: [CONFIRM WITH SIR: The authors declare no conflict of interest.]
- AI declaration: During the preparation of this manuscript, the authors used Claude (Anthropic) to assist with drafting and editing the manuscript text, writing and debugging the code, and preparing figures and tables. The authors reviewed and verified the AI-assisted outputs and take full responsibility for the accuracy and integrity of the final manuscript.
- Data and code availability: GitHub https://github.com/sumyiabutt/vm-placement-genetic-algorithm and Zenodo [DOI TO BE ADDED]. The Google cluster usage traces are publicly available from Google.
- Ethics: Not applicable (public anonymised trace data).

## 7. Files to upload
- Manuscript PDF (final, from Overleaf, 9 pages)
- LaTeX source: main.tex and the figs folder (zipped), if the portal asks
- Cover letter (below)
- Optional: AI Report and Plagiarism Report (MultiresourceGA AI Report.pdf, MultiresourceGA Plagiarism Report.pdf)

## 8. Cover letter
Dear Editor,

Please consider our manuscript, "Multiresource Accelerated Genetic Algorithm for Energy Efficient VM Placement in Cloud Data Centers", for publication in IEEE Transactions on Cloud Computing.

The manuscript studies energy efficient virtual machine placement in cloud data centres. It extends a recent accelerated genetic algorithm that considers CPU only by adding memory as a second resource, and evaluates SLA violations with measured usage from the Google cluster usage traces. We report an ablation and sensitivity study, and we state openly that the energy saving against a two resource first fit decreasing baseline (about 3 to 4 percent) comes from ranking several first fit decreasing seeds with the multiresource fitness, while the evolutionary operators add no improvement.

This work is original, has not been published elsewhere and is not under consideration by any other journal. All authors have approved the submission. Code and result files are publicly available.

Sincerely,
Muhammad Zulkifl Hasan (corresponding author) on behalf of all authors
zulkifl.hasan@ucp.edu.pk

## 9. After submitting
Take a screenshot of the confirmation page (manuscript ID) as proof for Sir.
