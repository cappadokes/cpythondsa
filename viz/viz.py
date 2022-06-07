from argparse import ArgumentParser
from os import walk
import os.path as path
import subprocess
import copy
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import wilcoxon, mannwhitneyu
from scipy.stats import mstats
from statistics import median
from statsmodels.distributions.empirical_distribution import ECDF

sns.set_theme(context="paper", style="whitegrid", font_scale=2, font="monospace")

def plot_means(df, cat):
    #   Plots app-wise mean speedup.
    agg = pd.DataFrame()
    for point in ["baseline", "pymalloc_mimalloc", "pymalloc_jemalloc", "mimalloc", "jemalloc", "malloc"]:
        point_df = df[df.config == point]
        dat = point_df.groupby(["benchmark"])
        means = dat.measurement.apply(mstats.gmean).reset_index()
        means.rename(columns = {"measurement":"mean_speedup"}, inplace=True)
        means = means.assign(config = [point] * len(means.index))
        agg = pd.concat([agg, means], ignore_index=True)
        ecdf = ECDF(means["mean_speedup"])
        sns.lineplot(x = ecdf.x, y = ecdf.y)
    
    plt.legend(["baseline", "pymalloc_mimalloc", "pymalloc_jemalloc", "mimalloc", "jemalloc", "malloc"])
    plt.ylabel("P(S <= x)")
    plt.xlabel("Speedup (x)")
    if cat == "time":
        cat = "execution time"
    elif cat == "mem":
        cat = "memory footprint"
    elif cat == "en_cpu":
        cat = "core energy consumption"
    elif cat == "en_dram":
        cat = "DRAM energy consumption"
    elif cat == "en_uncore":
        cat = "uncore energy consumption"
    plt.title("Speedup geometric mean ECDF of {}".format(cat))
    plt.show()
    

def print_report(gen_flow, uniapp, speedup, conf=0.05):
    #   Generates final, helpful report.
    #   Also prints figures.
    print("Partly answering RQ1: can performance be improved cross-app with respect to baseline?\n")
    #   RQ1: Cross-app speedup?
    for point in ["pymalloc_mimalloc", "mimalloc", "pymalloc_jemalloc", "jemalloc", "malloc"]:
        (s, c) = speedup[point]
        if s == 1.0:
            print("{}: could marginally improve performance of specific cases with a confidence of {}%".format(point, round(100 * c)))
        elif s == 0.0:
            print("{}: will hurt performance with a confidence of {}%".format(point, round(100 * (1.0 - c), 2)))
        else:
            print("{}: may improve performance up to {}x with a confidence of {}%".format(point, round(s, 3), round(100 * c, 2)))
    #   RQ2: Does the app itself matter?
    print("\nPartly answering RQ2: do application-specific characteristics matter?\n")
    for point in ["pymalloc_mimalloc", "mimalloc", "pymalloc_jemalloc", "jemalloc", "malloc"]:
        gain_count = 0
        conf_list = []
        for bench in uniapp[point]:
            if 1 - uniapp[point][bench] < conf:
                gain_count += 1
                conf_list.append(uniapp[point][bench])
        if len(conf_list) > 0:
            print("{}: improves {} out of {} stable apps with a geomean confidence of {}%.".format(point, gain_count, len(uniapp[point].keys()), round(100 * mstats.gmean(np.array(conf_list)), 2)))
        else:
            print("{}: does not improve any app.".format(point))

def clearsilver(dirty, cat):
    #   Keeps only valid subsets of benchmarks
    #   across all config points.
    #   Also normalizes everything with respect
    #   to the baseline.
    clear = copy.deepcopy(dirty)
    for point_1 in dirty:
        benchmarks_available = dirty[point_1].keys()
        for point_2 in dirty:
            benchmarks_to_clean = dirty[point_2].keys()
            for b in benchmarks_available:
                if b not in benchmarks_to_clean and b in clear[point_1].keys():
                    clear[point_1].pop(b)
    for clean_bench in clear["baseline"]:
        rule = unitsversalize(clear["baseline"][clean_bench][0], cat)
        for point in clear:
            for measurement in clear[point][clean_bench]:
                test = float(unitsversalize(measurement, cat))
                if test != 0.0:
                    measurement[0] = float(rule) / test
                else:
                    #   Laptop en_dram case yielded some zero values,
                    #   so we take care and drop them if they appear.
                    clear[point][clean_bench].remove(measurement)
    return clear


