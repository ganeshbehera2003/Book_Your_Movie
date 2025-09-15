from typing import List, Tuple

# Split row with N seats into 3 blocks as evenly as possible -> returns boundaries
# Example: N=8 -> blocks [3,3,2]; aisles between blocks create 6 aisle seats across the row (two ends + two at each internal boundary)

def split_into_three_blocks(n: int) -> Tuple[int, int, int]:
    base = n // 3
    rem = n % 3
    a = base + (1 if rem > 0 else 0)
    b = base + (1 if rem > 1 else 0)
    c = base
    return a, b, c

# Compute aisle seat numbers for a row of length n
# Aisles exist at boundaries between blocks; aisle seats are the seats immediately adjacent to each aisle on both sides,
# plus the very first and very last seats of the row -> total 6 aisle seats when n>=6.

def aisle_positions(n: int) -> List[int]:
    a,b,c = split_into_three_blocks(n)
    p1 = a  # last seat of block1
    p2 = a+1  # first of block2
    p3 = a+b  # last of block2
    p4 = a+b+1  # first of block3
    return [1, p1, p2, p3, p4, n]

# Find a contiguous block of size k within available seat numbers (sorted list)

def find_contiguous_block(avail: List[int], k: int) -> List[int]:
    if k <= 0: return []
    s = set(avail)
    # Sliding window over sorted availability to find k consecutive integers
    for i in range(len(avail)):
        start = avail[i]
        need = [start + d for d in range(k)]
        if all(x in s for x in need):
            return need
    return []
