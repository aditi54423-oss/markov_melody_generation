# music_theory_scorecard.py (objective evaluation program)
# Note Input format: pitch tokens must be {letter}{optional #}{octave} using ASCII '#', e.g., F#5.
# Rests and flat spellings (e.g., Bb) are not supported in this implementation.
# Paths are configured for the author’s local machine; adjust ORDER1_PATH/ORDER2_PATH as needed.


import json
import csv
import os
from collections import Counter

# CONFIGURATION
# Paths to the JSON files containing Markov-generated melodies of order 1 and order 2
ORDER1_PATH = r"C:\Users\Poonam\Desktop\Markov\new_markov (with minuet in g)\minuet_melody_order1.json"
ORDER2_PATH = r"C:\Users\Poonam\Desktop\Markov\new_markov (with minuet in g)\minuet_melody_order2.json"

# Output directory and CSV file path for evaluation results
OUT_DIR  = os.path.dirname(ORDER1_PATH)
OUT_CSV  = os.path.join(OUT_DIR, "final_eval_results.csv")

# Weights for different evaluation metrics when calculating the final score
WEIGHTS = {
  "ending_on_tonic": 0.173,
  "interval_smoothness": 0.227,
  "stepwise_ratio": 0.153,
  "motif_repetition": 0.250,
  "rhythmic_variety": 0.197
}

# Pitch-class mapping for note spellings used in the dataset (G major / D major pitch set).

PCLASS = {
    "C": 0,
    "C#": 1,
    "D": 2,
    "E": 4,
    "F": 5,
    "F#": 6,
    "G": 7,
    "A": 9,
    "B": 11
}

MIN_NOTES = 3  # Minimum length for a sequence to qualify as a motif

# HELPER FUNCTIONS FOR PITCH NORMALIZATION

def normalize_seq(mel):
    """
    Normalize a melody sequence.
    Expects a list of [pitch, duration] tokens.
    - Converts durations to float.
    - Rejects rests and invalid entries.
    """
    normalized = []
    for token in mel["sequence"]:
        if not isinstance(token, (list, tuple)) or len(token) != 2:
            raise ValueError(f"Each sequence token must be [pitch, dur]; got: {token!r}")
        note, dur = token
        if note is None:
            raise ValueError("Note cannot be None")
        note_s = str(note)
        if note_s == "REST" or note_s.startswith("REST"):
            raise ValueError(f"Rests are not supported; found token: {token!r}")
        try:
            dur_f = float(dur)
        except Exception as e:
            raise ValueError(f"Duration must be numeric for token {token!r}: {e}")
        normalized.append([note_s, dur_f])
    return normalized

def pitch_stream(seq):
    """Return the sequence of pitch names (ignoring durations)."""
    return [t[0] for t in seq]

def durations_numeric(seq):
    """Return the sequence of numeric durations."""
    return [t[1] for t in seq]

# MIDI CONVERSION
def note_to_number(note):
    """
    Convert a normalized pitch string to MIDI number (C4 = 60).
    Formula: MIDI = 60 + semitone_offset + 12*(octave - 4)
    Flats are unsupported; octave must be specified.
    """
    s = note
    if not s:
        raise ValueError("Empty note string")
    i = len(s)
    while i > 0 and s[i-1].isdigit():
        i -= 1
    name = s[:i]
    if i < len(s):
        octv = int(s[i:])
    else:
        raise ValueError(f"Octave required in note string: {note!r}")
    if name not in PCLASS:
        raise ValueError(f"Unknown or unsupported pitch name: {name!r}")
    semitone_offset = PCLASS[name]
    midi = 60 + semitone_offset + 12 * (octv - 4)
    return midi

def midi_stream(seq):
    """Convert an entire pitch sequence to MIDI numbers."""
    return [note_to_number(p) for p in pitch_stream(seq)]

def intervals_from_midi(midi_nums):
    """Compute intervals (in semitones) between consecutive MIDI notes."""
    return [midi_nums[i+1] - midi_nums[i] for i in range(len(midi_nums)-1)]


#EVALUATION METRICS 

def find_all_repeated_subsequences(stream, L):
    """
    Identify repeated subsequences of length L within a sequence.
    Ignores trivial sequences where all values are identical.
    Returns a list of dicts with subsequence and indices.
    """
    if L <= 0:
        return []
    n = len(stream)
    seen = {}
    occurrences = {}
    for i in range(n - L + 1):
        sub = tuple(stream[i:i+L])
        if len(set(sub)) == 1:  # skip trivial repeats
            continue
        if sub in seen:
            if sub not in occurrences:
                occurrences[sub] = [seen[sub]]
            occurrences[sub].append(i)
        else:
            seen[sub] = i
    return [{"subsequence": list(sub), "indices": idxs} for sub, idxs in occurrences.items()]

