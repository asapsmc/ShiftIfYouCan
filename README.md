# ShiftIfYouCan

Code Repository for ISMIR 2020 LBD Contribution "Shift if you can: Counting and visualising correction operations for beat tracking evaluation".  
We provide a straightforward calculation of *annotation efficiency* based on counting the number of shifts, insertions, and deletions, and pair it with an informative visualisation suited for the qualitative evaluation of beat tracking systems. It graphically displays the minimum set and type of operations required to transform a sequence of initial beat detections in such a way as to maximize the F-measure when comparing the transformed detections against a ground truth annotation sequence.

## Installation and Usage

To use this library, the user should first clone this repository to the working python directory.

The library can be imported with `...`.

## Dependencies:

* Scipy/Numpy

## Example Code

A detailed example on how to use the TIV.lib is available in [ShiftIfYouCan_example.ipynb](ShiftIfYouCan_example.ipynb).

### 3rd Party Code

On the examples provided we used and/or adapted the following two external functions, which can be found along all relevant information in the module *ext_libraries.py*.
- **variations**, that provides variations of a given beat sequence; 
- **f-measure**, that provides the f-measure of a given pair of beat detections and annotations.

## Authors

António Sá Pinto
antoniosapinto@gmail.com

Matthew E. P. Davies
mepdavies@gmail.com