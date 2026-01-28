# json_melody_to_midi_converter.py
# Converts predefined JSON-structured melody data into MIDI files.
# Output MIDI files are saved in a "midis" subfolder and absolute paths are printed.


import os
from mido import Message, MidiFile, MidiTrack, MetaMessage, bpm2tempo


# Each melody contains:
# melody_no - identifier
# rank - evaluation rank
# order  - Markov order
# sequence - [note_name, duration_in_beats]

melodies = [
    {
        "melody_no": 8,
        "rank": "2ndbest",
        "order": 1,
        "sequence": [
            ["F#5", 0.5], ["E5", 0.5], ["C5", 1], ["B4", 1], ["C5", 1], ["D5", 0.5],
            ["G4", 1], ["F#4", 1], ["G4", 1], ["A4", 1], ["B4", 1], ["G4", 1],
            ["F#4", 1], ["G4", 0.5], ["F#4", 0.5], ["G4", 0.5]
        ]
    },
    {
        "melody_no": 16,
        "rank": "best",
        "order": 1,
        "sequence": [
            ["G4", 3], ["G4", 1], ["F#4", 1], ["G4", 0.5], ["E5", 0.5], ["C5", 1],
            ["B4", 1], ["C#5", 1], ["B4", 0.5], ["C#5", 0.5], ["A4", 0.5], ["B4", 0.5],
            ["G4", 0.5], ["G4", 0.5], ["A4", 0.5], ["G4", 0.5]
        ]
    },
    {
        "melody_no": 12,
        "rank": "2ndbest",
        "order": 2,
        "sequence": [
            ["A4", 1], ["B4", 1], ["C5", 1], ["B4", 1], ["A4", 0.5], ["B4", 0.5],
            ["C5", 1], ["B4", 0.5], ["A4", 0.5], ["G4", 0.5], ["F#4", 1], ["G4", 0.5],
            ["A4", 0.5], ["B4", 1], ["D5", 1], ["G4", 1]
        ]
    },
    {
        "melody_no": 19,
        "rank": "best",
        "order": 2,
        "sequence": [
            ["G4", 1], ["A4", 0.5], ["D4", 0.5], ["E4", 1], ["F#4", 0.5], ["G4", 0.5],
            ["D5", 0.5], ["C5", 0.5], ["B4", 1], ["A4", 1], ["B4", 1], ["C5", 3],
            ["D5", 1], ["G4", 0.5], ["F#4", 0.5], ["G4", 0.5]
        ]
    },
    {
        "melody_no": 3,
        "rank": "2ndbest_tied",
        "order": 2,
        "sequence": [
            ["C#5", 1], ["A4", 0.5], ["A4", 0.5], ["B4", 1], ["C5", 1], ["B4", 1],
            ["A4", 1], ["G4", 1], ["F#4", 1], ["G4", 1], ["A4", 1], ["B4", 1],
            ["C5", 1], ["B4", 0.5], ["A4", 0.5], ["G4", 0.5]
        ]
    },
    {
        "melody_no": 5,
        "rank": "3rdbest",
        "order": 1,
        "sequence": [
            ["G5", 0.5], ["G4", 1], ["F#4", 3], ["G4", 1], ["A4", 0.5], ["G4", 1],
            ["F#4", 0.5], ["G4", 0.5], ["C5", 1], ["D5", 0.5], ["G4", 0.5], ["D5", 0.5],
            ["E5", 0.5], ["F#5", 1], ["G5", 0.5], ["G4", 0.5]
        ]
    }
]

# Pitch-to-MIDI mapping
BASE_MAP = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}

def note_to_midi(name: str) -> int:
    """
    Convert note string (e.g., 'C4', 'F#5') to MIDI note number.
    Assumes format: letter + optional '#' + octave (e.g., C4, F#5).
    """
    s = name.strip().upper()

    # Parse optional sharp accidental ('#')
    if len(s) >= 3 and s[1] == '#':
        base = s[0]
        octave = int(s[2:])
        semitone = BASE_MAP[base] + 1
    else:
        base = s[0]
        octave = int(s[1:])
        semitone = BASE_MAP[base]

    # MIDI formula: C4 = 60
    return 12 * (octave + 1) + semitone

def beats_to_ticks(mid_obj, beats: float) -> int:
    """
    Convert duration in beats to MIDI ticks.
    """
    return int(beats * mid_obj.ticks_per_beat)

def write_melody_to_midi(melody_dict, filename, bpm=120):
    """
    Write a single melody dictionary to a MIDI file.
    """
    mid = MidiFile(ticks_per_beat=480) # Timing resolution: 480 ticks per beat
    track = MidiTrack()
    mid.tracks.append(track)

    # Tempo and instrument setup
    track.append(MetaMessage('set_tempo', tempo=bpm2tempo(bpm), time=0))
    track.append(Message('program_change', program=0, time=0))  # Acoustic Grand Piano

    # Monophonic rendering: next note starts immediately after previous note ends
    for note_name, dur in melody_dict["sequence"]:
        midi_note = note_to_midi(note_name)
        track.append(Message('note_on', note=midi_note, velocity=90, time=0))
        track.append(
            Message(
                'note_off',
                note=midi_note,
                velocity=64,
                time=beats_to_ticks(mid, float(dur))
            )
        )

    mid.save(filename)
    print("written:", os.path.abspath(filename))


# Ensure output directory exists
out_dir = "midis"
os.makedirs(out_dir, exist_ok=True)

# Convert all melodies to MIDI
for mel in melodies:
    rank = mel.get("rank", "unknown").replace(" ", "_")
    order = mel.get("order", 1)
    outname = os.path.join(
        out_dir,
        f"melody_{mel['melody_no']}_{rank}_order{order}.mid"
    )
    write_melody_to_midi(mel, outname)
