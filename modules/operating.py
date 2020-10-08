"""
This module contains all the operations accounting.

"""
import numpy as np

from modules.utils import double_check_accounted


def get_summary(type_var, ann_eff, tup_f_m=(0.0, 1.0)):

    return (
        '- - - - - - - - - - - - - - - - -\n'
        f'{type_var:10s}\n'
        '- - - - - - - - - - - - - - - - -\n'
        f'annotation_efficiency: {ann_eff[0]:.3f}\n'
        f'  # "good" detections: {ann_eff[1]:.0f}\n'
        f'  # insertions: {ann_eff[2]:.0f}\n'
        f'  # deletions: {ann_eff[3]:.0f}\n'
        f'  # shifts: {ann_eff[4]:.0f}\n'
        '\n'
        f'(initial) f-measure: {tup_f_m[0]:.3f}\n'
        f'(transformed) f_measure: {tup_f_m[1]:.3f}\n'
    )


def get_variation(type_variation, list_detections, str_detections):
    """Gets a specific variation list of detections"""

    return list_detections[str_detections.index(type_variation)]


def annotation_efficiency(operations=None):
    """
    Calculates the annotation efficiency and stats

    Parameters
    ----------
    operations : list
        list of operations.

    Returns
    -------
    ae: float
        annotation efficiency
    n_detections: int
        number of (correct) detections
    n_insertions: int
        number of (correct) insertions
    n_deletions: int
        number of (correct) deletions
    n_shifts: int
        number of (correct) shifts

    """
    n_insertions = np.sum(operations[:, 2])
    n_deletions = operations[:, 3].sum()
    n_shifts = np.count_nonzero(operations[:, 4], axis=0)
    n_detections = operations[:, 1].sum()
    ae = n_detections / (n_detections + n_insertions + n_deletions + n_shifts)

    return ae, n_detections, n_insertions, n_deletions, n_shifts


def process_operations(operations=None):
    """ returns the transformed detections """
    ops = np.array(operations[np.where(operations[:, 3] != 1)], copy=True)
    transformed = ops[:, 0] + ops[:, 4]
    transformed = np.sort(transformed)

    return transformed


def operation_count(detections=None, annotations=None, inn_tol_win=0.07, out_tol_win=1.0):
    """
    Counts the number of operations necessary to maximise the F-measure.


    Parameters
    ----------
    detections : list
        list of detections.
    annotations : list
        list of annotations.
    inn_tol_win : float
        inner tolerance window in seconds
        (default value=0.07)
    out_tol_win : float
        outer tolerance window in seconds
        (default value=1)

    Returns
    -------
    operations: nparray
        matrix of operations required to transform detections.
    ae: float
        annotation efficiency.
    """
    if (annotations.size < 1) and (detections.size < 1):
        print('both the detections and annotations are empty, job done')
        operations = []
        ann_efficiency = 1
        return operations, ann_efficiency

    # to prevent a detection falling exactly midway between two annotations
    detections = np.sort(detections) + 1e-7
    annotations = np.sort(annotations)

    annotations_accounted_for = np.zeros(len(annotations))  # mark already used annotations
    detections_accounted_for = np.zeros(len(detections))  # mark already used detections
    operations = np.zeros(shape=(len(detections), 5))
    # populate the first column
    operations[:, 0] = detections

    # (1) Check whether the closest beat to each annotation is inside the tolerance window...
    # NOTE: this will be difficult to ascertain for other evaluation methods.
    for i, ann in enumerate(annotations):
        # find closest detection to current annotation ann
        val = np.amin(np.abs(detections - ann))
        ind = np.argmin(np.abs(detections - ann))
        if (val <= inn_tol_win):  # the detection is inside the tolerance window
            # Mark it as "good detection"
            operations[ind, 1] = 1
            # and ensure the other options aren't selected
            operations[ind, 2:] = 0
            detections_accounted_for[ind] = 1
            annotations_accounted_for[i] += 1
        else:  # The detection is outside of a tolerance window
            # Mark it for possible shifting or deletion, but only if
            # it hasn't already been marked as "good" for another detection
            if detections_accounted_for[ind] == 0:
                operations[ind, 3:] = 1

    # (2) extra detections (unmarked by now) are marked for deletion or shifting
    operations[np.nonzero(operations[:, 1:].sum(axis=1) == 0), 3:] = 1

    # (3) Determine which shifts and qualify the shift
    for i, ann in enumerate(annotations):
        # look at the unaccounted for annotations
        if (annotations_accounted_for[i] == 0):
            out_tol_win_min = ann - out_tol_win
            out_tol_win_max = ann + out_tol_win
            # get the set of detections inside the window
            dets_idx_in_shift_window, = np.nonzero((detections >= out_tol_win_min) & (detections <= out_tol_win_max))
            # over this set, we remove any detection that is
            # already accounted as a good detection
            # FIXME: Vectorised
            idx_to_remove = []
            for j, det in enumerate(dets_idx_in_shift_window):
                if (operations[det, 1] == 1) or (detections_accounted_for[det] == 1):
                    idx_to_remove.append(j)
            # Clear marking for removals
            dets_idx_in_shift_window = np.delete(dets_idx_in_shift_window, idx_to_remove)
            # find whichever unaccounted for detections is closest and mark this is a shift
            # FIXME: count_shift_to_treat
            count_shift_to_treat = len(dets_idx_in_shift_window)
            if count_shift_to_treat > 0:
                # Which is the closest detection the the current annotation ann
                dist = [ann - detections[det_idx] for det_idx in dets_idx_in_shift_window]
                idx_closest = np.argmin(np.abs(dist))
                if not detections_accounted_for[dets_idx_in_shift_window[idx_closest]]:
                    # it's not a deletion
                    operations[dets_idx_in_shift_window[idx_closest], 3] = 0
                    # we explicitly mark the shift
                    operations[dets_idx_in_shift_window[idx_closest], 4] = dist[idx_closest]

                # Once it's a shift, mark it as accounted for
                annotations_accounted_for[i] += 1
                detections_accounted_for[dets_idx_in_shift_window[idx_closest]] += 1
                count_shift_to_treat -= 1

            # Mark for deletion any other candidates for shift
            if count_shift_to_treat > 0:
                idx, = np.where(detections_accounted_for[dets_idx_in_shift_window] == 0)
                operations[dets_idx_in_shift_window[idx], 3] = 1  # mark as deletion
                operations[dets_idx_in_shift_window[idx], 4] = 0  # reset the shift to 0

    # (4) any detections marked as deletions and shifts, are now definitely deletions
    operations[np.nonzero(operations[:, 3:].sum(axis=1) == 2), 4] = 0

    # (5) Unnacounted annotations become insertions
    for i, ann in enumerate(annotations):
        if annotations_accounted_for[i] == 0:
            new_row = np.array([ann, 0., 1., 0., 0.])
            operations = np.vstack((operations, new_row))

    # Error checking
    if double_check_accounted(detections_accounted_for, annotations_accounted_for):
        print('ERROR')

    ae = annotation_efficiency(operations)

    return operations, ae
