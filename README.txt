# markov_melody_generation
README

This archive contains the supplementary materials for the research project "Comparing First-Order and Second-Order Markov Chains for Algorithmic Melody Generation".
The materials are provided to support reproducibility and transparency of the melody generation, evaluation, and analysis described in the paper.

Directory Structure

Supplementary_Code/
This folder contains four Python programs used in the study: first-order and second-order Markov melody generators, objective evaluation program (music-theory-based scorecard), and a JSON melody-to-MIDI converter.
The melody generators build transition tables from the training melody, generate 20 monophonic melodies each of fixed length (16 notes) and export them into JSON-encoded melodies. Pitch and rhythm are modelled as independent parallel sequences, as described in the Methods section of the paper.
The evaluation program (music_theory_scorecard)computes weighted scores for each melody based on multiple music-theory criteria and outputs the results in CSV format.
The JSON-to-MIDI converter maps pitch and duration tokens to MIDI notes. The MIDI files were later converted to mp3 audio files for subjective evaluation through a survey.

Supplementary_Data/
This folder contains JSON-encoded melodies, results of both subjective and objective evaluation in CSV format, and MIDI files of melodies used for subjective evaluation (Group A and Group B melodies).
A PDF containing screenshots of the online survey interface used for subjective evaluation is also included in this folder.
Images/
This folder contains the figures used in the paper in PNG format.

Note: All file paths in the program are specified relative to the author’s local file system and may need to be updated to match the user’s directory structure before execution.

Software Requirements
All programs were written in Python. Standard python libraries were used, except for the external library mido that was used for converting JSON melodies into MIDI.
