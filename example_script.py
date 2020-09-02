"""
This script provides an example of how to create a list of variations of beat detections,
and process it with the corresponding ground-truth annotation.
For each of the variations, it calculates the following:
  - annotation efficiency;
  - f-measure;
  - transformed beat detections and corresponding f-measure;
Saves the transformed beat detections as well as all the plots as *.png files in the /figures/ folder.
These figures are rendered as single plots with the reference annotations on the positive part of
the y-axis and the different operations (shifts, insertions, deletions) on the negative part.
"""

import matplotlib.pyplot as plt

import numpy as np

from modules.ext_libraries import f_measure, variations

from modules.operating import operation_count, process_operations, get_summary
from modules.plotting import plot_operations

# Load beat detections and annotations
dets_file = 'dets'
dets = np.loadtxt(f'{dets_file}.txt')
anns = np.loadtxt('hains006.beats')

# Use only the first column (i.e. the time stamp) if these are 2D
if dets.ndim > 1:
    dets = dets[:, 0]

if anns.ndim > 1:
    anns = anns[:, 0]

# Process all variations of beat detections and the ground truth annotations
dets_variations, types_variations = variations(dets, offbeat=True, double=True, half=True, triple=True, third=True)

# Cycle through the full list of variations
for dets_variation, type_variation in zip(dets_variations, types_variations):

    # Get matrix of operations and annotation efficiency
    ops, ann_eff = operation_count(dets_variation, anns)

    # Get list of transformed detections
    transformed = process_operations(ops)

    # Save list of transformed detections
    np.savetxt(f'dets_{type_variation}_transformed.txt', transformed, fmt='%.2f')

    # Get combined f-measure (tuple with initial f-measure and transformed f-measure)
    comb_f_measure = f_measure(dets_variation, anns), f_measure(transformed, anns)

    # Display results
    print(get_summary(type_variation, ann_eff, comb_f_measure))

    # Get the figure and save it
    fig, ax = plot_operations(ops, anns, type_variation, plot_type='single')
    plt.savefig(f'figures/{type_variation}_vis.png', bbox_inches='tight')

    # Show the plot
    # plt.tight_layout()
    # plt.show()
