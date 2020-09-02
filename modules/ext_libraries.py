import numpy as np


def variations(sequence, offbeat=True, double=True, half=True,
               triple=True, third=True):
    """
    Create variations of the given beat sequence.

    Parameters
    ----------
    sequence : numpy array
        Beat sequence.
    offbeat : bool, optional
        Create an offbeat sequence.
    double : bool, optional
        Create a double tempo sequence.
    half : bool, optional
        Create half tempo sequences (includes offbeat version).
    triple : bool, optional
        Create triple tempo sequence.
    third : bool, optional
        Create third tempo sequences (includes offbeat versions).

    Returns
    -------
    sequences: list
        Beat sequence variations.
    type_sequences: list of str
        Type of beat sequence variations.

        ['Original',
         'Offbeat',
         'Double',
         'Half-odd',
         'Half-even',
         'Triple',
         'Third-1',
         'Third-2',
         'Third-3']
    """
    # Adapted from:
    #
    # https://github.com/CPJKU/madmom/blob/master/madmom/evaluation/beats.py
    #
    # Copyright (c) 2012-2014 Department of Computational Perception,
    # Johannes Kepler University, Linz, Austria and Austrian Research Institute for
    # Artificial Intelligence (OFAI), Vienna, Austria.
    # All rights reserved.

    # create different variants of the annotations
    sequences = []
    sequences.append(sequence)

    # register the variants created
    type_sequences = []
    type_sequences.append('Original')

    # double/half and offbeat variation
    if double or offbeat:
        if len(sequence) == 0:
            # if we have an empty sequence, there's nothing to interpolate
            double_sequence = []
        else:
            # create a sequence with double tempo
            same = np.arange(0, len(sequence))
            # request one item less, otherwise we would extrapolate
            shifted = np.arange(0, len(sequence), 0.5)[:-1]
            double_sequence = np.interp(shifted, same, sequence)
        # same tempo, half tempo off
        if offbeat:
            sequences.append(double_sequence[1::2])
            type_sequences.append('Offbeat')
        # double/half tempo variations
        if double:
            # double tempo
            sequences.append(double_sequence)
            type_sequences.append('Double')
    if half:
        # half tempo odd beats (i.e. 1,3,1,3,..)
        sequences.append(sequence[0::2])
        type_sequences.append('Half-Odd')
        # half tempo even beats (i.e. 2,4,2,4,..)
        sequences.append(sequence[1::2])
        type_sequences.append('Half-Even')
    # triple/third tempo variations
    if triple:
        if len(sequence) == 0:
            # if we have an empty sequence, there's nothing to interpolate
            triple_sequence = []
        else:
            # create a annotation sequence with triple tempo
            same = np.arange(0, len(sequence))
            # request two items less, otherwise we would extrapolate
            shifted = np.arange(0, len(sequence), 1. / 3)[:-2]
            triple_sequence = np.interp(shifted, same, sequence)
        # triple tempo
        sequences.append(triple_sequence)
        type_sequences.append('Triple')

    if third:
        # third tempo 1st beat (1,4,3,2,..)
        sequences.append(sequence[0::3])
        type_sequences.append('Third-1')
        # third tempo 2nd beat (2,1,4,3,..)
        sequences.append(sequence[1::3])
        type_sequences.append('Third-2')
        # third tempo 3rd beat (3,2,1,4,..)
        sequences.append(sequence[2::3])
        type_sequences.append('Third-3')
    # return
    return sequences, type_sequences


def f_measure(annotations, detections, inn_tol_win=0.07):
    """
    Calculates the F-measure as used in (Dixon, 2006) and (Dixon, 2007).

    @param anns sequence of ground truth beat annotations (in seconds)
    @param beats sequence of estimated beat times (in seconds)

    @returns f - the F-measure
    """
    # Adapted from:
    #
    # https://github.com/adamstark/Beat-Tracking-Evaluation-Toolbox/blob/master/beat_evaluation_toolbox.py
    #
    # (c) 2009 Matthew Davies
    # Python implementation by Adam Stark 2011-2012

    minBeatTime = 0

    # remove detections and annotations that are within the first 5 seconds
    annotations = annotations[np.where(annotations >= minBeatTime)]
    detections = detections[np.where(detections >= minBeatTime)]

    # number of false positives
    fp = 0

    # number of false negatives
    fn = 0

    # number of correct detections
    hits = 0

    # Check if there are any detections, if not then exit
    if detections.size == 0:
        print("beat sequence is empty, assigning zero to all outputs [f,p,r,a]")
        f = 0
        return f

    # get the threshold parameter for the tolerance window
    delta = inn_tol_win

    for i in range(annotations.size):
        # set up range of tolerance window
        windowMin = annotations[i] - delta
        windowMax = annotations[i] + delta

        # find those detections which are in the range of the tolerance window
        # [a1,a2,a3] = find(and(detections>=windowMin, detections<=windowMax));
        detectionsinwindow = []
        detectionstoadd = []
        for j in range(detections.size):
            if (detections[j] >= windowMin) and (detections[j] <= windowMax):
                detectionstoadd.append(j)

        # now remove these detections so it can't be counted again
        for k in range(len(detectionstoadd)):
            detectionsinwindow.append(detectionstoadd[k])
            detections = np.delete(detections, detectionstoadd[k])

        if (len(detectionsinwindow) == 0):      # no detections in window, therefore it's a false negative
            fn = fn + 1
        elif(len(detectionsinwindow) > 1):       # false positive case, more than one beat in a tolerance window
            hits = hits+1
            fp = fp + 1
        else:                               # only one beat in the tolerance window therefore a correct detection
            hits = hits+1

    # add any remaining detections to the number of false positives
    fp = fp + detections.size

    # calculate precision, p
    if ((hits + fp) > 0):
        p = (hits / (hits+fp))
    else:
        p = 0

    # calculate recall, r
    if ((hits + fn) > 0):
        r = ((hits)/(hits+fn))
    else:
        r = 0

    # now calculate the f-measure
    if ((p + r) > 0):
        f = 2 * p*r/(p+r)
    else:
        f = 0

    return f
