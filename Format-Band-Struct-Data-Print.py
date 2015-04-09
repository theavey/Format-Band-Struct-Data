#! /usr/bin/env python3.4

########################################################################
#                                                                      #
# This script will take a file output by abinit of a band structure    #
# and pull out the k points and the energy of the bands at those       #
# k points in a form that is pretty easy for Mathematica to interpret. #
# It takes two arguments. The first is the path to the output of       #
# abinit and the second is the desired file name for the outputted     #
# reformatted data. If the second argument is "print" it will just     #
# create a file named tmp(current time) and then print the data to     #
# stdout. This is useful if you call this script from within the       #
# Mathematica notebook.
#                                                                      #
# Known issues:                                                        #
# This will not work (as currently written) if the band energies       #
# extends past one line. It shouldn't be too hard to fix (might need   #
# to implement some state variables or something), but I haven't done  #
# it yet.                                                              #
# Also, this is very dependent on an exact output form from abinit,    #
# but I somewhat doubt that will change significantly. I am basing it  #
# on my output from abinit 7.10.4 I believe.                           #
#                                                                      #
# This script was written by Thomas Heavey in 2015.                    #
#        theavey@bu.edu     thomasjheavey@gmail.com                    #
#                                                                      #
# Copyright 2015 Thomas J. Heavey IV                                   #      
#                                                                      #
# Licensed under the Apache License, Version 2.0 (the "License");      #
# you may not use this file except in compliance with the License.     #
# You may obtain a copy of the License at                              #
#                                                                      #
#    http://www.apache.org/licenses/LICENSE-2.0                        #
#                                                                      #
# Unless required by applicable law or agreed to in writing, software  #
# distributed under the License is distributed on an "AS IS" BASIS,    #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or      #
# implied.                                                             #
# See the License for the specific language governing permissions and  #
# limitations under the License.                                       #
#                                                                      #
########################################################################




# This is written to work with python 3.4 because it should be good to
# be working on the newest version of python.

import fileinput  # allows easy iteration over a file
import sys        # For importing the arguments given
import re         # RegEx package for sorting data
import os.path    # Allows for checking if file already exists
from time import strftime  # Allows for putting time with temp file name
# Current time and date as a string:
nowtime = strftime("%Y%m%d%H%M")

# First argument is the file to take the band structure data from.
# Second argument is the output file name. If the second argument is
# "print", it will just print the output to sys.stdout. If it is the
# same time as the last time the script was run, it will overwrite
# your last tmp file, which could be good or bad.
band_s_in  = sys.argv[1]
band_s_out = sys.argv[2]

if os.path.exists(band_s_out):
    print('{} already exists!'.format(band_s_out))
    band_s_out = 'formatted_' + band_s_in
    if os.path.exists(band_s_out):
        raise IOError('pick new output file name!')
    print('Output file will instead be called {}'.format(band_s_out))

if band_s_out == "print":
    band_s_out = 'tmp' + nowtime

# Open the output file to write to
with open(band_s_out, 'w') as out_file:
    # List opening character for Mathematica:
    out_file.write('{')
    for i, line in enumerate(fileinput.input(band_s_in)):
        # First line of file, not useful
        # Note, in most places, these lines are "stripped" because
        # they come with leading spaces, which messes with
        # startswith and the split function, too I think.
        if line.strip().startswith('Eigenvalues'):
            continue
        if line.strip().startswith('kpt#'):
            if i != 1:
                out_file.write(',')
            # Make the line into a list of elements of the line
            # separated by spaces. Uses RegEx. Don't remember this
            # usage/language specifically. Just Google it.
            linelist = re.split(' {1,}',line.strip())
            # Define formatted k point coordinate
            k_point_coord = '{{' + \
              linelist[7] + ',' + \
              linelist[8] + ',' + \
              linelist[9] + '},'
            out_file.write(k_point_coord)
            continue
        # make the line into a list split by spaces
        linelist = re.split(' {1,}',line.strip())
        # Will make sure the first element of linelist is a number.
        # If it's not one of the above, it should be the eigenenergies,
        # which is just a list of numbers.
        # If it's not a number, this will raise a ValueError, I think.
        # I could catch that, but I'm not certain what I would do with
        # the line anyway. I think I want the exception raised.
        float(linelist[0])
        ee_output = '{'
        # Join eigenenergies into comma separated string list and append
        # to the line to be outputted:
        ee_output += ','.join(linelist)
        ee_output += '}}'
        out_file.write(ee_output)
        continue
    out_file.write('}')

# If "print" was given earlier, now want to print the output to stdout:
if band_s_out.startswith('tmp'):
    # Just open the file we made above,
    with open(band_s_out) as outputted_data:
        # read it, and print it.
        print(outputted_data.read())
# If not given "print", might as well make a nice little statement
# saying that something happened.
else:
    print('Band Structure data written to {}'.format(band_s_out))
