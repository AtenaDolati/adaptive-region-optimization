# ARRGO

## Adaptive Region Refinement for Global Optimization

ARRGO is a deterministic, region-based framework for bounded global optimization that adaptively refines the search space through objective evaluation, regional analysis, sampling, and structural splitting.

---

## Overview

Global optimization aims to identify the best solution within a bounded search domain, where the objective function may contain multiple local optima, narrow peaks, flat regions, or other challenging landscape structures.

ARRGO addresses this problem by maintaining a hierarchy of regions covering the search domain and progressively refining regions that remain informative for the global search.

The framework treats the objective function as a black-box evaluator and does not require analytical derivatives.

The central principle of ARRGO is to combine:

- Information refinement through objective evaluations
- Spatial refinement through region splitting
- Regional behavior analysis
- Global selection of informative regions
- Explicit state transitions and termination conditions

---

---

## Problem

ARRGO addresses bounded global optimization problems in which the goal is to find the best value of an objective function within a specified search domain.

$$
\max_{x \in [l,r]} f(x)
$$

The objective function is treated as a black-box evaluator. ARRGO does not require access to analytical derivatives or an explicit mathematical form of the objective function.

The current implementation focuses on one-dimensional bounded optimization problems.

The theoretical framework is additionally generalized to bounded finite-dimensional search spaces.

---

## Motivation

Many optimization methods focus primarily on generating better candidate points.

ARRGO instead treats the search domain itself as an evolving object.

The algorithm maintains explicit regions and uses information collected from evaluated points to determine where additional resolution is useful.

This leads to two complementary forms of refinement:

- **Information refinement:** obtaining new objective evaluations
- **Structural refinement:** subdividing regions to increase spatial resolution

This separation allows ARRGO to reason about both what is known about the objective function and where the search space still requires refinement.

---

## Key Idea

ARRGO maintains a hierarchical representation of the search domain.

Each region can contain evaluated points and associated objective values. Regional information is analyzed to determine whether a region remains unresolved, stable, or requires further refinement.

The algorithm generates feasible refinement actions and selects informative regions globally.

A refinement action can either:

1. Sample a new point inside a region.
2. Split a region into smaller child regions.

The process continues until a termination condition is satisfied or the available evaluation budget is exhausted.

---

---

## Key Features

- Deterministic global optimization framework
- Bounded-domain optimization
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

## Main Contributions

The project develops the following components:

1. A deterministic region-based framework for bounded global optimization.
2. An adaptive refinement mechanism combining sampling and structural splitting.
3. Explicit regional and global state representations.
4. A hierarchical representation of the search domain.
5. A certification-oriented formulation based on valid Lipschitz bounds.
6. A theoretical convergence framework under explicit assumptions.
7. A finite-dimensional mathematical generalization.
8. A modular Python implementation with dedicated validation.
9. Empirical evaluation on representative one-dimensional benchmark functions.
10. Comparative evaluation against several global optimization baselines.

---

---

## Algorithm

ARRGO follows an adaptive refinement process in which the search domain is represented by a hierarchy of regions.

At each iteration, the algorithm analyzes the available information, identifies unresolved regions, generates feasible refinement actions, and selects the most informative action according to the current search state.

The main stages of the algorithm are described below.

### Optimization Problem

The current implementation considers bounded one-dimensional global optimization problems.

The objective function is treated as a black-box evaluator. The algorithm only requires the ability to evaluate the objective at selected points within the search domain.

### Region Representation

The search domain is represented as a collection of regions.

Each region maintains its spatial boundaries, evaluated points, objective values, regional state, and hierarchical relationships with other regions.

Regions can be classified according to their current state, including:

- **ACTIVE:** the region may still contain useful unresolved information.
- **STABLE:** the available information indicates that further local refinement is currently unnecessary.
- **REFINED:** the region has been structurally divided into smaller regions.

Parent regions remain part of the hierarchy after refinement.

### Sampling

Sampling adds new objective evaluations to the search process.

ARRGO generates candidate points inside informative regions and evaluates the objective function at selected candidates.

Sampling is used to improve the information available about the objective landscape without necessarily changing the structural representation of the search space.

### Region Analysis

Each region is analyzed using the information available from its evaluated points.

The analysis considers factors such as:

- Local objective behavior
- Spatial coverage
- Uncertainty
- Potential for improvement
- Resolution
- Stability
- Unresolved behavior

