import math
from collections import Counter

def shannon_entropy(symbols):
    """Compute Shannon entropy H(X) in bits for a sequence of discrete symbols."""
    total = len(symbols)
    if total == 0:
        return 0.0
    counts = Counter(symbols)
    entropy = 0.0
    for count in counts.values():
        p = count / total
        entropy -= p * math.log2(p)
    return entropy

def mutual_information(sender_signals, receiver_responses):
    """
    Compute Mutual Information I(S; R) = H(S) + H(R) - H(S, R) in bits.
    Measures how many bits of information the receiver's response carries
    about the sender's signal.
    """
    pairs = tuple(zip(sender_signals, receiver_responses))
    h_s = shannon_entropy(sender_signals)
    h_r = shannon_entropy(receiver_responses)
    h_sr = shannon_entropy(pairs)
    mi = h_s + h_r - h_sr
    return h_s, h_r, h_sr, mi

if __name__ == "__main__":
    # Example interaction log from a robot-to-robot trial
    # (Students replace these lists with live logged events from their robots)
    sender_log   = ("ALARM", "GREET", "SEARCH", "ALARM", "GREET", "GREET", "SEARCH", "ALARM")
    receiver_log = ("RETREAT", "APPROACH", "LOOK", "RETREAT", "APPROACH", "LOOK", "LOOK", "RETREAT")

    h_s, h_r, h_sr, mi = mutual_information(sender_log, receiver_log)

    print(f"Total interactions logged : {len(sender_log)}")
    print(f"Sender Entropy H(S)       : {h_s:.3f} bits")
    print(f"Receiver Entropy H(R)     : {h_r:.3f} bits")
    print(f"Joint Entropy H(S, R)     : {h_sr:.3f} bits")
    print(f"Mutual Information I(S;R) : {mi:.3f} bits")