def hpt_speedup(df, conf=0.05, gamma_step=0.01):
    #   Implements the statistical speedup
    #   calculation.
    opts = df.config.unique()
    #   Remove baseline from the datasets that are
    #   to be compared with baseline.
    to_del = np.where(opts == "baseline")
    opts = np.delete(opts, to_del)
    speedup = {}
    for point in opts:
        gamma = 1.0
        gammas_tried = []
        tests_computed = []
        h = True
        while h:
            #   First case: the point doesn't improve at all.
            gammas_tried.append(gamma)
            test = hpt_core(df, "baseline", point, gamma, conf)[0]
            if test < conf:
                gammas_tried.append(0.0)
                h = False
            #   Second case: the point does improve performance.
            elif 1 - test < conf:
                gamma += gamma_step 
            #   Third case: not enough confidence.
            else:
                h = False
        final_gamma = gammas_tried.pop()
        #   Keep the uncertain speedups too, for more clarity.
        #   Also save the HPT confidence.
        speedup[point] = (final_gamma, test)

    return speedup


def hpt_core(df, x_name, y_name, gamma=1.0, conf=0.05):
    #   Implements the HPT general flow.
    #   Decoupled from hpt in order to
    #   support speedup calculations.
    diffs = []
    uniapp_results = {}
    for bench_name in df.benchmark.unique():
        #   Select data.
        x = df.query("config == @x_name and benchmark == @bench_name").measurement
        y = df.query("config == @y_name and benchmark == @bench_name").measurement
        #   'greater' means that the baseline performance can be improved.
        #   because y has stochastically better performance.
        y = y.divide(gamma)
        result = mannwhitneyu(x, y, alternative='greater')
        if result.pvalue < conf or 1 - result.pvalue < conf:
            diffs.append(median(x) - median(y))
            uniapp_results[bench_name] = result.pvalue
        else:
            diffs.append(0.0)
    final_results = wilcoxon(diffs, alternative='greater').pvalue

    return final_results, uniapp_results


def hpt(df, conf=0.05):
    #   Accepts a DataFrame full of measurements
    #   and conducts the general Flow of HPT for all pairs
    #   reasonable to compare.
    #   The reasonable datasets to compare are:
    #   - (baseline, pymalloc_mimalloc, pymalloc_jemalloc)
    #   - (baseline, malloc, jemalloc, mimalloc)
    opts = df.config.unique()
    #   Remove baseline from the datasets that are
    #   to be compared with baseline.
    to_del = np.where(opts == "baseline")
    opts = np.delete(opts, to_del)
    final_results = {}
    uniapp_results = {}
    for point in opts:
        fr, ua = hpt_core(df, "baseline", point, 1.0, conf)
        uniapp_results[point] = ua
        final_results[point] = fr

    return final_results, uniapp_results


def transformu(tup, cat):
    #   For time, makes all milliseconds.
    #   For mem, makes all kilobytes.
    #   For energy, makes all millijoules.
    (val, u) = tup
    if cat == "time":
        if u == "sec":
            val *= 1000
        elif u == "us":
            val /= 1000
        elif u == "ns":
            val /= 10e6
    elif cat == "mem":
        if u == "MB":
            val *= 1024
    else:
        if u == "J":
            val *= 1000
        elif u == "mJ":
            return val
        else:
            val /= 1000
    return val


def unitsversalize(dat, cat):
    #   Appropriately transforms and
    #   returns values so as to maintain
    #   a single unit of measurement.
    val = transformu(dat, cat)
    if cat == "time":
        u = "ms"
    elif cat == "mem":
        u = "kB"
    else:
        u = "mJ"
    return val


def make_dataframe(dct, cat):
    #   Assuming the structure implied
    #   by the parsing functions below,
    #   create seaborn-friendly DataFrame.
    points_list = []
    benchmarks_list = []
    measurements_list = []
    for point in dct:
        for benchmark in dct[point]:
            for m in dct[point][benchmark]:
                points_list.append(point)
                benchmarks_list.append(benchmark)
                val = m[0]
                measurements_list.append(val)

    data = {
        "config": points_list,
        "benchmark": benchmarks_list,
        "measurement".format(cat): measurements_list,
    }
    return pd.DataFrame(data)


def numberize_str(src):
    if '.' in src:
        return float(src)
    else:
        return int(src)


def str_to_data(l):
    #   Assumes input of format "value unit garbage"
    els = l.split(' ')
    return [numberize_str(els[0]), els[1]]


def list_to_str(l):
    res = ""
    for c in l:
        res += c
    return res