The resulting regional information is used to determine which refinement actions remain relevant.

### Candidate Generation

ARRGO generates feasible candidate actions for unresolved regions.

Candidate actions may correspond to:

- Sampling a new point
- Splitting a region
- Refining the region according to its current information state

Candidates are evaluated using the available regional information before an action is selected.

### Region Splitting

Structural refinement divides a region into smaller child regions.

Splitting increases spatial resolution and allows the algorithm to investigate different parts of the search domain more precisely.

The implementation uses binary splitting for the current one-dimensional problem.

The splitting mechanism also respects the configured spatial contraction requirement.

### Global Region Selection

After regional analysis, ARRGO selects regions globally rather than processing regions independently.

The selection mechanism prioritizes regions that remain relevant to the global optimization objective.

This prevents the search from becoming restricted to a single locally promising region.

### Refinement

Refinement is the central operation of ARRGO.

At each iteration, the algorithm determines whether the selected region should be sampled or structurally split.

The selected action is executed, the global state is updated, and the resulting information is incorporated into subsequent iterations.

The refinement cycle can therefore be summarized as:

1. Analyze the current search state.
2. Identify unresolved regions.
3. Generate feasible refinement actions.
4. Select the globally relevant region.
5. Select an appropriate refinement action.
6. Execute sampling or splitting.
7. Update regional and global information.
8. Check termination conditions.

### Termination

The algorithm terminates when a defined stopping condition is satisfied.

Depending on the execution mode, termination may be caused by:

- Reaching the available evaluation budget
- Satisfying the required optimization tolerance
- Satisfying a certified global optimality gap
- Detecting that no valid refinement action remains

When the evaluation budget is exhausted, ARRGO reports the best solution found within the available evaluations rather than claiming exact global optimality.

---

---

## Theoretical Foundations

ARRGO is supported by a theoretical framework that describes the conditions under which adaptive regional refinement can provide global convergence.

The theoretical analysis separates the optimization process into three complementary components:

- Spatial contraction of the search regions
- Progressive acquisition of objective information
- Fair global selection of unresolved regions

The convergence results are conditional on explicit mathematical assumptions and do not claim unconditional global optimality for arbitrary black-box functions.

### Assumptions

The theoretical framework considers a bounded search domain and assumes appropriate regularity of the objective function.

The main assumptions include:

- The search domain is compact.
- The objective function is continuous on the search domain.
- Refinement produces progressively smaller regions.
- Relevant regions continue to receive sufficient information.
- Global region selection remains fair with respect to unresolved regions.
- Numerical operations remain sufficiently stable.
- For certified optimization, a valid Lipschitz constant is available.

These assumptions define the conditions under which the theoretical convergence arguments apply.

### Spatial Contraction

ARRGO requires structural refinement to increase spatial resolution.

When a region is split, its child regions must satisfy the configured contraction requirement.

$$
\max(s-l,r-s)\leq\rho(r-l),
\qquad 0<\rho<1
$$

Repeated refinement therefore produces regions with progressively smaller spatial extent.

Spatial contraction is the structural mechanism that allows ARRGO to resolve increasingly localized parts of the search domain.

### Information Acquisition

Spatial refinement alone is not sufficient for global optimization.

ARRGO also requires progressive acquisition of objective information in regions that remain relevant to the global search.

As additional evaluations are obtained, the algorithm improves its knowledge of the objective landscape and can distinguish between promising and sufficiently resolved regions.

The theoretical framework therefore treats spatial refinement and information acquisition as complementary requirements.

### Global Convergence

Under the stated assumptions, if relevant regions are progressively refined and sufficient objective information is acquired throughout the search domain, the best-found objective value approaches the global optimum.

The convergence argument is based on the interaction between:

1. Spatial contraction
2. Information acquisition
3. Fair global region selection
4. Continuous objective behavior

The result is conditional: it establishes convergence under the required assumptions rather than guaranteeing global optimality for every possible black-box objective.

### Certified Mode

ARRGO also provides a certification-oriented mode based on Lipschitz bounds.

When a valid Lipschitz constant is known, evaluated points can be used to construct lower and upper bounds on the objective function within a region.

$$
L_R(x)=\max_i\left[f(x_i)-L|x-x_i|\right]
$$

