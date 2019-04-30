# Blaze-FAT-Code

This code is intended for use with FAT testing on the BLaze instrument. It will take flow plot data files from the Blaze instrument, and analyze them. The code is intended to overlay the periodic dips in flow that the Blaze instruments experience. It takes the data, overlays and graphs it, and determines whether the run was a pass or fail for the Blaze. 
The limitations of this code are that it will not work if the dips are very small, or if the data is very noisy. In those cases, you will get unexpected results, and it may be necessary to change that value (line 22 from Blaze.py) to get the code to work.
