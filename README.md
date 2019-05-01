# Blaze-FAT-Code

This code is intended for use with FAT testing on the BLaze instrument. It will take flow plot data files from the Blaze instrument, and analyze them. The code is intended to overlay the periodic dips in flow that the Blaze instruments experience. It takes the data, overlays and graphs it, and determines whether the run was a pass or fail for the Blaze. 
The limitations of this code are that it will not work if the dips are very small, or if the data is very noisy. In those cases, you will get unexpected results, and it may be necessary to change that value (line 22 from Blaze.py) to get the code to work.

## Instructions of Use

In order for the code to work, you must run the file <b>"Flow Graphing Code.py"</b>. This file must be in the same directory as the .txt files that you would like to analyze. These .txt files must be created by a Bronkhorst flowmeter, and must follow the required naming convention. These files should be the only .txt files in the same directory as the python code. 

The required naming convention for the script to run properly is as follows:

[Instrument name]\_[Flow Ratio]\_[Flow Rate]\_[Side]\_

The instrument name should be the instrument's ID. The Flow Ratio should be a ratio in the form of XtoY, where X and Y are numbers, and X is the number representing the left hand side. Flow Rate should give the total flow rate in the form XmL-min, where X is the flow rate in mL/min. Side refers to either RHS or LHS for the right and left hand side pushers. 

For example:

Inst1_3to1_12ml-min_RHS

Each instrument run should have two text files, one for the LHS and one for the RHS. 

The output of the file will be one graph for every run, or one graph for every two text files. The graph will have the overlaid dips in flow rate in an easy to understand way, and will clearly show whether or not the fun passed, and if not, what caused it to fail. 

The <b>Blaze.py</b> file is an ADT that is used by the <b>Flow Graphing Code.py</b> script.