$$
U_R(x)=\min_i\left[f(x_i)+L|x-x_i|\right]
$$

These bounds provide a principled estimate of the remaining optimization uncertainty.

A global certification gap can then be used as a termination criterion.

$$
\Delta_{\mathrm{global}}
=
P_{\mathrm{global}}-f_{\mathrm{best}}
$$

If the certification conditions are satisfied and the global gap falls below the specified tolerance, the current incumbent can be considered epsilon-optimal under the assumed Lipschitz model.

The certification mechanism therefore provides a stronger termination statement than simple budget exhaustion.

---

---

## Implementation

ARRGO is implemented as a modular Python framework.

The implementation separates objective evaluation, numerical utilities, evaluation history, region representation, regional analysis, candidate generation, refinement action selection, global region selection, certified bounds, termination, and algorithm execution.

### Technology Stack

- **Python**
- **NumPy**
- **SciPy**
- **Jupyter Notebook**
- **Matplotlib**
- **Git / GitHub**

The implementation is organized to keep the optimization logic independent from the experimental and theoretical documentation.

### Architecture

The core implementation is divided into the following conceptual components:

1. **Objective Evaluation**  
   Handles objective-function evaluation and numerical validation.

2. **Numerical Utilities**  
   Provides numerical validation and robustness utilities.

3. **Evaluation History**  
   Maintains the evaluated points and their objective values.

4. **Region Representation**  
   Represents search regions and their hierarchical relationships.

5. **Region Analysis**  
   Extracts regional information from evaluated points.

6. **Candidate Generation**  
   Generates feasible sampling and splitting candidates.

7. **Refinement Action Selection**  
   Selects the refinement action for the currently selected region.

8. **Global Region Selection**  
   Determines which region is globally relevant for further refinement.

9. **Certified Bounds**  
   Provides Lipschitz-based regional bounds and global certification information when a valid Lipschitz constant is available.

10. **Termination**  
    Handles budget-based and tolerance-based stopping conditions.

11. **ARRGO Execution**  
    Integrates the complete optimization pipeline into an executable algorithm.

### Current Scope

The current software implementation targets one-dimensional bounded global optimization.

The implementation uses a hierarchical binary region structure and supports both empirical and certification-oriented execution modes.

The dimensional generalization presented in this project is theoretical and mathematical only.

No higher-dimensional implementation or scalability claim is made.

The experimental studies therefore focus exclusively on one-dimensional optimization problems.

---

---

## Experimental Evaluation

The experimental evaluation investigates the behavior of ARRGO on a collection of representative one-dimensional global optimization problems.

The experiments are designed to evaluate whether the implemented framework can identify high-quality solutions across different objective landscapes while respecting a fixed evaluation budget.

### Benchmark Suite

The benchmark suite contains five one-dimensional objective functions representing different optimization characteristics:

1. **Quadratic Function**  
   A smooth unimodal objective with a single well-defined optimum.

2. **Asymmetric Smooth Function**  
   A smooth asymmetric objective used to evaluate behavior on a non-symmetric landscape.

3. **Multimodal Function**  
   An objective containing multiple local optima, requiring the algorithm to distinguish globally promising regions from competing local structures.

4. **Narrow Peak Function**  
   An objective with a highly localized optimum, testing the ability of adaptive refinement to increase resolution around narrow promising regions.

5. **Flat Peak Function**  
   An objective containing a non-unique optimum, testing the behavior of ARRGO when multiple points share the optimal objective value.

### Experimental Setup

The experiments use the following configuration:

- One-dimensional bounded search domains
- Deterministic ARRGO execution
- Maximum of 100 objective evaluations per benchmark
- Contraction factor of 0.75
- Empirical execution mode
- Initial evaluations included in the evaluation budget
- Fixed benchmark definitions
- Numerical reference solutions for error analysis

The evaluation budget is counted in terms of objective-function evaluations.

Structural region splitting does not consume an objective evaluation.

### Results

ARRGO successfully identified solutions close to the reference optima across all five benchmark functions.

The obtained results include:

| Benchmark | Best Value | Best Location | Value Error | Location Error |
|---|---:|---:|---:|---:|
| Quadratic | 4.999939 | 2.007779 | 6.05e-05 | 7.78e-03 |
| Asymmetric Smooth | 3.999990 | 0.803112 | 9.69e-06 | 3.11e-03 |
| Multimodal | 0.920212 | 0.776076 | 3.78e-08 | 5.91e-05 |
| Narrow Peak | 1.000000 | 1.500000 | 1.78e-15 | 1.21e-08 |
| Flat Peak | 0.000000 | 0.000000 | 0.00e+00 | Non-unique |

