# range_expand.py
RANKS = "23456789TJQKA"
RANK_INDEX = {r:i for i,r in enumerate(RANKS)}

def _up(s: str) -> str:
    return (s or "").strip().upper()

def normalize_hand(hand: str) -> str:
    h = _up(hand)
    if len(h) == 2 and h[0] in RANK_INDEX and h[1] in RANK_INDEX:
        # pair like TT
        return h
    if len(h) == 3 and h[0] in RANK_INDEX and h[1] in RANK_INDEX and h[2] in ("S","O"):
        return h
    return h

def _pair_interval(a: str, b: str):
    a=_up(a); b=_up(b)
    if len(a)!=2 or len(b)!=2 or a[0]!=a[1] or b[0]!=b[1]:
        return None
    ia = RANK_INDEX[a[0]]; ib = RANK_INDEX[b[0]]
    step = -1 if ia >= ib else 1
    out=[]
    for i in range(ia, ib+step, step):
        r = RANKS[i]
        out.append(r+r)
    return out

def _nonpair_interval(a: str, b: str):
    a=_up(a); b=_up(b)
    if len(a)!=3 or len(b)!=3: return None
    if a[2]!=b[2]: return None
    if a[0]!=b[0]: return None
    ia = RANK_INDEX.get(a[1]); ib = RANK_INDEX.get(b[1])
    if ia is None or ib is None: return None
    step = -1 if ia >= ib else 1
    out=[]
    for i in range(ia, ib+step, step):
        out.append(f"{a[0]}{RANKS[i]}{a[2]}")
    return out

def expand_token(token: str):
    t=_up(token)
    if not t: return []
    if "-" not in t: return [t]
    left,right = [x.strip() for x in t.split("-",1)]
    if len(left)==2 and len(right)==2 and left[0]==left[1] and right[0]==right[1]:
        got=_pair_interval(left,right)
        return got if got is not None else [t]
    if len(left)==3 and len(right)==3 and left[2] in ("S","O") and right[2] in ("S","O"):
        got=_nonpair_interval(left,right)
        return got if got is not None else [t]
    return [t]

def hand_in_tokens(hand: str, tokens) -> bool:
    h = normalize_hand(hand)
    if not tokens:
        return False
    for tok in tokens:
        for ex in expand_token(tok):
            if normalize_hand(ex) == h:
                return True
    return False
