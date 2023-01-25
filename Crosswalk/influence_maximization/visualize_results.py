import os
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
import json


DATASETS = ["rice_subset", "synth2", "synth3", "twitter"]
METHODS = ["greedy", "adv", "unweighted", "fairwalk", "random_walk"]
NUM_NODES_A = {"rice_subset": 344, "synth2": 350, "synth3": 300, "twitter": 2598}
NUM_NODES_B = {"rice_subset": 97, "synth2": 150, "synth3": 125, "twitter": 782}
NUM_NODES_C = {"synth3": 75, "twitter": 180}
NUM_GROUPS = {"rice_subset": 2, "synth2": 2, "synth3": 3, "twitter": 3}

n_seeds = np.arange(2,41,2)
red_ = '#fab3ac'
blue_ = '#29a5e3'
cyan_ = '#d2f0f7'
green_ = '#a3f77e'
gray_ = '#dbdbdb'
purple_ = '#BF55EC'
yellow_ = '#F7CA18'
label_size = 27
font_size = 24
image_size = (14, 8.5)
line_width = 3
square = True
bar_width = 0.5
legend_size = 20

def get_bar_plot(total_influence_results, disparity_results, dataset, ylim=None):

    has_3_groups = NUM_GROUPS[dataset] == 3

    xe = [2 - bar_width, 2]
    xu = [4 - bar_width, 4]
    xf = [6 - bar_width, 6]
    xa = [8 - bar_width, 8]

    if not has_3_groups:
        xp = [10 - bar_width, 10]

    deepwalk_influence = total_influence_results["unweighted"]
    fairwalk_influence = total_influence_results["fairwalk"]
    crosswalk_influence = total_influence_results["random_walk"]
    greedy_influence = total_influence_results["greedy"]

    if not has_3_groups:
        adv_influence = total_influence_results["adv"]

    deepwalk_disparity = disparity_results["unweighted"]
    fairwalk_disparity = disparity_results["fairwalk"]
    crosswalk_disparity = disparity_results["random_walk"]
    greedy_disparity = disparity_results["greedy"]

    if not has_3_groups:
        adv_disparity = disparity_results["adv"]

    fig, ax = plt.subplots()

    ax.bar(xe[0], greedy_influence, bar_width, color=purple_, edgecolor='black', label='Total Influence Percentage')
    ax.bar(xu[0], deepwalk_influence, bar_width, color=purple_, edgecolor='black')
    ax.bar(xf[0], fairwalk_influence, bar_width, color=purple_, edgecolor='black')
    ax.bar(xa[0], crosswalk_influence, bar_width, color=purple_, edgecolor='black')
    if not has_3_groups:
        ax.bar(xp[0], adv_influence, bar_width, color=purple_, edgecolor='black')

    ax.bar(xe[1], greedy_disparity, bar_width, color=yellow_, edgecolor='black', label='Disparity')
    ax.bar(xu[1], deepwalk_disparity, bar_width, color=yellow_, edgecolor='black')
    ax.bar(xf[1], fairwalk_disparity, bar_width, color=yellow_, edgecolor='black')
    ax.bar(xa[1], crosswalk_disparity, bar_width, color=yellow_, edgecolor='black')
    if not has_3_groups:
        ax.bar(xp[1], adv_disparity, bar_width, color=yellow_, edgecolor='black')

    if ylim:
        ax.set_ylim([0, ylim])

    plt.legend(loc='upper right', prop={'size': legend_size})

    if has_3_groups:
        plt.xticks([2, 4, 6, 8], ['Greedy', 'DeepWalk', 'FairWalk', 'CrossWalk'], fontsize=legend_size)
    else:
        plt.xticks([2, 4, 6, 8, 10], ['Greedy', 'DeepWalk', 'FairWalk', 'CrossWalk', 'Adversarial'], fontsize=legend_size)

    ax.yaxis.grid(color='gray', linestyle='dashed')

    plt.rcParams.update({'font.size': font_size})
    plt.yticks(fontsize=label_size)
    fig.set_size_inches(image_size[0], image_size[1])

    fig.savefig(os.path.join("fig", dataset) + ".pdf", bbox_inches='tight')


def read_txt_file(filename, dataset):
    has_3_groups = NUM_GROUPS[dataset] == 3

    n_a = NUM_NODES_A[dataset]
    n_b = NUM_NODES_B[dataset]

    if has_3_groups:
        n_c = NUM_NODES_C[dataset]

    inf_a, inf_b, inf_c = [], [], []

    with open(filename, "r") as r:
        for line in r:
            info = line.split()

            inf_a.append(float(info[2]))
            inf_b.append(float(info[4]))

            if has_3_groups:
                inf_c.append(float(info[6]))

    inf_a, inf_b = np.array(inf_a), np.array(inf_b)
    if has_3_groups:
        inf_c = np.array(inf_c)

    if has_3_groups:
        total_fraction = 100 * (inf_a + inf_b + inf_c) / (n_a + n_b + n_c)
    else:
        total_fraction = 100 * (inf_a + inf_b) / (n_a + n_b)

    frac_a = 100 * inf_a / n_a
    frac_b = 100 * inf_b / n_b

    if has_3_groups:
        frac_c = 100 * inf_c / n_c

    if has_3_groups:
        var_fraction = np.var(np.concatenate( [frac_a.reshape([-1,1]), frac_b.reshape([-1,1]), frac_c.reshape([-1,1])], axis=1), axis=1)
    else:
        var_fraction = np.var(np.concatenate( [frac_a.reshape([-1,1]), frac_b.reshape([-1,1])], axis=1), axis=1)

    results = np.concatenate([np.array(total_fraction).reshape([-1,1]), np.array(var_fraction).reshape([-1,1])], axis=1)

    return results


def main():
    for dataset in DATASETS:
        result_files = os.listdir(os.path.join("results", dataset))

        total_influence_results = {}
        disparity_results = {}

        for method in METHODS:
            if method != "adv":
                cur_files = [os.path.join("results", dataset, file) for file in result_files if method in file]

                all_results = []
                for file in cur_files:
                    results = read_txt_file(file, dataset)
                    all_results.append(results)

                all_results = np.mean( np.concatenate([np.expand_dims(result, 2) for result in all_results], axis=2), axis=2)
                total_influence_results[method] = all_results[-1][0]
                disparity_results[method] = all_results[-1][1]
            elif dataset == "rice_subset" or dataset == "synth2":
                results_filename = os.path.join("results", dataset, "adv_results.txt")

                with open(results_filename, "r") as r:
                    results = json.load(r)

                    influence_results = []
                    disparities = []

                    for result in results:
                        influence_a = result[4] * 100
                        influence_b = result[5] * 100
                        total_influence = (influence_a + influence_b) / 2
                        disparity = np.var([influence_a, influence_b])

                        influence_results.append(total_influence)
                        disparities.append(disparity)

                    total_influence = np.mean(influence_results)
                    disparity = np.mean(disparities)

                disparity_results[method] = disparity
                total_influence_results[method] = total_influence

        get_bar_plot(total_influence_results, disparity_results, dataset)

if __name__ == "__main__":
    main()