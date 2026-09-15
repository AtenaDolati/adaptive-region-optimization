# ARRGO

## Adaptive Region Refinement for Global Optimization

ARRGO is a deterministic, region-based framework for bounded global optimization.

The framework partitions the search domain into regions, evaluates the objective function, analyzes regional behavior, and adaptively refines informative regions through sampling and structural splitting.

ARRGO treats the objective function as a black-box evaluator and does not require analytical derivatives.

---

## Overview

Global optimization aims to find the best solution over a bounded search domain, where the objective function may contain multiple local optima, narrow peaks, flat regions, or other challenging structures.

ARRGO approaches this problem through adaptive region refinement.

The main optimization cycle is:

Domain
↓
Initial Sampling
↓
Region Analysis
↓
Candidate Generation
↓
Global Region Selection
↓
Sampling / Splitting
↓
State Update
↓
Certified Bounds / Global Relevance
↓
Termination
↺

The central idea is to combine:

- Information refinement through objective evaluations
- Spatial refinement through region splitting
- Regional behavior analysis
- Global selection of informative regions
- Explicit termination conditions

---

## Key Features

- Deterministic global optimization framework
- Bounded search domains
- Region-based search
- Adaptive refinement
- Information-driven sampling
- Structural region splitting
- Regional behavior analysis
- Global incumbent tracking
- Hierarchical region representation
- Optional Lipschitz-based certification
- Explicit convergence conditions
- Numerical robustness
- Finite-dimensional theoretical generalization

---

## Algorithm

At each iteration, ARRGO performs the following high-level process:

1. Maintain regions covering the search domain.
2. Evaluate the objective function at selected points.
3. Update the global incumbent.
4. Analyze the current regions.
5. Generate feasible refinement actions.
6. Select an informative region and action.
7. Refine the region through sampling or splitting.
8. Update the global and regional state.
9. Evaluate certified bounds when certification is enabled.
10. Check termination conditions.
11. Continue the refinement process.

Sampling consumes objective evaluations, while structural splitting changes the spatial representation without directly consuming an objective evaluation.

ARRGO does not remove refined parent regions from its hierarchy. Parent regions remain represented while their child regions provide finer spatial resolution.

---

## Theoretical Foundations

ARRGO is supported by a theoretical framework that connects spatial refinement, information acquisition, regional resolution, and global convergence.

The analysis considers bounded optimization problems under explicit assumptions such as:

- A compact search domain
- Continuity of the objective function
- Valid region refinement
- Spatial contraction
- Sufficient information acquisition
- Fair global region selection

Under these assumptions, the refinement process can progressively improve the resolution of the search space and the information available about the objective function.

The convergence results are conditional on these assumptions. They do not claim universal convergence for arbitrary black-box functions without sufficient information or regularity assumptions.

---

## Certified Mode

ARRGO can optionally use Lipschitz-based bounds when a valid Lipschitz constant is known.

For a region R and evaluated points inside that region, ARRGO constructs lower and upper envelopes based on the Lipschitz condition.

The lower envelope is defined conceptually as:

L_R(x) = max_i [ f(x_i) - L ||x - x_i|| ]

The upper envelope is defined as:

U_R(x) = min_i [ f(x_i) + L ||x - x_i|| ]

These envelopes provide bounds on the possible objective value inside a region under the assumed Lipschitz constant.

A regional potential can then be used to estimate the maximum objective value that may still be achievable within a region.

The global certification process operates over a certification frontier covering the search domain.

The global optimality gap is defined as the difference between the global potential and the best evaluated objective value.

When the required assumptions hold and the global gap becomes sufficiently small, ARRGO can provide an epsilon-optimality certificate.

If the evaluation budget is exhausted before certification is achieved, the returned solution is interpreted as the best-found solution rather than as a universally certified global optimum.


---

## Implementation

The current ARRGO implementation is written in Python and organized as a modular package.

The implementation is located under:

src/arrgo/

The core architecture contains components for:

