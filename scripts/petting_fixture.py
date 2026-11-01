"""Compiled automatic petting, with the native affection/wallet cap bodies."""

from unicorn import arm64_const as reg
from convenience_fixture import ConvenienceFixture

NATIVE_BODIES = (
  (0x02AEED20, "fd7bbea9f44f01a9fd030091f303002a2cffff97f403002a4efdff970100130be003142ae2031faaa6c11f94f44f41a9fd7bc2a857feff171f2003d51f2003d5"),
  (0x0250ECC0, "fd7bbda9f50b00f9fd030091f44f02a9f4cf92521413a072f30300aae003012ae103142ae2031faabe413794686e40b90800084bf503002a1f050071eb000054697240b92001080be103142ae2031faab4413794607200b9756e00b9f44f42a9f50b40f9fd7bc3a8c0035fd61f2003d5"),
)


class PettingFixture(ConvenienceFixture):
  def __init__(self, *args):
    super().__init__(*args)
    self.heap = self.game + 0xDC00000
    for offset, name in (
      (0x02AEE9E0, "PET_LIMIT"), (0x02AEE270, "PET_POINTS"),
      (0x02AEE6B0, "PET_WRITE_POINTS"), (0x032DF3E0, "PET_MINIMUM"),
    ):
      self.functions[self.game + offset] = name
      self.write(self.game + offset, bytes.fromhex("c0035fd6"))

  def handle(self, pc, import_name):
    name = self.functions.get(pc, import_name)
    # Other existing fixtures model an undiscovered Sommie. They must not
    # acquire new reward/API requirements merely because the option defaults on.
    if not self.active:
      if name != "PET_FOUND": return False
      self.cpu.reg_write(reg.UC_ARM64_REG_X0, 0)
      self.cpu.reg_write(reg.UC_ARM64_REG_PC, self.cpu.reg_read(reg.UC_ARM64_REG_X30))
      return True
    a, b = (self.cpu.reg_read(getattr(reg, f"UC_ARM64_REG_X{i}")) for i in range(2))
    result = None
    if name == "PET_FOUND": result = int(self.found)
    elif name == "PET_DONE": result = int(self.done)
    elif name == "PET_COMPLETE":
      assert self.operations[-1] == "reward"
      self.done = True
      self.operations.append("complete")
    elif name == "PET_PARAM":
      assert a == self.point_key
      result = 5
    elif name == "ITEM_GET":
      assert a == self.reward_key and b == self.item_method
      result = self.reward if self.reward_available else 0
    elif name in ("PET_ADD_POINT", "PET_SET_BOND"):
      self.operations.append("points" if name == "PET_ADD_POINT" else "reward")
      return False  # Execute the independently NSO-verified bodies below.
    elif name == "PET_LIMIT": result = self.limit
    elif name == "PET_POINTS": result = self.points
    elif name == "PET_WRITE_POINTS": self.points = a
    elif name == "PET_MINIMUM": result = min(a, b)
    elif name == "HUB_IS_MAIN": result = 1
    elif name in ("HUB_INIT", "HUB_TICK"): pass
    else: return super().handle(pc, import_name)
    if result is not None: self.cpu.reg_write(reg.UC_ARM64_REG_X0, result)
    self.cpu.reg_write(reg.UC_ARM64_REG_PC, self.cpu.reg_read(reg.UC_ARM64_REG_X30))
    return True

  def exercise_petting(self, callbacks, hooks, stop, stack):
    self.active = True
    self.units = self.list()
    self.exercise(callbacks, stop, stack)
    self.active = True
    # Keep the automatic actions independent: only petting is enabled here.
    def change(kind, value):
      self.next_count = value
      item = self.invoke(self.factories[kind])
      callback = self.pointer(self.pointer(item) + 0x138 + 26 * 16)
      return self.invoke(callback, item)
    assert change(3, 0) == change(4, 0) == 4096
    self.reset(4)
    self.arena_spent, self.fishing_remaining = 0, 3
    self.found, self.done, self.reward_available = False, False, True
    self.points, self.limit, self.operations = 98, 100, []
    self.point_key = self.metadata(0x0629B238, self.string("なでる"))
    self.reward_key = self.metadata(0x062A2B28, self.string("fixture_native_sommie_reward"))
    self.item_method = self.metadata(0x06287888)
    self.reward = self.alloc()
    self.integer(self.reward + 0x48, 17)
    self.integer(self.reward + 0x70, 100)
    self.integer(self.user + 0x6C, 50)
    self.integer(self.user + 0x70, 250)
    for offset, body in NATIVE_BODIES:
      self.write(self.game + offset, bytes.fromhex(body))

    def arrive():
      self.invoke(hooks["HUB_INIT"], self.hub)
      self.invoke(hooks["HUB_TICK"], self.hub)
      assert not self.pointer(self.hub + 0x38), "petting must not bind a menu or interaction"

    arrive()
    assert not self.operations and self.points == 98
    self.found = True
    self.reward_available = False
    arrive()
    assert not self.operations and not self.done and self.points == 98
    self.reward_available = True
    arrive()
    assert self.operations == ["points", "reward", "complete"]
    assert self.points == 100 and self.number(self.user + 0x6C) == 150
    assert self.number(self.user + 0x70) == 350
    for _ in range(8): self.invoke(hooks["HUB_TICK"], self.hub)
    arrive()
    assert self.operations == ["points", "reward", "complete"]

    # The original done flag also prevents a later manual path from rewarding again.
    assert self.done
    assert change(14, 0) == 4096
    assert b"auto_pet=0\n" in self.files[self.paths[0]]
    reopened = self.invoke(self.factories[14])
    assert self.read_string(self.pointer(reopened + 0x70)) == "关闭"
    self.done = False
    arrive()
    assert len(self.operations) == 3 and not self.done
    assert change(14, 1) == 4096
    assert b"auto_pet=0\n" not in self.files[self.paths[0]]
    self.integer(self.user + 0x28, 5)
    arrive()
    assert len(self.operations) == 3 and not self.done
    self.integer(self.user + 0x28, 4)
    self.integer(self.user + 0x6C, 9_999_950)
    self.integer(self.user + 0x70, 1000)
    arrive()
    assert self.number(self.user + 0x6C) == 9_999_999
    assert self.number(self.user + 0x70) == 1049
    assert self.points == 100 and self.done and len(self.operations) == 6
    self.active = False
