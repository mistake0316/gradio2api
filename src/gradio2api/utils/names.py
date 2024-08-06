from collections import Counter
prefix_counter = Counter()
def prefix_to_name(prefix:str):
  idx = prefix_counter[prefix]
  prefix_counter[prefix] += 1
  return f"{prefix}_{idx}"