def unmangle_raw(inp):
    outp = {}
    name_parsed = False
    in_warning = False
    empty_traversed = 0
    #   Split output in lines.
    for line in inp.split('\n'):
        #   Keep only stable results.
        if 'WARNING' in line:
            in_warning = True
            data_obj["valid"] = False
        elif in_warning:
            if line == '':
                empty_traversed += 1
            if empty_traversed == 2:
                in_warning = False
                empty_traversed = 0
        elif not name_parsed and line != '' and not in_warning:
            data_obj = {"valid": True, "data": []}
            bench_name = list_to_str(line)
            name_parsed = True
        elif '- value' in line:
            data_obj["data"].append(str_to_data(line.split(": ")[1]))

        if len(data_obj["data"]) > 0 and line == '' and not in_warning:
            name_parsed = False
            if data_obj["valid"] == True:
                outp[bench_name] = data_obj["data"]

    return outp


def do_assertions(p, c, machine="laptop"):
    #   Make sure that category is valid.
    assert c in ["time", "mem", "en_cpu", "en_dram", "en_uncore"]

    data = {}
    for idx, t in enumerate(walk(p, onerror=lambda e: print(e))):
        if idx == 0:
            continue
        else:
            if len(set(["server", "laptop", "tegra"]).intersection(t[1])) > 0:
                #   Need to go one level deeper.
                #   Points are scanned depth-first.
                current_point = t[0].split('/')[-1]
                continue
            elif machine != t[0].split('/')[-1]:
                #   Have not reached the right level yet!
                continue
            #   Check that point subdir only contains files.
            if len(t[1]) != 0:
                raise AssertionError("Design point subdirs should only include measurements, not folders. Raised for {}.".format(point_names[name_idx]))
            elif len(t[2]) == 0:
                raise AssertionError("No measurements included for {}.".format(current_point))
            #   Check that category exists everywhere.
            found = False
            for file in t[2]:
                els = file.split('.')
                if c in els:
                    found = True
                    d = subprocess.run(['pyperf', 'dump', path.join(t[0], file)], stdout=subprocess.PIPE).stdout.decode('utf-8')
                    break
            if not found:
                print("Measurements for given category not included in {}.".format(current_point))
            #   Consolidate final data dictionary with specific data for this design point.
            data[current_point] = unmangle_raw(d)
    
    return data


def parse_args():
    parser = ArgumentParser(description="Visualizes SAMOS data.")
    parser.add_argument("results", type=str, help="Absolute path to results directory.")
    parser.add_argument("category", type=str, help="Desired category to be plotted.")
    parser.add_argument("machine", type=str, help="Sub-directory of machine-specific measurements.")
    args = parser.parse_args()
    return args.results, args.category, args.machine


def clearsilver2(df, ua):
    #   Keeps only those measurements that
    #   correspond to stable (HPT-wise) apps
    #   across ALL points.
    clear = copy.deepcopy(df)
    for point_to_clean in ua:
        to_be_cleaned = ua[point_to_clean].keys()
        for point_as_rule in ua:
            rule = ua[point_as_rule].keys()
            for benchmark in to_be_cleaned:
                if benchmark not in rule and benchmark in clear.benchmark.unique():
                    indices = clear[clear.benchmark == benchmark].index
                    clear.drop(index=indices, inplace=True)
    return clear


if __name__ == "__main__":
    #   Parse arguments.
    results_path, category, machine = parse_args()
    conf = 0.05
    #   Gather all data to be plotted in a dictionary.
    dirty_data = do_assertions(results_path, category, machine)
    #   Normalize everything with respect to first baseline
    #   measurement and also keep only valid subsets.
    clean_data = clearsilver(dirty_data, category)
    #   Create the corresponding DataFrame.
    clean_pdf = make_dataframe(clean_data, category)
    #   Now all measurements are in the DataFrame, and
    #   we are ready to invoke HPT.
    hpt_gen, hpt_uniapp = hpt(clean_pdf, conf)
    #   We do a double distillation here since some results
    #   proved unstable HPT-wise.
    clean_pdf = clearsilver2(clean_pdf, hpt_uniapp)
    hpt_gen, hpt_uniapp = hpt(clean_pdf, conf)
    #   Next, we compute the speedup of each point.
    speedup = hpt_speedup(clean_pdf, conf, 0.005)
    #   Speedup Legend:
    #   (1.0, x)    --> config under test (not baseline) will MARGINALLY improve performance with a certainty of x.             ---> points to app-specificity
    #   (0.0, x)    --> config under test will worsen performance with a certainty of 1 - x.                                    ---> points to baseline superiority over specific config
    #   (s, x)      --> config under test will improve performance s times (e.g. 1.005x for s = 1.005) with a certainty of x.   ---> points to config superiority
    print_report(hpt_gen, hpt_uniapp, speedup, conf)
    #   To finish with my report, I need my plot of average mean improvement.
    #   I will do it the stupid way.
    plot_means(clean_pdf, category)