def motif_repetition(seq, iv, durs):
    """
    Detect repeated motifs in a sequence:
      - Intervallic (iv) motifs: score 1.0
      - Melodic (pitch) motifs: score 0.8
      - Rhythmic motifs: score 0.5
    When multiple motifs are found, take the higher-graded one.
    Returns: list of found motif types, chosen score, and motif details.
    """
    pitch_seq = pitch_stream(seq)
    details = {}
    found_types = []

    max_k = min(8, len(pitch_seq))
    if max_k < MIN_NOTES:
        return found_types, 0.0, details

    for k in range(max_k, MIN_NOTES-1, -1):
        L_iv = k - 1
        if L_iv >= 1 and len(iv) >= L_iv:
            iv_occ = find_all_repeated_subsequences(iv, L_iv)
            if iv_occ:
                details.setdefault("intervallic", []).extend(iv_occ)
                if "intervallic" not in found_types:
                    found_types.append("intervallic")

        if len(pitch_seq) >= k:
            p_occ = find_all_repeated_subsequences(pitch_seq, k)
            if p_occ:
                details.setdefault("melodic", []).extend(p_occ)
                if "melodic" not in found_types:
                    found_types.append("melodic")

        if len(durs) >= k:
            r_occ = find_all_repeated_subsequences(durs, k)
            if r_occ:
                details.setdefault("rhythmic", []).extend(r_occ)
                if "rhythmic" not in found_types:
                    found_types.append("rhythmic")

    chosen_score = 0.0
    if "intervallic" in found_types:
        chosen_score = 1.0
    elif "melodic" in found_types:
        chosen_score = 0.8
    elif "rhythmic" in found_types:
        chosen_score = 0.5

    return found_types, chosen_score, details


def normalize_base_name(p):
    """Return the pitch class (name) without octave, normalized."""
    s = p
    i = len(s)
    while i>0 and s[i-1].isdigit(): i-=1
    return s[:i]

def ending_on_tonic(seq):
    """
    Evaluate whether melody ends on tonic:
      - Special condition: last 8 notes may indicate D major.
      - Otherwise, G major is assumed.
    Only D major and G major are considered, since the training melody is restricted to these key signatures.
    Returns score (0.0 or 1.0) and last note.
    """
    pts = pitch_stream(seq)
    if not pts:
        return 0.0, None
    last8 = pts[-8:]
    base_counts = Counter(normalize_base_name(p) for p in last8)
    cond_csharp = base_counts.get("C#", 0) >= 2
    cond_d = base_counts.get("D", 0) >= 2
    cond_a_or_fsharp = (base_counts.get("A", 0) >= 1) or (base_counts.get("F#", 0) >= 1)
    if cond_csharp and cond_d and cond_a_or_fsharp:
        tonic = "D"
        last_root = normalize_base_name(pts[-1])
        return (1.0 if last_root == tonic else 0.0), pts[-1]
    else:
        tonic = "G"
        last_root = normalize_base_name(pts[-1])
        return (1.0 if last_root == tonic else 0.0), pts[-1]

def interval_smoothness(iv):
    """
    Evaluate melodic smoothness based on large intervallic leaps (>7 semitones).
    Scoring:
      - <2 large leaps: 1.0 (smooth contour)
      - 2 large leaps: 0.5 (moderately smooth)
      - >2 large leaps: 0.0 (disjointed contour)
    """
    leaps = sum(1 for d in iv if abs(d) > 7)
    return (0.0 if leaps > 2 else (0.5 if leaps == 2 else 1.0)), leaps

def stepwise_ratio(iv):
    """
    Evaluate the prevalence of stepwise motion (≤2 semitones).
    Scoring:
      - ≥9 stepwise intervals: 1.0 (predominantly stepwise)
      - 6–8 stepwise intervals: 0.5 (moderate stepwise motion)
      - <6 stepwise intervals: 0.0 (predominantly leap-based)
    """
    steps = sum(1 for d in iv if abs(d) <= 2)
    return (1.0 if steps >= 9 else (0.5 if 6 <= steps <= 8 else 0.0)), steps

def rhythmic_variety(durs):
    """
    Assess rhythmic variety based on the number of distinct durations and repetition:
      - >11 identical durations: 0.0 (Excessive repetition)
      - 2 or 5 distinct durations: 0.5 (Moderate variety)
      - 3–4 distinct durations: 1.0 (Balanced variety)
    """

    distinct = set(durs)
    counts = Counter(durs)
    max_same = max(counts.values()) if counts else 0
    n_dist = len(distinct)
    if max_same > 11: return 0.0
    if n_dist in (2,5): return 0.5
    if 3 <= n_dist <= 4: return 1.0
    return 0.0

