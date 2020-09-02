"""
This module contains all plotting functionality.
To use within Python Scripts

"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.collections import LineCollection
from matplotlib.legend_handler import HandlerTuple
import matplotlib.transforms as transforms
from IPython.core.getipython import get_ipython

# Control Definitions

# Colors
col_dict = {'Annotations': 'grey',
            'Detections': 'tab:blue',
            'Insertions': 'tab:green',
            'Deletions': 'tab:orange',
            'Shifts': 'palevioletred'}

# Linestyles
lin_dict = {'Annotations': 'solid', 'Detections': 'solid', 'Insertions': 'dashdot', 'Deletions': 'dotted',
            'Shifts': 'dotted'}

# Plotted Elements - Edit this to change the drawed elements
D_SID = True        # Draw SID Labels
D_INN_WIN = True    # Draw Inner Tolerance Window
D_OUT_WIN = True    # Draw Outer Tolerance Window
D_LEGEND = True     # Draw Legend
D_ARROWS = True     # Draw Shift Arrows

# SID Labels
SHI_char = 'S'      # Label for Shifts
INS_char = 'I'      # Label for Insertions
DEL_char = 'D'      # Label for Deletions


class HandlerTupleVertical(HandlerTuple):
    """Plots all the given Lines vertical stacked."""

    def __init__(self, **kwargs):
        """Run Base Handler."""
        HandlerTuple.__init__(self, **kwargs)

    def create_artists(self, legend, orig_handle,
                       xdescent, ydescent, width, height, fontsize, trans):
        """Create artists (the symbol) for legend entry."""

        # How many lines are there.
        numlines = len(orig_handle)
        handler_map = legend.get_legend_handler_map()

        # divide the vertical space where the lines will go
        # into equal parts based on the number of lines
        height_y = (height / numlines)

        leglines = []
        for i, handle in enumerate(orig_handle):
            handler = legend.get_legend_handler(handler_map, handle)
            legline = handler.create_artists(legend, handle, xdescent, (2*i + 1)
                                             * height_y, width, 2*height, fontsize, trans)
            leglines.extend(legline)
        return leglines


def detail_operations(ops):
    """Gets the list of operations and indexes from the full operations matrix."""
    idx_shi = np.where(ops[:, 4] != 0)[0]
    idx_ins = np.where(ops[:, 2] == 1)[0]
    idx_del = np.where(ops[:, 3] == 1)[0]
    lst_det = ops[ops[:, 1] == 1, 0]
    lst_ins = ops[ops[:, 2] == 1, 0]
    lst_del = ops[ops[:, 3] == 1, 0]
    shi_res = ops[idx_shi, 0] + ops[idx_shi, 4]
    un_shi = ops[idx_shi, 0]

    return lst_det, lst_ins, lst_del, shi_res, un_shi, idx_shi, idx_ins, idx_del


def draw_SID_labels(ax, ops, idx_SHI=None, idx_INS=None, idx_DEL=None, plot_type='subplots'):
    """Draws the labels for Shift, Insert, Delete"""
    fontsize = 'smaller'
    bbox_def = dict(boxstyle="round,pad=0.20", fc="white", ec="grey", alpha=0.9)
    bbox_ins = bbox_del = bbox_shi = bbox_def

    if (plot_type == 'subplots'):
        Y_pos = 1.0  # subplot: top of axis
    else:
        Y_pos = 0.5  # single: half of axis

    # the x coords of this transformation are data, and the y coord are axes
    trans = transforms.blended_transform_factory(ax.transData, ax.transAxes)

    for idx, det in enumerate(ops):
        if idx in idx_INS:
            ax.annotate(INS_char, xy=(det, Y_pos), xycoords=trans, bbox=bbox_ins, xytext=(0, 0),
                        textcoords='offset points', ha='center', size=fontsize)
        elif idx in idx_DEL:
            ax.annotate(DEL_char, xy=(det, Y_pos), xycoords=trans, bbox=bbox_del, xytext=(0, 0),
                        textcoords='offset points', ha='center', size=fontsize)
        elif idx in idx_SHI:
            ax.annotate(SHI_char, xy=(det, Y_pos), xycoords=trans, bbox=bbox_shi, xytext=(0, 0),
                        textcoords='offset points', ha='center', size=fontsize)
    return True


def draw_outer_tolerance_window(ax, annotations, idx_shifts, window=1):
    """Draws the outer tolerance window around annotations"""
    for idx, ann in enumerate(annotations):
        if idx in idx_shifts:
            window_left = ann - window
            window_right = ann + window
            rect = patches.Rectangle(xy=(window_left, 0), width=window_right-window_left, height=1,
                                     edgecolor='None', facecolor=col_dict.get('Shifts'), alpha=0.3)
            ax.add_patch(rect)
    return True


def draw_inner_tolerance_window(ax, annotations, window=0.07):
    """Draws the inner tolerance window around annotations"""
    for ann in annotations:
        window_left = ann - window
        window_right = ann + window
        rect = patches.Rectangle(xy=(window_left, 0), width=window_right-window_left, height=1,
                                 edgecolor='None', facecolor=col_dict.get('Annotations'), alpha=0.3)
        ax.add_patch(rect)
    return True


def get_segment(positions, plot_type):
    """
    Gets a line segment in (x,y) coords (required for linecollection) from a list of x positions

    Parameters
    ----------
    positions : list
        x positions.

    plot_type : str
        type of plot.
            'subplots': coords for subplot
            'upper': coords for single plot - positive part
            'lower': coords for single plot - negative part

    Returns
    -------
    result: list
        line segments in (x,y) coords

    """
    if (plot_type == 'subplots'):
        result = [[(el, 0), (el, 1)] for el in positions]
    elif plot_type == 'upper':
        result = [[(el, 0), (el, 1)] for el in positions]
    elif plot_type == 'lower':
        result = [[(el, -1), (el, 0)] for el in positions]
    return result


def get_shift_indices_from_annotations(anns, shifts):
    """
    Gets a line segment in (x,y) coords (required for linecollection) from a list of x positions

    Parameters
    ----------
    positions : list
        x positions.

    plot_type : str
        type of plot.
            'subplots': coords for subplot
            'upper': coords for single plot - positive part
            'lower': coords for single plot - negative part

    Returns
    -------
    result: list
        line segments in (x,y) coords

    """
    result = []
    for i in shifts:
        match = np.nonzero(i == anns)[0]
        if len(match) > 0:
            result.append(match[0])

    return result


def add_line_collections(ax_upper, ax_lower, labels_upper, labels_lower, items_upper, items_lower):
    """Adds line collections to the proper axis."""
    # Upper part of the plot (reference values: annotations and tolerance windows)
    lcs_upper = []
    for item, label in zip(items_upper, labels_upper):
        if type(item) is np.ndarray:
            # Regular case (array)
            lc = LineCollection(get_segment(item, 'upper'), colors=col_dict.get(label), linestyle=lin_dict.get(label))
            ax_upper.add_collection(lc)
            lcs_upper.append(lc)
        else:
            # Otherwise, it's a patch
            lcs_upper.append(item)

    # Lower part of the plot (detections, shifts, insertions, deletions)
    lcs_lower = []
    for item, label in zip(items_lower, labels_lower):
        if type(item) is tuple:
            # Case of un_shifted and shift_result that come as a tuple
            lc1 = LineCollection(
                get_segment(item[0],
                            'lower'),
                colors=col_dict.get(label),
                linestyle=lin_dict.get(label))
            ax_lower.add_collection(lc1)
            lc2 = LineCollection(get_segment(item[1], 'lower'), colors=col_dict.get(label))
            ax_lower.add_collection(lc2)
            lcs_lower.append((lc1, lc2))
        else:
            # All the other cases
            lc = LineCollection(get_segment(item, 'lower'), colors=col_dict.get(label), linestyle=lin_dict.get(label))
            ax_lower.add_collection(lc)
            lcs_lower.append(lc)
    ax_lower.autoscale()
    ax_upper.autoscale()

    return lcs_upper, lcs_lower


def isnotebook():
    try:
        shell = get_ipython().__class__.__name__
        if shell == 'ZMQInteractiveShell':
            return True   # Jupyter notebook or qtconsole
        elif shell == 'TerminalInteractiveShell':
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)
    except NameError:
        return False      # Probably standard Python interpreter


def plot_operations(operations, annotations, title='', inn_tol_win=0.07, out_tol_win=1.0, plot_type='subplots'):
    """
    Produces the matplotlib figure to be rendered.

    Parameters
    ----------
    operations : nparray
        x positions.

    annotations : list/nparray
        ground-truth annotation

    title : str (optional)
        figure title
        (Default value = '')

    inn_tol_win : float (optional)
        inner tolerance window (+- interval) in seconds
        (Default value = 0.07)

    out_tol_win : float (optional)
        outer tolerance window (+- interval) in seconds
        (Default value = 1)

    plot_type: str (optional)
        type of plot
            (default) 'subplots': 2 subplots with annotations on upper axis and operations on lower axis
                        'single': single subplot with annotations and operations on same axis

    Returns
    -------
    fig: matplotlib figure
    ax: matplotlib axis
    """

    # Default Settings
    if isnotebook():
        plt.style.use('./jupyter.mplstyle')
        fs_single = (16, 2.5)
        fs_subplots = (16, 3)
    else:
        plt.style.use('./python.mplstyle')
        fs_single = (11, 2)
        fs_subplots = (11, 3)

    if plot_type == 'subplots':
        fig, ax = plt.subplots(2, figsize=fs_subplots, dpi=100, sharex=True)
        ax_upper = ax[0]
        ax_lower = ax[1]
    else:
        fig, ax = plt.subplots(figsize=fs_single, dpi=100)
        ax_upper = ax_lower = ax
    fig.canvas.set_window_title(title)

    detections, insertions, deletions, shift_result, un_shifted, idx_shifts, idx_insertions,\
        idx_deletions = detail_operations(operations)

    idx_shifts_per_annotation = get_shift_indices_from_annotations(annotations, shift_result)

    # draw the SID (Shift, Insert, Delete) labels
    if D_SID:
        draw_SID_labels(ax_lower, operations[:, 0], idx_shifts, idx_insertions, idx_deletions, plot_type)

    # draw the inner tolerance window
    if D_INN_WIN:
        draw_inner_tolerance_window(ax_upper, annotations, inn_tol_win)
    # FIXME:
    # inner tolerance patch for legend
    inner_tolerance_patch = patches.Patch(facecolor=col_dict.get('Annotations'), edgecolor='None', alpha=0.3)

    # draw the outer tolerance window (for shifts)
    if D_OUT_WIN:
        draw_outer_tolerance_window(ax_upper, annotations, idx_shifts_per_annotation, out_tol_win)
    # FIXME:
    # outer tolerance patch for legend
    outer_tolerance_patch = patches.Patch(facecolor=col_dict.get('Shifts'), edgecolor='None', alpha=0.3)

    # add Line Collections
    lines_positive = [annotations, inner_tolerance_patch, outer_tolerance_patch]
    lines_negative = [detections, insertions, deletions, (un_shifted, shift_result)]
    labels_upper = ['Annotations', f'Inner tol. win.:$\\pm${inn_tol_win}s', f'Outer tol. win.:$\\pm${out_tol_win}s']
    labels_lower = ['Detections', 'Insertions', 'Deletions', 'Shifts']
    lines_upper, lines_lower = add_line_collections(
        ax_upper, ax_lower, labels_upper, labels_lower, lines_positive, lines_negative)

    if D_LEGEND:
        if plot_type == 'subplots':
            ax_lower.legend(lines_lower, labels_lower, bbox_to_anchor=(1.02, 0.5),
                            loc='center left', borderaxespad=0,
                            handler_map={tuple: HandlerTupleVertical()})
        else:
            lines_upper += lines_lower
            labels_upper += labels_lower

        ax_upper.legend(lines_upper, labels_upper, bbox_to_anchor=(1.02, 0.5),
                        loc='center left', borderaxespad=0,
                        handler_map={tuple: HandlerTupleVertical()})

    if plot_type == 'subplots':
        ax_upper.set(ylim=(0, 1), yticks=[])
        ax_lower.set(ylim=(-1, 0), yticks=[], xlabel='time (s)')
    else:
        # Draw horizontal line (at y=0)
        ax_upper.axhline(y=0, linewidth=1, color='k')
        ax_lower.set(ylim=(-1, 1), yticks=[], xlabel='time (s)')
    ax_lower.set_xlim(left=0)

    if D_ARROWS:
        for i, shift_ind in enumerate(idx_shifts):
            ax_lower.annotate("", xy=(shift_result[i], -0.5), xycoords='data',
                              xytext=(operations[shift_ind, 0], -0.5), textcoords='data',
                              arrowprops=dict(arrowstyle="->", color=col_dict.get('Shifts'), linestyle='dashdot'))

    return fig, ax
