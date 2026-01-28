# order2_melody generator (second-order Markov)
# Builds empirical second-order Markov transition probabilities from a single melody sequence (count-and-normalize).
# Pitch and rhythm are modeled separately using independent Markov chains and combined afterward. Thus, pitch–rhythm dependency is not modeled.
# Generates 20 melodies of 16 note-events each using probabilistic sampling (Python random library).
# Stochastic sampling is used without a fixed random seed, allowing melody outputs to vary across runs.
# Pitch encoding: {letter}{optional #}{octave} (e.g., G4, F#5). Durations are in beats.

import random
import json

# Training melody pitches 
pitches = [
    "D5","G4","A4","B4","C5","D5","G4","G4","E5","C5","D5","E5","F#5","G5","G4","G4",
    "C5","D5","C5","B4","A4","B4","C5","B4","A4","G4","F#4","G4","A4","B4","G4","A4",
    "D5","G4","A4","B4","C5","D5","G4","G4","E5","C5","D5","E5","F#5","G5","G4","G4",
    "C5","D5","C5","B4","A4","B4","C5","B4","A4","G4","A4","B4","A4","G4","F#4","G4",
    "B4","G4","A4","B4","G4","A4",
    "D5","E5","F#5","D5",
    "G5","E5","F#5","G5","D5",
    "C#5","B4","C#5","A4",
    "A4","B4","C#5","D5","E5","F#5",
    "G5","F#5","E5","F#5",
    "A4","C#5","D5",
    "D5","G4","F#4","G4",
    "E5","G4","F#4","G4",
    "D5","C5","B4",
    "A4","G4","F#4","G4","A4",
    "D4","E4","F#4","G4","A4","B4",
    "C5","B4","A4",
    "B4","D5","G4","F#4","G4"
]

# Corresponding rhythmic durations (in beats)
rhythm = [
    1,0.5,0.5,0.5,0.5,1,1,1,1,0.5,0.5,0.5,0.5,1,1,1,
    1,0.5,0.5,0.5,0.5,1,0.5,0.5,0.5,0.5,1,0.5,0.5,0.5,0.5,3,
    1,0.5,0.5,0.5,0.5,1,1,1,1,0.5,0.5,0.5,0.5,1,1,1,
    1,0.5,0.5,0.5,0.5,1,0.5,0.5,0.5,0.5,1,0.5,0.5,0.5,0.5,3,
    1,0.5,0.5,0.5,0.5,1,
    0.5,0.5,0.5,0.5,
    1,0.5,0.5,0.5,0.5,
    1,0.5,0.5,1,
    0.5,0.5,0.5,0.5,0.5,0.5,
    1,1,1,1,
    1,1,3,
    1,0.5,0.5,1,
    1,0.5,0.5,1,
    1,1,1,
    0.5,0.5,0.5,0.5,1,
    0.5,0.5,0.5,0.5,0.5,0.5,
    1,1,1,
    0.5,0.5,1,1,
    3
]
assert len(pitches) == len(rhythm), "Training pitch and rhythm streams must be aligned."


# Second-order Markov model functions

def build_second_order_chain(seq):
    """
    Construct a second-order Markov chain from a sequence.
    Returns a dictionary mapping each pair of consecutive elements to a list of (next_element, probability).
    """
    trans = {}
    for i in range(len(seq)-2):
        pair = (seq[i], seq[i+1])
        nxt = seq[i+2]
        trans.setdefault(pair, []).append(nxt)
    chain = {}
    for pair, lst in trans.items():
        freq = {}
        for x in lst:
            freq[x] = freq.get(x, 0) + 1
        s = sum(freq.values())
        # Normalize counts to probabilities
        chain[pair] = [(k, freq[k]/s) for k in freq]
    return chain

def generate_sequence(chain, length, starting_pair=None):
    """
    Generate a sequence from a second-order Markov chain.
    If the starting pair exists in the chain, generation starts from it; otherwise a random valid pair is used.
    Returns a list of length `length`.
    """
    keys = list(chain.keys())
    curr = starting_pair if (starting_pair in chain) else random.choice(keys)
    out = [curr[0], curr[1]]
    for _ in range(length-2):
        nxts = chain.get(curr)
        if not nxts:
            # fallback: if current state pair has no outgoing transitions, restart from a random valid state pair
            curr = random.choice(keys)
            out.append(curr[1])
        else:
            choices, probs = zip(*nxts)
            nxt = random.choices(choices, probs)[0]
            out.append(nxt)
            # shift pair window for next iteration
            curr = (curr[1], nxt)
    return out

def zip_notes_rhythms(notes, rhythms):
    """Combine generated pitches and durations into a sequence of [note, duration] pairs."""
    return [[n, r] for n, r in zip(notes, rhythms)]

# Build second-order Markov chains for pitches and rhythms
note_chain = build_second_order_chain(pitches)
rhythm_chain = build_second_order_chain(rhythm)

# Generate 20 synthetic melodies (each 16 notes long)
melodies = []
for i in range(1, 21):
    # Pick random starting indices for 2-note / 2-duration seeds
    iN = random.randint(0, len(pitches)-2)
    iR = random.randint(0, len(rhythm)-2)
    n_start = (pitches[iN], pitches[iN+1])
    r_start = (rhythm[iR], rhythm[iR+1])
    # Generate sequences using second-order Markov chain
    n_seq = generate_sequence(note_chain, 16, n_start)
    r_seq = generate_sequence(rhythm_chain, 16, r_start)
    melodies.append({"melody_no": i, "sequence": zip_notes_rhythms(n_seq, r_seq)})

# Export generated melodies to JSON
with open("order2_melodies.json", "w") as f:
    json.dump(melodies, f, indent=2)
