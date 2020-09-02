# ShiftIfYouCan

Code Repository for ISMIR 2020 LBD Contribution "Shift if you can: Counting and visualising correction operations for beat tracking evaluation".  
We provide a straightforward calculation of *annotation efficiency* based on counting the number of shifts, insertions, and deletions, and pair it with an informative visualisation suited for the qualitative evaluation of beat tracking systems. It graphically displays the minimum set and type of operations required to transform a sequence of initial beat detections in such a way as to maximize the F-measure when comparing the transformed detections against a ground truth annotation sequence.

## Installation and Usage

To use this library, the user should first clone this repository to the working python directory.

The library can be imported with `...`.

## Dependencies:

* Numpy

## Example Code

Two detailed examples on how to use this code are provided: 
*
* [ShiftIfYouCan_notebook.ipynb](ShiftIfYouCan_notebook.ipynb) where we present a walkthrough example for the ShiftIfYouCan visualisation code;
*  [example_script.py](example_script.py): this script provides an example of how to create a list of variations of beat detections,
and process it with the corresponding ground-truth annotation. It saves the transformed beat detections, as well as all the corresponding 
visualisation plots as *.png files in the /figures/ folder.
For each of the variations, it calculates the following:
     * annotation efficiency;
     * f-measure;
     * transformed beat detections and corresponding f-measure;


## Authors

António Sá Pinto
antoniosapinto@gmail.com

Matthew E. P. Davies
mepdavies@gmail.com