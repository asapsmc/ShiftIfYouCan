import numpy as np


def delete_idx_from_list(my_list, indexes):
    """
    Helper to delete an arbitrary collection of indexes.
    Note: delete them in reverse order so not to lose the subsequent indexes.
    """
    for index in sorted(indexes, reverse=True):
        del my_list[index]
    return my_list


def dimx(a):
    """
    Helper to get the "shape" of a multidimensional list
    """
    if not type(a) == list:
        return []
    return [len(a)] + dimx(a[0])


def double_check_accounted(acc_det, acc_ann):
    result = False
    if np.max(acc_det) > 1:
        print(f'ERROR: detections_accounted_for) > 1 in pos: {np.argmax(acc_det)}')
        result = True

    if np.max(acc_ann) > 1:
        print(f'ERROR: annotations_accounted_for) > 1 in pos: {np.argmax(acc_ann)}')
        result = True
    return result


def _compare_objects(obj1, obj2):
    """
    FIXME:
    CALL: print(f'compare_objects (ops2,operations): {_compare_objects (ops2,operations)}')
    DEBUG Helper to compare 2 numpy arrays
    """
    result = (obj1 == obj2).all()
    return result