# ---------- MAIN EVALUATION FUNCTION ----------
def evaluate_sequence(seq):
    """
    Compute all evaluation metrics for a normalized sequence and return detailed results including weighted final score.
    """
    midi_seq = midi_stream(seq)
    iv = intervals_from_midi(midi_seq)
    int_score, _   = interval_smoothness(iv)
    step_score, _  = stepwise_ratio(iv)
    durs = durations_numeric(seq)
    rv_score = rhythmic_variety(durs)
    end_score, _ = ending_on_tonic(seq)
    found_types, motif_score, motif_details = motif_repetition(seq, iv, durs)

    final = (
        WEIGHTS["ending_on_tonic"]      * end_score  +
        WEIGHTS["interval_smoothness"]  * int_score  +
        WEIGHTS["stepwise_ratio"]       * step_score +
        WEIGHTS["motif_repetition"]     * motif_score +
        WEIGHTS["rhythmic_variety"]     * rv_score
    )

    return {
        "ending_on_tonic": end_score,
        "interval_smoothness": int_score,
        "stepwise_ratio": step_score,
        "motif_repetition": motif_score,
        "motif_types": found_types,
        "motif_details": motif_details,
        "rhythmic_variety": rv_score,
        "final_weighted": final
    }

# ---------- FILE INPUT / OUTPUT ----------
def load_json(path):
    """Load JSON data from file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def process_file(path, label):
    """
    Process a JSON file of melodies:
      - Normalize sequences
      - Evaluate metrics
      - Return list of results per melody
    """
    rows = []
    data = load_json(path)
    for m in data:
        seq = normalize_seq(m)
        out = evaluate_sequence(seq)
        rows.append([label, m.get("melody_no", ""), out])
    return rows

def _write_table(writer, rows, label):
    """
    Write evaluation table for a single order to CSV.
    Includes per-melody metrics and average summary row.
    """
    header = ["Melody No", "Ending On Tonic", "Interval Smoothness", "Stepwise Ratio",
              "Motif Repetition", "Rhythmic Variety", "Final Weighted"]
    writer.writerow([label])  # section label row
    writer.writerow(header)
    per_melody_finals = []
    for r in rows:
        melno = r[1]
        out = r[2]
        ending = out.get("ending_on_tonic", 0.0)
        interval = out.get("interval_smoothness", 0.0)
        step = out.get("stepwise_ratio", 0.0)
        motif = out.get("motif_repetition", 0.0)
        rhythmic = out.get("rhythmic_variety", 0.0)
        final = out.get("final_weighted", 0.0)
        per_melody_finals.append(final)
        writer.writerow([melno, ending, interval, step, motif, rhythmic, final])
    # Section summary row
    if per_melody_finals:
        avg_ending = sum(out.get("ending_on_tonic",0.0) for _,_,out in rows) / len(rows)
        avg_interval = sum(out.get("interval_smoothness",0.0) for _,_,out in rows) / len(rows)
        avg_step = sum(out.get("stepwise_ratio",0.0) for _,_,out in rows) / len(rows)
        avg_motif = sum(out.get("motif_repetition",0.0) for _,_,out in rows) / len(rows)
        avg_rhyth = sum(out.get("rhythmic_variety",0.0) for _,_,out in rows) / len(rows)
        avg_final = sum(per_melody_finals) / len(per_melody_finals)
        writer.writerow([])  # blank line
        writer.writerow(["Averages", avg_ending, avg_interval, avg_step, avg_motif, avg_rhyth, avg_final])
    writer.writerow([])  # blank line after table
    return avg_final

# MAIN SCRIPT
def main():
    """
    Process both order 1 and order 2 melody files and output CSV with:
      - Per-melody metrics
      - Average metrics per order
      - Final weighted scores
    """
    rows1 = process_file(ORDER1_PATH, "order1")
    rows2 = process_file(ORDER2_PATH, "order2")

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        o1_final_avg = _write_table(w, rows1, "Order 1")
        o2_final_avg = _write_table(w, rows2, "Order 2")
        # Write final average summary
        w.writerow(["order1_avg", "", "", "", "", "", o1_final_avg])
        w.writerow(["order2_avg", "", "", "", "", "", o2_final_avg])

    if rows1:
        print("AVERAGE (order1 final weighted) =", o1_final_avg)
    if rows2:
        print("AVERAGE (order2 final weighted) =", o2_final_avg)
    print("\nSaved CSV to:\n", OUT_CSV)

if __name__ == "__main__":
    main()