All five experiments used the full evaluation budget.

The narrow-peak benchmark demonstrates that ARRGO can concentrate refinement around a highly localized optimum, while the flat-peak benchmark illustrates that the algorithm can return one of multiple valid optimal locations.

### Observations

The experiments demonstrate several qualitative properties of the implementation:

- The global incumbent improves monotonically during optimization.
- ARRGO can refine different regions at different spatial resolutions.
- Narrow and highly localized structures receive substantially deeper refinement.
- Multimodal landscapes can be explored while maintaining a global region hierarchy.
- The algorithm remains deterministic under the same configuration and objective.
- Budget exhaustion is reported explicitly rather than being interpreted as a proof of global optimality.

These experiments provide empirical evidence about the behavior of the implementation but do not establish universal superiority over other optimization methods.

---

---

## Comparative Evaluation

ARRGO was empirically compared with several established optimization methods on a larger collection of synthetic one-dimensional benchmark functions.

The purpose of this experiment is not to claim universal superiority, but to evaluate the practical behavior of ARRGO under a common experimental protocol.

### Baselines

ARRGO was compared against:

- **Random Search**
- **Hill Climbing**
- **Genetic Algorithm**
- **Simulated Annealing**
- **SHGO**

A* was not included because it is primarily a graph and pathfinding algorithm rather than a continuous global optimization method.

### Experimental Protocol

The comparative study uses 300 deterministic randomly generated one-dimensional benchmark functions.

Each benchmark is defined over the same bounded domain and evaluated under a fixed objective-function evaluation budget.

The main experimental conditions are:

- 300 benchmark functions
- One-dimensional search domain
- Domain of [-5, 5]
- 100 objective evaluations per method
- Identical benchmark functions for all methods
- Fixed master seed for benchmark generation
- Fixed seeds for stochastic optimization methods
- Method-specific algorithm parameters
- Numerically computed reference solutions for error analysis

The benchmark functions are generated from smooth Gaussian-mixture landscapes with varying numbers of components, locations, widths, amplitudes, and small linear trends.

Reference solutions are computed using a substantially finer numerical search followed by local numerical refinement.

These reference solutions are numerical approximations and are not treated as exact proofs of global optimality.

### Evaluation Metrics

The methods are evaluated using several complementary metrics:

- Best objective value
- Absolute value error
- Normalized value error
- Location error
- Success rate
- Evaluation efficiency
- Convergence behavior
- Benchmark-wise performance

Using multiple metrics avoids relying on a single aggregate measure and provides a more complete view of optimization behavior.

### Results

Under the experimental configuration, SHGO achieved the strongest overall performance across the selected benchmark family.

Its mean normalized value error was effectively zero, and it achieved the best final error on all 300 benchmark functions.

Random Search also performed strongly, achieving a substantially lower mean normalized value error than ARRGO under the same evaluation budget.

ARRGO achieved a mean normalized value error of approximately 6.31% and a success rate of approximately 46.7%.

For comparison:

| Method | Mean Normalized Value Error | Success Rate |
|---|---:|---:|
| SHGO | ~0.00% | 100.0% |
| Random Search | 0.78% | 84.0% |
| Genetic Algorithm | 6.05% | 67.3% |
| ARRGO | 6.31% | 46.7% |
| Simulated Annealing | 14.13% | 65.3% |
| Hill Climbing | 28.53% | 48.7% |

ARRGO achieved the best final result on 15 of the 300 benchmark functions.

The convergence analysis also showed that ARRGO improved substantially during the early evaluation stages, followed by a tendency to plateau under the fixed 100-evaluation budget.

### Discussion

The comparative results show that ARRGO is competitive on the selected benchmark family but does not outperform the strongest baseline.

In particular, SHGO provides substantially stronger performance under the configuration used in this study, while Random Search also performs surprisingly well on the generated smooth benchmark family.

ARRGO performs better than Simulated Annealing and Hill Climbing in mean normalized value error, while remaining close to the Genetic Algorithm in this metric.

The results should not be interpreted as evidence that one algorithm is universally superior.

