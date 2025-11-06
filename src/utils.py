import re

YOUTUBE_ID_RE = re.compile(r"(UC[0-9A-Za-z_-]{22})")

def seconds_to_atempo_chain(factor: float) -> list[str]:
    remain = 1.0 / max(factor, 0.001)
    chain=[]
    while remain < 0.5: chain.append("0.5"); remain/=0.5
    while remain > 2.0: chain.append("2.0"); remain/=2.0
    chain.append(f"{remain:.6f}")
    return chain
