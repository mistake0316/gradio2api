used_pair = set()

class AutoName:
  def __init__(
    self,
    idx=0,
    prefix="Model",
    suffix=""
  ):
    key = (prefix, suffix)
    assert key not in used_pair
    used_pair.add(key)

    self.idx = idx
    self.prefix = prefix
    self.suffix = suffix

  def get_name(self):
    ret = f"{self.prefix and self.prefix+'_'}{self.idx:05d}{self.suffix and '_'+self.suffix}"
    self.idx += 1
    return ret