The experiment uses a specific synthetic benchmark family, a fixed evaluation budget, one seeded run for each stochastic method and benchmark, and method-specific configurations that were not exhaustively tuned.

Therefore, the comparative evaluation is best interpreted as an empirical characterization of ARRGO rather than a universal ranking of global optimization algorithms.

---

---

## Dimensional Generalization

Although the current implementation is limited to one-dimensional optimization, the theoretical framework of ARRGO is generalized to bounded finite-dimensional search spaces.

In the generalized formulation, the search domain is represented as a bounded hyperrectangle in a finite-dimensional space.

The main concepts of the one-dimensional framework are preserved:

- Objective evaluation
- Region representation
- Hierarchical decomposition
- Spatial coverage
- Adaptive refinement
- Information acquisition
- Global region selection
- Certified bounds
- Termination conditions
- Global convergence conditions

In higher dimensions, regions become hyperrectangles and structural refinement can be performed along selected coordinate directions.

The theoretical analysis establishes the conditions required for spatial contraction and sufficient information acquisition in finite-dimensional domains.

The generalized convergence framework remains conditional on assumptions such as compactness, continuity, valid refinement, sufficient information acquisition, and fair global region selection.

The dimensional generalization is theoretical only.

No higher-dimensional implementation or empirical scalability study is included in the current project.

Therefore, the experimental results and software implementation should be interpreted strictly as one-dimensional results, while the finite-dimensional formulation represents the theoretical extension of the framework.

----

---

## Repository Structure

The repository is organized to separate theoretical development, implementation, experimentation, and documentation.

```text
adaptive-region-optimization/
│
├── notebooks/
│   ├── 01_problem_definition.ipynb
│   ├── 02_theoretical_foundations.ipynb
│   ├── 03_arrgo_algorithm_design.ipynb
│   ├── 04_arrgo_core_implementation.ipynb
│   ├── 05_testing_and_validation.ipynb
│   ├── 06_experimental_evaluation.ipynb
│   ├── 07_dimensional_generalization.ipynb
│   └── 08_comparative_evaluation.ipynb
│
├── src/
│   └── arrgo/
│       ├── __init__.py
│       ├── core/
│       ├── evaluation/
│       ├── regions/
│       ├── refinement/
│       ├── selection/
│       ├── certification/
│       └── termination/
│
├── README.md
│
└── pyproject.toml
```


### Directory Overview

- **`notebooks/`**  
  Contains the theoretical development, algorithm design, implementation walkthrough, validation, experimental studies, and comparative evaluation.

- **`src/arrgo/`**  
  Contains the modular Python implementation of the ARRGO framework.

- **`README.md`**  
  Provides an overview of the project, its methodology, theoretical foundations, implementation, and experimental findings.

- **`pyproject.toml`**  
  Defines the Python project configuration and dependencies.

The repository structure is designed to keep the research narrative in the notebooks while maintaining a reusable implementation in the source package.

---

## Notebook Guide

The project is organized as a sequence of notebooks, with each notebook covering a specific stage of the ARRGO research and development process.

### 01 — Problem Definition

Defines the global optimization problem, search regions, evaluation information, refinement concepts, uncertainty, potential, region lifecycle, and the formal problem structure used throughout the project.

### 02 — Theoretical Foundations

Develops the mathematical foundations of ARRGO, including the main assumptions, spatial contraction, information acquisition, optimization potential, global convergence, epsilon-optimality, and certified convergence.

### 03 — Algorithm Design

Presents the complete ARRGO algorithm design, including region analysis, candidate generation, sampling, splitting, global region selection, refinement decisions, state transitions, termination, and the overall execution cycle.

### 04 — Core Implementation

Implements the ARRGO framework as a modular Python system, covering objective evaluation, evaluation history, region representation, candidate generation, refinement actions, global selection, certified bounds, termination, and algorithm execution.

### 05 — Testing and Validation

Validates the implementation through component-level tests, integration tests, deterministic behavior checks, numerical robustness tests, and end-to-end execution in both empirical and certified modes.

### 06 — Experimental Evaluation

Evaluates ARRGO on five representative one-dimensional benchmark functions, covering unimodal, asymmetric, multimodal, narrow-peak, and flat-peak objective landscapes.

### 07 — Dimensional Generalization

