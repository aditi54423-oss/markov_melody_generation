README
This repository contains supplementary materials for the research project “Comparing First-Order and Second-Order Markov Chains for Algorithmic Melody Generation.”
The materials are provided to support reproducibility and transparency of the melody generation and evaluation processes described in the paper.

This repository includes:
Python programs implementing first-order and second-order Markov chain melody generators, an objective evaluation program (music-theory-based scorecard), and a JSON melody-to-MIDI converter.
The melody generators construct transition tables from the training melody, generate 20 monophonic melodies per model of fixed length (16 notes), and export them as JSON-encoded melodies. Pitch and rhythm are modelled as independent parallel sequences, as described in the Methods section of the paper.
The evaluation program (music_theory_scorecard) computes weighted scores for each melody based on multiple music-theory criteria and outputs the results in CSV format.
The JSON-to-MIDI converter maps pitch and duration tokens to MIDI notes.
It also consists of two JSON files containing melodies produced by the first-order and second-order Markov models.

Note on File Paths
All file paths in the programs are specified relative to the author’s local file system and may need to be updated to match the user’s directory structure before execution.

Software Requirements
All programs were written in Python. Standard Python libraries are used, with the exception of the external library mido, which is required for converting JSON-encoded melodies into MIDI format.
