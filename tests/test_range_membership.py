from range_expand import hand_in_tokens

def test_suited_interval_membership():
    assert hand_in_tokens("98s", ["98S-96S"]) is True
    assert hand_in_tokens("97s", ["98S-96S"]) is True
    assert hand_in_tokens("96s", ["98S-96S"]) is True
    assert hand_in_tokens("95s", ["98S-96S"]) is False

def test_pairs_interval_membership():
    assert hand_in_tokens("TT", ["AA-99"]) is True
    assert hand_in_tokens("88", ["AA-99"]) is False

def test_offsuit_interval_membership():
    assert hand_in_tokens("A5o", ["A9O-A2O"]) is True
    assert hand_in_tokens("ATo", ["A9O-A2O"]) is False
