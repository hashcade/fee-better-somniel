"""Execute native arena construction and compiled shortcut scoping, not Unity."""

import struct
from unicorn import arm64_const as reg
from facility_fixture import FacilityFixture
from arena_native_fixture import NATIVE_BODIES


class ArenaFixture(FacilityFixture):
  def array_values(self, array):
    return [self.pointer(array + 0x20 + i * 8) for i in range(self.number(array + 0x18))]

  def __init__(self, *args):
    super().__init__(*args)
    self.heap = self.game + 0xE000000
    self.arena_orders = []
    self.testing_arena = False

  def handle(self, pc, import_name):
    if not self.active: return False
    if not self.testing_arena:
      handled = super().handle(pc, import_name)
      if pc == self.game + 0x01CA5330:
        self.arena_orders.append(self.cpu.reg_read(reg.UC_ARM64_REG_X0))
      return handled
    name = self.functions.get(pc, import_name)
    args = [self.cpu.reg_read(getattr(reg, f"UC_ARM64_REG_X{i}")) for i in range(7)]
    a, b, c = args[:3]
    result = None
    if pc == self.game + 0x01CAA4A8:
      # This is the native StartTraining tail call. The trampoline itself still
      # executes the complete original CreateBind below.
      self.forwarded = tuple(args[:6])
      self.cpu.reg_write(reg.UC_ARM64_REG_PC, self.replacement)
      return True
    if name == "ARENA_CTOR":
      self.qword(a + 0x88, b)
      self.qword(a + 0x90, c)
      self.integer(a + 0x98, args[5])
      self.write(a + 0x9C, bytes(args[3:5]))
    elif name == "ARENA_ARRAY":
      result = self.alloc(0x20 + b * 8)
      self.qword(result, a)
      self.qword(result + 0x18, b)
    elif name == "ARENA_ENUMERATOR":
      result = self.alloc()
      self.qword(result + 0x20, self.pointer(a + 0x20))
    elif name in ("ARENA_FADE", "ARENA_WAIT", "ARENA_END"):
      result = self.alloc()
      self.integer(result + 0x10, {"ARENA_FADE": 10, "ARENA_WAIT": 15, "ARENA_END": 0}[name])
    elif name == "ARENA_BIND":
      self.qword(a + 0x30, b)
      self.qword(b + 0x38, a)
      self.qword(a + 0x10, c)
      self.original_descriptors = self.array_values(c)
    elif name == "ARENA_IS_INSTANCE": result = a
    elif name in ("INITIALIZE_METADATA", "ARENA_CLASS_INIT", "ARENA_OBJECT_CTOR", "WRITE_BARRIER"): pass
    elif name == "PARAMETER": result = self.reward_exp
    elif name == "ARENA_DEAD_SIDE": result = self.dead_side
    elif name == "ARENA_PHASE": result = self.phases[b]
    elif name == "ARENA_EXP":
      assert a == self.combat and b == self.calculator
      self.settlements.append("exp")
    elif name == "ARENA_POPUP_NEW": result = self.alloc()
    elif name == "ARENA_SUPPORT":
      assert (a, b, c) == (self.ally, self.opponent, self.reward_exp)
      self.settlements.append("support")
      result = 1
    elif name in ("ARENA_POPUP_SUPPORT", "ARENA_POPUP_WAIT", "ARENA_MESSAGE"): pass
    elif name == "ARENA_DELTA":
      self.cpu.reg_write(reg.UC_ARM64_REG_S0, struct.unpack("<I", struct.pack("<f", 3.0))[0])
    elif name == "ARENA_GROW3": self.settlements.append("grow3")
    elif name == "ARENA_PID": result = self.string("PID_Emblem_Marth")
    elif name == "ARENA_SPLIT":
      result = self.pointer(self.list([self.string("PID"), self.string("Emblem"), self.string("Marth")], capacity=3) + 0x10)
    elif name == "ARENA_TEXT_CONCAT": result = self.string("GID_Marth")
    elif name == "ARENA_TEXT_CONTAINS": result = 0
    elif name == "ARENA_GOD": result = self.god
    elif name == "ARENA_BOND": result = self.bond
    elif name == "ARENA_ADD_BOND_EXP":
      assert a == self.bond and b == self.reward_exp
      self.settlements.append("bond_exp")
      result = 0
    elif name == "ARENA_BOND_LEVEL": result = 1
    elif name == "ARENA_BOND_LEVEL_UP":
      assert a == self.bond
      self.write(self.bond + 0x28, b"\x01")
      self.settlements.append("bond_level_up")
    elif name == "ARENA_GROWTH_DATA": result = 0
    elif name == "ARENA_APTITUDE":
      assert (a, b) == (self.ally, self.god)
      self.settlements.append("aptitude")
    elif name == "ARENA_BOND_TALK":
      # These remain original result/conversation APIs, not auto-skipped input.
      self.settlements.append("bond_talk")
      result = 0
    elif name == "ARENA_GROWTH_UI": self.settlements.append("growth_ui")
    else: return super().handle(pc, import_name)
    if result is not None: self.cpu.reg_write(reg.UC_ARM64_REG_X0, result)
    self.cpu.reg_write(reg.UC_ARM64_REG_PC, self.cpu.reg_read(reg.UC_ARM64_REG_X30))
    return True

  def exercise_arena(self, hook, ring_hook, replacement, stop, stack, profile):
    # Initialize the actual private shortcut class through its compiled menu.
    self.exercise(hook, ring_hook, stop, stack, profile)
    quick_class = self.pointer(self.arena_orders[-1])
    assert quick_class and quick_class != self.sequence_class
    self.active = self.testing_arena = True
    self.replacement = replacement
    methods = {
      0x06291680: 0x01CA38C0, 0x062916B8: 0x01CA3940,
      0x062916B0: 0x01CA39A0, 0x062916C0: 0x01CA3A20,
      0x062916A8: 0x01CA3A80, 0x06291690: 0x01CA3B00,
      0x06291698: 0x01CA3B80, 0x062916A0: 0x01CA3C00,
      0x06291688: 0x01CA3DB0,
    }
    slots = [0x06291678, 0x06286CD0, 0x0628E7F0, 0x062863D0, 0x06286CE8,
      0x06286CD8, 0x062BE008, 0x062BD760, 0x062863D8, 0x0628D688,
      0x0628D690, 0x06286178, 0x06284368, 0x0628BF98, 0x0628D6A0,
      0x06287E40, 0x06287E48, 0x0628D6A8, 0x0628C148, 0x06287210,
      0x0628D6B0, 0x0628D6B8, 0x0628D650, 0x06289750,
      0x0628D6C0, 0x0628D6C8, 0x0628D6D0]
    slots += list(range(0x06291A28, 0x06291A58, 8))
    for slot in slots: self.metadata(slot)
    for slot, function in methods.items():
      method = self.metadata(slot)
      self.qword(method, self.game + function)
    for flag in (0x0631537C, 0x06315356, 0x06319F88, 0x0631A007, 0x06314DF1, 0x06314DF2):
      self.write(self.game + flag, b"\x01")
    for offset, name in (
      (0x01CA36E0, "ARENA_CTOR"), (0x004920A0, "ARENA_ARRAY"),
      (0x0281D610, "ARENA_ENUMERATOR"), (0x02D539A0, "ARENA_FADE"),
      (0x02D53A60, "ARENA_FADE"), (0x02D53E00, "ARENA_WAIT"),
      (0x0280AA50, "ARENA_END"), (0x0280A6B0, "ARENA_BIND"),
      (0x004921B0, "ARENA_IS_INSTANCE"), (0x00492180, "ARENA_CLASS_INIT"),
      (0x037D2B40, "ARENA_OBJECT_CTOR"), (0x02476300, "ARENA_DEAD_SIDE"),
      (0x0246F1A0, "ARENA_PHASE"), (0x01E77310, "ARENA_EXP"),
      (0x02010E30, "ARENA_POPUP_NEW"), (0x01C5A630, "ARENA_SUPPORT"),
      (0x02011380, "ARENA_POPUP_SUPPORT"), (0x01A01840, "ARENA_POPUP_WAIT"),
      (0x02272FD0, "ARENA_MESSAGE"), (0x0378E820, "ARENA_DELTA"),
      (0x01CA3C00, "ARENA_GROW3"), (0x01A35BF0, "ARENA_PID"),
      (0x037808E0, "ARENA_SPLIT"), (0x037713E0, "ARENA_TEXT_CONCAT"),
      (0x03771AF0, "ARENA_TEXT_CONTAINS"), (0x001EAB60, "ARENA_GOD"),
      (0x02334570, "ARENA_GOD"), (0x02B4F3E0, "ARENA_BOND"),
      (0x02B4D990, "ARENA_ADD_BOND_EXP"), (0x02B4D600, "ARENA_BOND_LEVEL"),
      (0x02B4DFF0, "ARENA_BOND_LEVEL_UP"),
      (0x001FCAA0, "ARENA_GROWTH_DATA"), (0x01A3DD90, "ARENA_APTITUDE"),
      (0x0298A5A0, "ARENA_BOND_TALK"), (0x021E1240, "ARENA_GROWTH_UI"),
    ):
      self.functions[self.game + offset] = name
      if offset != 0x0280A6B0:
        self.write(self.game + offset, bytes.fromhex("c0035fd6"))
    for offset, body in NATIVE_BODIES: self.write(self.game + offset, bytes.fromhex(body))

    def call(address, *args):
      for i in range(8): self.cpu.reg_write(getattr(reg, f"UC_ARM64_REG_X{i}"), args[i] if i < len(args) else 0)
      self.cpu.reg_write(reg.UC_ARM64_REG_SP, stack)
      self.cpu.reg_write(reg.UC_ARM64_REG_X30, stop)
      try:
        self.cpu.emu_start(address, stop + 4, count=300_000)
      except Exception as error:
        pc = self.cpu.reg_read(reg.UC_ARM64_REG_PC)
        raise AssertionError(f"arena boundary PC={pc:#x}, X0={self.cpu.reg_read(reg.UC_ARM64_REG_X0):#x}") from error
      assert self.cpu.reg_read(reg.UC_ARM64_REG_PC) == stop

    functions = [0x1CA38C0, 0x1CA3940, 0, 0, 0x1CA39A0, 0x1CA3A20,
      0x1CA3A80, 0x1CA3B00, 0x1CA3B80, 0x1CA3C00, 0, 0, 0x1CA3DB0, 0]
    kinds = [11, 11, 10, 15, 11, 11, 10, 11, 11, 10, 10, 15, 11, 0]
    order = [2, 3, 7, 8, 9, 10, 11, 13] + [13] * 6
    for room, emblem, special, exp, dead in (
      (False, False, False, 30, 1), (False, False, False, 10, 0),
      (False, True, False, 6000, 1), (False, True, False, 100, 0),
      (False, False, True, 30, 1), (False, True, True, 100, 0),
      (True, False, False, 30, 1), (True, True, False, 6000, 1),
    ):
      parent, self.calculator, simulation = (self.alloc() for _ in range(3))
      self.qword(parent, self.sequence_class if room else quick_class)
      self.integer(parent + 0x8C, int(emblem))
      self.integer(parent + 0xAC, exp)
      self.write(parent + 0x88, bytes([emblem, special]))
      self.qword(parent + 0xB0, self.calculator)
      self.qword(parent + 0xB8, simulation)
      self.reward_exp, self.dead_side, self.settlements = exp, dead, []
      call(self.game + 0x01CAA3A0, parent)
      assert self.forwarded == (parent, self.calculator, simulation, int(emblem), int(special), exp)
      self.combat = self.pointer(parent + 0x38)
      array = self.pointer(self.combat + 0x10)
      original = self.original_descriptors
      assert [self.number(d + 0x10) for d in original] == kinds
      for i, function in enumerate(functions):
        if function:
          delegate = self.pointer(original[i] + 0x18)
          assert self.pointer(delegate + 0x10) == self.game + function
          assert self.pointer(delegate + 0x20) == self.combat
      assert self.array_values(array) == (original if room else [original[i] for i in order])
      if room: continue
      self.ally, self.opponent, self.god, self.bond = (self.alloc() for _ in range(4))
      self.qword(self.god + 0x38, self.alloc())
      self.phases = [self.alloc(), self.alloc()]
      for phase, unit in zip(self.phases, (self.ally, self.opponent)): self.qword(phase + 0x20, unit)
      # Follow the edited array through End, including the exact cached native
      # growth iterators. External growth/UI APIs remain modeled boundaries.
      for descriptor in self.array_values(array):
        kind = self.number(descriptor + 0x10)
        if kind == 0: break
        delegate = self.pointer(descriptor + 0x18)
        if not delegate: continue  # Native fade/wait descriptors.
        function = self.pointer(delegate + 0x10) - self.game
        if function == 0x01CA3C00:
          call(self.game + function, self.combat)
          continue
        assert function in (0x01CA3B00, 0x01CA3B80), "a rendering step survived the shortcut edit"
        iterator = self.pointer(descriptor + 0x20)
        native_move = 0x01BABDB0 if function == 0x01CA3B00 else 0x01BABFD0
        call(self.game + native_move, iterator)
        while self.cpu.reg_read(reg.UC_ARM64_REG_X0): call(self.game + native_move, iterator)
      assert self.settlements.count("exp") == (0 if special else 1)
      assert self.settlements.count("support") == (0 if emblem else 1)
      assert self.settlements.count("bond_exp") == int(emblem)
      assert self.settlements.count("aptitude") == int(emblem)
      assert self.settlements.count("bond_level_up") == int(emblem)
      assert self.settlements.count("grow3") == 1
    self.active = self.testing_arena = False