Extends the mathematical formulation of ARRGO from one-dimensional intervals to bounded finite-dimensional hyperrectangular domains and develops the corresponding theoretical convergence framework.

### 08 — Comparative Evaluation

Compares ARRGO with Random Search, Hill Climbing, Genetic Algorithm, Simulated Annealing, and SHGO on 300 deterministic randomly generated one-dimensional benchmark functions under a common evaluation budget.

---

---

## Reproducibility

ARRGO is designed to support reproducible research and experimentation.

The repository contains the theoretical development, algorithm design, implementation, validation, benchmark definitions, and experimental evaluations used throughout the project.

Reproducibility is supported through:

- Fixed benchmark definitions
- Deterministic ARRGO execution
- Fixed evaluation budgets
- Fixed random seeds for stochastic comparative methods
- Explicit experimental configurations
- Numerical reference solutions for comparative evaluation
- Dedicated validation and testing procedures

The experimental notebooks document the configurations, evaluation procedures, benchmark functions, and metrics used to obtain the reported results.

The comparative evaluation additionally uses a fixed master seed for benchmark generation, ensuring that the same collection of synthetic benchmark functions can be regenerated under the same configuration.

Results may exhibit small numerical differences across environments due to floating-point arithmetic and numerical optimization behavior.

---

---

## Limitations

The current version of ARRGO has several limitations that define the scope of the presented results.

- The software implementation is limited to one-dimensional bounded optimization.
- The finite-dimensional generalization is theoretical and has not been implemented or empirically evaluated.
- The current region decomposition uses binary splitting in one dimension.
- Certified optimization requires a valid Lipschitz constant, which may not be available for an arbitrary black-box objective.
- Without valid certification assumptions, budget exhaustion does not constitute a proof of global optimality.
- The empirical evaluation uses a limited collection of representative one-dimensional benchmark functions.
- The comparative evaluation uses a specific family of synthetic benchmark functions generated from smooth Gaussian-mixture landscapes.
- The reference solutions used in the comparative study are numerical approximations rather than analytically verified global optima.
- Stochastic baseline methods are evaluated using fixed seeded runs rather than statistical distributions over many independent runs.
- The comparative experiments do not exhaustively tune the parameters of every optimization method.
- The current study does not establish scalability to high-dimensional optimization problems.
- No universal superiority claim is made for ARRGO over existing global optimization methods.

These limitations indicate directions for further theoretical development, implementation, and empirical evaluation rather than contradictions of the core framework.

---

---

## Future Work

Several directions can extend the ARRGO framework beyond its current scope.

### Higher-Dimensional Implementation

Implement the finite-dimensional formulation developed in the theoretical framework and evaluate ARRGO on multidimensional optimization problems.

### Advanced Region Decomposition

Investigate alternative region-splitting strategies, including adaptive split-direction selection and multidimensional spatial decomposition.

### Improved Refinement Policies

Develop more advanced criteria for deciding between sampling and structural splitting based on regional uncertainty, potential, resolution, and objective behavior.

### Stronger Certification

Extend the certification framework to support tighter bounds and investigate practical approaches for obtaining or estimating valid regularity information.

### Broader Benchmark Evaluation

Evaluate ARRGO on larger and more diverse benchmark suites, including established optimization benchmarks and more challenging objective landscapes.

### Statistical Comparative Studies

Perform multiple independent runs for stochastic baselines and report statistical measures such as variance, confidence intervals, and robustness across different random seeds.

### Parameter Sensitivity Analysis

Study the sensitivity of ARRGO and competing methods to their configuration parameters and investigate systematic parameter-selection strategies.

### Performance and Scalability

Analyze computational complexity, memory usage, evaluation overhead, and scalability as the dimensionality and evaluation budget increase.

### Parallel Objective Evaluation

Investigate parallel evaluation strategies for settings where objective-function evaluations are expensive and can be performed independently.

### Real-World Applications

Evaluate ARRGO on practical optimization problems where objective evaluations are expensive, noisy, or computationally demanding.

---

---

## Citation

If you use ARRGO in your research or academic work, please cite this repository.

```bibtex
@software{dolati_arrgo,
  author = {Atena Dolati},
  title = {ARRGO: Adaptive Region Refinement for Global Optimization},
  url = {https://github.com/AtenaDolati/adaptive-region-optimization},
  year = {2026}
}
```