- Objective evaluation
- Numerical utilities
- Evaluation history
- Region representation
- Region analysis
- Candidate generation
- Refinement action selection
- Global region selection
- Certified bounds
- Termination
- ARRGO execution

The implementation currently targets bounded one-dimensional optimization.

---

## Validation

The implementation is supported by a dedicated validation notebook covering the main components and execution paths.

The validation includes:

- Numerical utilities
- Configuration validation
- Evaluation history
- Region representation
- Region hierarchy
- Region analysis
- Sampling candidates
- Split candidates
- Refinement decisions
- Global region selection
- Region splitting
- Sampling execution
- Global incumbent updates
- Certified bounds
- Termination conditions
- Deterministic execution
- Empirical end-to-end execution
- Certified end-to-end execution
- Numerical robustness

The validation focuses on implementation consistency and correctness. It is not intended to establish universal optimization superiority over other algorithms.


---

## Experimental Evaluation

ARRGO was evaluated on a fixed suite of five one-dimensional benchmark functions designed to represent different objective landscapes.

The benchmark suite includes:

- Quadratic objective
- Asymmetric smooth objective
- Multimodal objective
- Narrow peak objective
- Flat peak objective

The experiments used a maximum budget of 100 objective evaluations for each benchmark.

The experimental configuration used a contraction factor of 0.75, with initial sampling included in the evaluation budget.

The results show that ARRGO can identify high-quality solutions across different landscape structures, including multimodal and narrow-peak objectives.

For example, on the multimodal benchmark, ARRGO reached a solution with an objective value very close to the independently computed reference value.

On the narrow-peak benchmark, ARRGO identified the optimum with very high numerical accuracy.

The flat-peak benchmark also demonstrates that ARRGO can handle non-unique optima, where multiple points in the domain have the same optimal objective value.

The experimental results are empirical observations under the specified benchmark functions and configuration. They are not used to claim universal optimization performance.

---

## Comparative Evaluation

ARRGO was compared with five baseline optimization methods:

- Random Search
- Hill Climbing
- Genetic Algorithm
- Simulated Annealing
- SHGO

The comparison used 300 deterministic randomly generated one-dimensional benchmark functions.

All methods were evaluated under the same objective functions, search domains, and maximum budget of 100 objective evaluations.

The comparison considered:

- Final objective-value quality
- Normalized value error
- Location error
- Success rate
- Convergence behavior

Reference solutions were computed independently using a much finer numerical search followed by local numerical refinement.

The reference solutions are numerical approximations and should not be interpreted as mathematically exact global optima.

### Comparative Results

Under the benchmark generator and algorithm configurations used in the study, SHGO achieved the strongest overall performance.

Random Search also performed strongly on this benchmark family.

ARRGO showed competitive performance, with a mean normalized value error of approximately 6.31% and a success rate of approximately 46.7% under the selected success criterion.

ARRGO was competitive with the Genetic Algorithm and achieved lower mean normalized value error than Simulated Annealing and Hill Climbing.

ARRGO also showed relatively strong early improvement during the evaluation budget, although its average performance later plateaued compared with stronger baselines.

The benchmark-wise comparison showed that SHGO achieved the best final normalized value error on all 300 evaluated benchmark functions under the exact comparison criterion used in this study. ARRGO achieved the best result on 15 of the 300 benchmarks.

These results are specific to the benchmark generator, evaluation budget, reference-solution procedure, and algorithm configurations used in this experiment.

They should not be interpreted as a universal ranking of global optimization algorithms or as evidence that ARRGO is universally superior or inferior to the evaluated baselines.


---

## Dimensional Generalization

The mathematical framework of ARRGO is generalized from one-dimensional intervals to bounded hyperrectangles in finite-dimensional spaces.

For a d-dimensional optimization domain, the search space can be represented as a bounded hyperrectangle.

The theoretical formulation extends the main concepts of ARRGO to higher dimensions, including:

- Spatial coverage
- Region representation
- Sampling
- Structural splitting
- Region selection
- Information acquisition
- Certified bounds
- Refinement
- Convergence conditions

