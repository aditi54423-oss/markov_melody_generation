# order1_melody generator (first-order Markov)
# Builds empirical first-order Markov transition probabilities from a single melody sequence (count-and-normalize).
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

# Corresponding rhythmic durations
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



# First-order Markov model functions
def build_first_order_chain(seq):
    """
    Construct a first-order Markov chain from a sequence.
    Returns a dictionary mapping each element to a list of (next_element, probability).
    """
    trans = {}
    for i in range(len(seq)-1):
        a, b = seq[i], seq[i+1]
        trans.setdefault(a, []).append(b)
    chain = {}
    for a, lst in trans.items():
        freq = {}
        for x in lst:
            freq[x] = freq.get(x, 0) + 1
        s = sum(freq.values())
        # Normalize counts to probabilities
        chain[a] = [(k, freq[k]/s) for k in freq]
    return chain

def generate_sequence(chain, length, start_state=None):
    """
    Generate a sequence of given length from a first-order Markov chain.
    If starting state is a valid state in the chain, generation starts from it; otherwise a random valid start state is used.
    """
    keys = list(chain.keys())
    curr = start_state if (start_state in chain) else random.choice(keys)
    out = [curr]
    for _ in range(length-1):
        nxts = chain.get(curr)
        if not nxts:
            # fallback: if current state has no outgoing transitions, restart from a random valid state
            curr = random.choice(keys)
        else:
            choices, probs = zip(*nxts)
            curr = random.choices(choices, probs)[0]
        out.append(curr)
    return out

def zip_notes_rhythms(notes, rhythms):
    """
    Combine generated pitches and durations into a sequence of [note, duration] pairs.
    """
    return [[n, r] for n, r in zip(notes, rhythms)]

# Build Markov chains for pitches and rhythms
note_chain = build_first_order_chain(pitches)
rhythm_chain = build_first_order_chain(rhythm)

# Generate 20 synthetic melodies (each 16 notes long)
melodies = []
for i in range(1, 21):
    n_start = random.choice(pitches)
    r_start = random.choice(rhythm)
    n_seq = generate_sequence(note_chain, 16, n_start)
    r_seq = generate_sequence(rhythm_chain, 16, r_start)
    melodies.append({"melody_no": i, "sequence": zip_notes_rhythms(n_seq, r_seq)})

# Export generated melodies to JSON
with open("order1_melodies.json", "w") as f:
    json.dump(melodies, f, indent=2)
