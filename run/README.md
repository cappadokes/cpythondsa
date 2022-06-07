#   Running the experiments on your machine

To run analogous experiments as the ones we conducted locally, please follow the below instructions:

1. Ensure that your machine:
   - runs GNU/Linux
   - exposes an interface identical or similar to [Intel's RAPL](https://www.kernel.org/doc/html/latest/power/powercap/powercap.html). If you're **not** interested in energy consumption measurements, ignore this.
2. Install the modified [`pyperf`](https://github.com/psf/pyperf/pull/125) and [`pyperformance`](https://github.com/python/pyperformance/pull/140) packages mentioned in the linked PR's. Again, you have to do this **only** if you're interested in taking energy measurements.

> ***ATTENTION:*** As you may observe, current modifications done on the aforementioned Python packages assume that the machine of interest includes a RAPL-based power capping interface. We have taken care, however, to make these changes extensible to arbitrary interfaces. The only requirement is that *it is possible to read from somewhere, or compute, an always-increasing value of the total energy consumed up to the point of reading/computing.*

3. Configure and run the included `bash` scripts depending on your setup (you will see that they are dead-simple).
4. Use `/viz/viz.py` for producing both a terminal-located report and visual results.