# The Impact of Dynamic Storage Allocation on CPython Execution Time, Memory Footprint and Energy Consumption: An Empirical Study
This repo accompanies our [SAMOS XXII](https://samos-conference.com/wp/) paper. It contains:

- the full set of our experimental results (`/data`)
- instructions and scripts for running the experiments (`/run`)
- code for data analysis and visualization (`/viz`)

At the time of writing, our paper is not yet available online. We will update this document as soon as it becomes so.

##  Abstract
Below you may find the paper's abstract, for a quick overview of what was done:

> CPython is the reference implementation of the Python programming language. Tools like machine learning frameworks, web development interfaces and scientific computing libraries have been built on top of it. Meanwhile, single-board computers are now able to run GNU/Linux distributions. As a result CPython's influence today is not limited to commodity servers, but also includes edge and mobile devices. We should thus be concerned with the performance of CPython applications. In this spirit, we investigate the impact of dynamic storage allocation on the execution time, memory footprint and energy consumption of CPython programs. Our findings show that (i) CPython's default configuration is optimized for memory footprint, (ii) replacing this configuration can improve performance by more than **1.6x** and (iii) application-specific characteristics define which allocator setup performs best at each case. Additionally, we contribute an open-source means for benchmarking the energy consumption of CPython applications. By employing a rigorous and reliable statistical analysis technique, we provide strong indicators that most of our conclusions are platform-independent.

##  Reference
If you find our work interesting and/or useful, please cite it as:

Christos Lamprakos, Lazaros Papadopoulos, Francky Catthoor and Dimitrios Soudris. "The Impact of Dynamic Storage Allocation on CPython Execution Time, Memory Footprint and Energy Consumption: An Empirical Study." In *Embedded Computer Systems: Architectures, Modeling, and Simulation: 22nd International Conference, SAMOS 2022, Samos, Greece, July 3-7, 2022*, Proceedings. Vol. TBA. Springer, 2022