The generalized formulation preserves the central principles of the one-dimensional framework while allowing regions to be represented as multidimensional hyperrectangles.

This generalization is theoretical only.

The current software implementation and experimental evaluation remain one-dimensional.

No claim of high-dimensional scalability or empirical performance is made.

---

## Research Scope

ARRGO is presented as a research-oriented optimization framework rather than as a claim of universal superiority over existing optimization algorithms.

The main contribution of the project consists of:

1. A deterministic region-based framework for bounded global optimization.
2. An adaptive refinement mechanism combining sampling and structural splitting.
3. Explicit regional and global state representations.
4. A certification-oriented formulation based on valid Lipschitz bounds.
5. A theoretical convergence framework under explicit assumptions.
6. A finite-dimensional mathematical generalization.
7. Empirical validation and comparative evaluation on one-dimensional benchmarks.

The current implementation does not claim:

- Universal superiority over established optimizers
- High-dimensional empirical scalability
- Certification without the assumptions required by the theoretical analysis
- Exact global-optimum identification for arbitrary black-box functions under a finite evaluation budget

---

## Limitations

The current study has several limitations:

- The implementation is currently one-dimensional.
- The comparative evaluation uses a specific synthetic benchmark family.
- Reference solutions are numerical approximations rather than exact global optima.
- Stochastic baselines use fixed seeded runs rather than statistical distributions over many independent trials.
- Algorithm parameters were not exhaustively tuned for every method.
- High-dimensional scalability was not experimentally evaluated.
- Certified convergence requires a valid Lipschitz constant and the assumptions stated in the theoretical analysis.

These limitations define the scope of the conclusions presented in this repository.


---

## Repository Structure

The repository is organized as follows:

adaptive-region-optimization/

├── src/
│   └── arrgo/

├── notebooks/
│   ├── 01_problem_definition.ipynb
│   ├── 02_theoretical_foundations.ipynb
│   ├── 03_arrgo_algorithm_design.ipynb
│   ├── 04_arrgo_core_implementation.ipynb
│   ├── 05_testing_and_validation.ipynb
│   ├── 06_experimental_evaluation.ipynb
│   ├── 07_dimensional_generalization.ipynb
│   └── 08_comparative_evaluation.ipynb

├── README.md
├── .gitignore
└── ...

---

## Notebook Guide

The notebooks are organized as a progression from problem definition to theory, implementation, validation, and experimentation.

### 01 — Problem Definition

Defines the optimization problem, regions, information, refinement, uncertainty, global state, hierarchy, termination, and contraction concepts.

### 02 — Theoretical Foundations

Develops the mathematical assumptions, regularity conditions, regional bounds, convergence conditions, and certification framework.

### 03 — Algorithm Design

Defines the ARRGO algorithm, including region analysis, candidate generation, sampling, splitting, global selection, state transitions, and termination.

### 04 — Core Implementation

Implements the ARRGO framework as a modular Python package.

### 05 — Testing and Validation

Validates the main implementation components and execution paths.

### 06 — Experimental Evaluation

Evaluates ARRGO on a fixed suite of one-dimensional benchmark functions.

### 07 — Dimensional Generalization

Provides the theoretical extension of ARRGO from one-dimensional intervals to finite-dimensional hyperrectangles.

### 08 — Comparative Evaluation

Compares ARRGO with Random Search, Hill Climbing, Genetic Algorithm, Simulated Annealing, and SHGO on 300 randomly generated one-dimensional benchmark functions.

---

## Reproducibility

The experimental studies use fixed random seeds where stochastic behavior is involved.

The comparative evaluation uses a fixed master seed for benchmark generation and deterministic per-benchmark seeds for stochastic optimization methods.

The experiments are therefore reproducible under the same software environment, dependency versions, algorithm configurations, and numerical settings.

---

## Status

Research prototype — one-dimensional implementation with theoretical finite-dimensional generalization.

The repository contains the complete algorithm design, theoretical analysis, implementation, validation, experimental evaluation, comparative evaluation, and dimensional generalization developed in this study.
