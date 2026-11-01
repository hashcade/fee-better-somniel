"""Execute compiled Emblem settlement with NSO-pinned native progression bodies."""

import struct
from unicorn import arm64_const as reg
from collector_fixture import CollectorFixture

NATIVE_BODIES = (
  (0x02B4F3E0, "ff0301d1fd7b01a9fd430091f65702a9f44f03a975be0190a8ce5639f30301aaf40300aa28010037c0bb01d0007041f9140b6597c0bb01d0007441f9110b659728008052a8ce1639ff0700f9130600b4d6bb01d0d67641f9951a40f9e00313aae1031faaeb99bb97c30240f9e10300aae2230091e00315aa5eec459440040037e00313aae1031faae299bb97f60300aa801e40f9080040f9098557a920013fd6f50300aa800100b4810a42a9e00315aae30316aaebf6ff97881240f9019140b9a8a240393f00086b60000054e00315aaacf8ff97f50700f9941a40f9e00313aae1031faacb99bb97c8bb01d0e20740f9e10300aa087141f9e00314aa030140f9d4e44594e00740f902000014e0031faaf44f43a9f65742a9fd7b41a9ff030191c0035fd6"),
  (0x23405b0, "001c40f9e2031faa8a3b20141f2003d5"),
  (0x23305d0, "fd7bbfa9fd030091001c40f9e2031faa807b2094800000b4e1031faafd7bc1a8c0782014fd7bc1a8c0035fd61f2003d5"),
  (0x2334310, "fd7bbfa9fd030091001c40f9e2031faa306c2094800000b4e1031faafd7bc1a830672014fd7bc1a8c0035fd61f2003d5"),
  (0x2334340, "fd7bbea9f30b00f9fd030091f30300aa001440f9600000b4e1031faaf560db97601a40f9a00000b4f30b40f9e1031faafd7bc2a8ef60db17f30b40f9fd7bc2a8c0035fd6"),
  (0x2336260, "fd7bbfa9fd030091001c40f9e2031faa5c642094800000b4e1031faafd7bc1a8845c2014fd7bc1a8c0035fd61f2003d5"),
  (0x1a3dd90, "fd7bbea9f44f01a9fd030091010200b4f30300aae00301aae10313aae2031faa4c142494e1031faae2031faaf40300aa44263d94c0000037689a40f9091140b98a1240b94901092a091100b9f44f41a9fd7bc2a8c0035fd6"),
  (0x2b4e8f0, "ffc300d1fd7b01a9fd430091f44f02a9f30300aae3faff971f100071000100541f0c007161010054e00313aaf44f42a9fd7b41a9ffc3009176ffff17e0031f2af44f42a9fd7b41a9ffc30091c0035fd668a2403901050011aafcff9720ffffb4001840f9e1031faa6ac73094c0000036e0031f2af44f42a9fd7b41a9ffc30091c0035fd674564079bfc31f38a21300d161a24039e00313aae2fcff971f00146be0179f1af44f42a9fd7b41a9ffc30091c0035fd6"),
  (0x2b4dff0, "fd7bbea9f44f01a9fd030091080c40f9f30300aa080200b4000940f9e2031faa611240f9b78e3094f403002ae0031faa6097df97880200120000080b68a240391f00086b21010054f44f41a9fd7bc2a8c0035fd6e0031faa5697df9768a240391f00086b20ffff5408050011011d00121f00016b68a20039c1010054680e40f9a80200b4000940f9e2031faa611240f99c8e3094f403002ae0031faa6597df97082840b9890200120801090b0d000014d4feff9769564079082840b91f01096b0c010054e00313aaf44f41a9fd7bc2a80c000014e0031faa5697df97082840b968560079e00313aaf44f41a9fd7bc2a804000014"),
  (0x2b4dd10, "fd7bbda9f65701a9fd030091f44f02a95f000039080c40f9f30302aaf403012af50300aac80300b4000940f9e2031faaa11240f96b8f3094f603002ae0031faa1498df97c80200120000080b1f00146be10200542800805268020039a80e40f9880600b4000940f9e2031faaa11240f95c8f3094f303002ae0031faa2598df97082840b9690200120001090bf44f42a9f65741a9fd7bc3a8c0035fd6e0031faafc97df971f00146b60fdff5476be01d0c8a65639c8000037e0b901b000d040f9a410659728008052c8a61639b60a40f995060011c8624339bf02086b81010054e8b901b008d140f9000140f908cc44396800083608e040b968030034e00316aae1031faa77cbdf9780030036e103152a74ffff97a00000b4001840f9e1031faa34ca3094c0000036e103152a16000014e0031faaf797df971400001428008052e103152a6802003966ffff97082840b900050051f44f42a9f65741a9fd7bc3a8c0035fd6c3106597e00316aae1031faa5ccbdf97c0fc07372800805268020039e103142a57ffff97002840b9f44f42a9f65741a9fd7bc3a8c0035fd6"),
  (0x2b4d490, "fd7bbda9f65701a9fd030091f44f02a974be01d088ae5639f30300aa2801003700ba0190005043f9ea12659700ba0190005443f9e71265972800805288ae1639680e40f9680100b4000940f9e2031faa611240f983913094c000003680008052f44f42a9f65741a9fd7bc3a8c0035fd673a24039f302003415ba019016ba0190b55643f9d65243f9a00240f908cc44398800083608e040b94800003515136597c10240f9e003132a5abd5a97f40300aa001840f9e1031faa6ecc309440010036681e0012730600511f050071e1fdff54e0031f2af44f42a9f65741a9fd7bc3a8c0035fd6e00314aaf44f42a9f65741a9e1031faafd7bc3a85e9adf17"),
  (0x233eb20, "fd7bbda9f50b00f9fd030091f44f02a9f30300aa001040f9e00200b4741640f9b40200b435fa01d0b5ea40f9a8024039c800003520fa01d000e440f9414d859728008052a8020039940a40f9e00314aa880240f9098958a90110a05220013fd6880a40f91f0100ea601240f940000054008040f9f44f42a9f50b40f9fd7bc3a8c0035fd6"),
  (0x23353f0, "081440f9a80000b4082940f9e80000b4002140b9c0035fd6081040f9680000b4009540b9c0035fd6e0008052c0035fd6"),
  (0x2a62b80, "fd7bbda9f50b00f9fd030091f44f02a9d5c5019054c10190a87a7b3994be44f9f30300aa2801003740c1019000b844f92cbd689740c1019000bc44f929bd689728008052a87a3b3955c10190b5ba44f9800240f908cc44396800083608e040b988030034a00240f9d62b5e97600400b4800240f908cc44396800083608e040b928030034a00240f9ce2b5e97086440f9480300b4800240f908cc44398800083608e040b94800003556bd6897a00240f9c42b5e97006440f9e10313aae2031faaf44f42a9f50b40f9fd7bc3a8fd2ff9174cbd6897a00240f9ba2b5e97a0fcffb50600001447bd6897a00240f9b52b5e97086440f908fdffb5f44f42a9f50b40f9fd7bc3a8c0035fd6"),
)


class EmblemFixture(CollectorFixture):
  def __init__(self, *args):
    super().__init__(*args)
    self.heap = self.game + 0xD800000
    for offset, name in (
      (0x02393F60, "UNIT_LIST"),
      (0x03CCA5D0, "BOND_DICTIONARY_GET"),
      (0x03CC8830, "BOND_DICTIONARY_SET"),
      (0x02B4D040, "BOND_INITIALIZE"),
      (0x03D30010, "BOND_POOL_GET"),
      (0x02B4DBF0, "LEVEL_DATA"),
      (0x001FCAA0, "GLOBAL_LEVEL_DATA"),
      (0x02333DA0, "GLOBAL_MAX"),
      (0x02333E20, "LAST_LEVEL_DATA"),
      (0x02333F00, "TALK_RANK"),
      (0x02340BF0, "CAP_UNLOCKED"),
      (0x03780700, "STRING_EMPTY"),
      (0x03771AF0, "STRING_EQUALS"),
      (0x02B4E0F0, "GAIN_ABILITY"),
      (0x01A0C730, "UPDATE_UNIT"),
      (0x02342EE0, "GOD_APTITUDE"),
      (0x029876D0, "FLAG_EMPTY"),
      (0x001EDB40, "ACHIEVE_INFO"),
      (0x028AEC40, "ACHIEVE_CLEAR_KEY"),
      (0x03D30000, "LINK_MASK"),
    ):
      self.functions[self.game + offset] = name
      self.write(self.game + offset, bytes.fromhex("c0035fd6"))
    for offset in (0x02097320, 0x01BA8260, 0x02396290, 0x02393B40, 0x023970A0):
      self.functions[self.game + offset] = "FORBIDDEN_DIALOG"

  def handle(self, pc, import_name):
    if not self.active:
      return False
    name = self.functions.get(pc, import_name)
    args = [self.cpu.reg_read(getattr(reg, f"UC_ARM64_REG_X{i}")) for i in range(4)]
    a, b = args[:2]
    result = None
    if self.idle:
      assert name not in ("GOD_POOL", "UNIT_LIST", "EMBLEM_BOND", "EMBLEM_CAN_TALK",
        "EMBLEM_LEVEL_UP", "malloc"), "idle frames must not rescan or allocate"
    if name == "GOD_POOL":
      assert a == self.pool_method
      self.scans += 1
      result = self.pool
    elif name == "UNIT_LIST": result = self.units
    elif name in ("UNIT_PID", "UNIT_NAME"): result = self.pids[a]
    elif name == "GET_DIRTY": result = 0
    elif name == "RELATION": result = 0  # No ordinary supports in this fixture.
    elif name == "BOND_DICTIONARY_GET":
      bond = self.bonds.get((a, self.read_string(b)), 0)
      self.cpu.mem_write(args[2], struct.pack("<Q", bond))
      result = int((a, self.read_string(b)) in self.bonds)
    elif name == "BOND_DICTIONARY_SET": self.bonds[(a, self.read_string(b))] = args[2]
    elif name == "BOND_POOL_GET": result = self.alloc()
    elif name == "BOND_INITIALIZE":
      self.qword(a + 0x10, b)
      self.qword(a + 0x18, args[2])
      self.qword(a + 0x20, args[3])
      self.write(a + 0x28, bytes([1]))
      self.write(a + 0x2A, bytes(2))
      self.initialized.append(a)
    elif name == "EMBLEM_LEVEL_UP" and (a, b) == self.failed_pair:
      pass  # Simulate a native step that did not advance; no secondary awards.
    elif name in ("LEVEL_DATA", "GLOBAL_LEVEL_DATA"): result = self.levels.get(b if name == "LEVEL_DATA" else a, 0)
    elif name == "GLOBAL_MAX": result = 20
    elif name == "LAST_LEVEL_DATA": result = self.levels[20]
    elif name == "TALK_RANK": result = self.ranks[a]
    elif name == "CAP_UNLOCKED": result = int(a in self.unlocked)
    elif name == "STRING_EMPTY": result = int(not a or not self.read_string(a))
    elif name == "STRING_EQUALS": result = int(self.read_string(a) == self.read_string(b))
    elif name == "GAIN_ABILITY":
      self.abilities.append((a, self.level(a)))
    elif name == "UPDATE_UNIT": self.updated.append(a)
    elif name == "GOD_APTITUDE":
      assert (a, b) in self.completed_pairs()
      result = self.aptitude
    elif name == "FLAG_EMPTY": result = int(not a or self.number(a + 0x10) == 0)
    elif name == "ACHIEVE_INFO": result = self.achieve
    elif name == "ACHIEVE_CLEAR_KEY":
      assert a == self.clear_keys
      self.cleared.append(self.read_string(b))
    elif name == "LINK_MASK": result = 0x800000
    elif name == "HUB_IS_MAIN": result = int(self.is_main)
    elif name in ("HUB_INIT", "HUB_TICK"): pass
    elif name == "FORBIDDEN_DIALOG":
      raise AssertionError("automatic Emblem settlement must not open conversation or reward UI")
    elif pc - self.game in self.native_offsets:
      return False
    else:
      return super().handle(pc, import_name)
    if result is not None:
      self.cpu.reg_write(reg.UC_ARM64_REG_X0, result)
    self.cpu.reg_write(reg.UC_ARM64_REG_PC, self.cpu.reg_read(reg.UC_ARM64_REG_X30))
    return True

  def level(self, bond):
    return self.cpu.mem_read(bond + 0x28, 1)[0]

  def exp(self, bond):
    return struct.unpack("<H", self.cpu.mem_read(bond + 0x2A, 2))[0]

  def completed_pairs(self):
    completed = {bond for bond, _ in self.abilities}
    return {(god, unit) for god, unit, bond in self.definitions if bond in completed}

  def exercise(self, hooks, menu_hook, stop, stack, enabled=True):
    self.active, self.idle = True, False
    self.reset(4)
    original_pool_method = self.pointer(self.game + 0x0628DD48)
    self.metadata(0x062840F0)
    self.qword(self.user + 0x50, self.alloc())
    self.is_main, self.scans = True, 0
    self.failed_pair = None
    self.initialized = []
    self.native_offsets = {offset for offset, _ in NATIVE_BODIES}
    self.abilities, self.updated, self.cleared = [], [], []
    for offset, body in NATIVE_BODIES:
      self.write(self.game + offset, bytes.fromhex(body))
    self.write(self.game + 0x0631B5A9, bytes(9))
    self.write(self.game + 0x0631AEDE, b"\0")
    for offset in (0x0628D6A0, 0x0628D6A8, 0x0628A1A0, 0x0628A970, 0x0628A978,
      0x062C92E0, 0x062C92E8):
      self.metadata(offset)
    self.achieve, self.clear_keys = self.alloc(), self.alloc()
    self.qword(self.achieve + 0xC8, self.clear_keys)
    self.aptitude = self.alloc()
    self.integer(self.aptitude + 0x10, 4)
    self.pids = {self.alloc(): self.string(f"PID_fixture_{i}") for i in range(8)}
    units = list(self.pids)
    self.units = self.list(units + [units[0], 0])
    for unit in units:
      self.qword(unit + 0x130, self.alloc())
      self.integer(self.pointer(unit + 0x130) + 0x10, 1)
    self.levels, self.ranks = {}, {}
    for level in range(22):
      data = self.alloc()
      self.integer(data + 0x28, level * 100)
      if level in (5, 10, 20):
        self.qword(data + 0x30, self.string(f"BondTalk_{level}"))
        self.ranks[data] = {5: 1, 10: 2, 20: 3}[level]
      self.levels[level] = data
    self.pool_method = self.metadata(0x0628DD48)
    gods = []
    for i in range(7):
      god, data, holder = self.alloc(), self.alloc(), self.alloc()
      self.qword(god + 0x20, data)
      self.qword(god + 0x38, holder)
      self.qword(holder + 0x20, data)
      self.qword(holder + 0x30, self.alloc())
      bond_pool, pool_class = self.alloc(), self.alloc()
      self.qword(bond_pool, pool_class)
      self.qword(pool_class + 0x178, self.game + 0x03D30010)
      self.qword(holder + 0x38, bond_pool)
      self.integer(data + 0x90, 1)
      self.qword(data + 0x20, self.string(f"GID_fixture_{i}"))
      self.integer(data + 0x94, 3 if i == 2 else 1 if i == 5 else 7 if i == 6 else 0)
      self.write(data + 0xD8, bytes([11]))
      gods.append(god)
    self.write(gods[3] + 0x4B, b"\1")
    self.write(gods[4] + 0x4A, b"\1")
    # The equipped linked Emblem uses the native linked GID, not the base GID.
    parent = units[0]
    flags, klass, force, linked = (self.alloc() for _ in range(4))
    self.qword(parent + 0x10, flags)
    self.qword(flags, klass)
    self.qword(flags + 0x10, 0x800000)
    self.qword(klass + 0x188, self.game + 0x03D30000)
    self.qword(parent + 0x50, force)
    self.integer(force + 0x20, 0)
    self.qword(gods[1] + 0x28, parent)
    self.qword(gods[1] + 0x30, units[1])
    self.qword(self.pointer(gods[1] + 0x20) + 0x100, linked)
    self.qword(linked + 0x20, self.string("GID_linked"))
    self.metadata(0x062841C8)
    self.metadata(0x062841D0)
    self.bonds, self.definitions, self.unlocked = {}, [], set()
    specs = [(0, 0, 4, 499), (0, 1, 9, 999), (0, 2, 19, 1999),
      (0, 3, 4, 498), (0, 4, 5, 500), (0, 5, 20, 2000), (0, 6, 21, 2001),
      (1, 0, 9, 999), (2, 1, 4, 499), (2, 2, 10, 1000),
      (3, 0, 4, 499), (4, 0, 4, 499), (5, 0, 4, 499), (6, 0, 4, 499)]
    for god_index, unit_index, level, exp in specs:
      god, unit, bond = gods[god_index], units[unit_index], self.alloc()
      self.qword(bond + 0x10, self.pointer(god + 0x20))
      self.qword(bond + 0x20, self.pids[unit])
      self.write(bond + 0x28, bytes([level]))
      self.write(bond + 0x2A, struct.pack("<H", exp))
      holder = self.pointer(god + 0x38)
      self.bonds[(self.pointer(holder + 0x30), self.read_string(self.pids[unit]))] = bond
      self.definitions.append((god, unit, bond))
    special = self.definitions[6][2]
    partner = self.alloc()
    self.qword(partner + 0x10, self.pids[units[6]])
    self.qword(special + 0x18, partner)
    # A native cached null lookup must be left untouched.
    self.bonds[(self.pointer(self.pointer(gods[0] + 0x38) + 0x30),
      self.read_string(self.pids[units[7]]))] = 0
    self.pool = self.alloc()
    self.qword(self.pool + 0x28, self.list(gods + [gods[0], 0]))
    assert self.pointer(self.pool + 0x10) == self.number(self.pool + 0x18) == 0

    def call(address, *args):
      for index in range(8):
        self.cpu.reg_write(getattr(reg, f"UC_ARM64_REG_X{index}"), args[index] if index < len(args) else 0)
      self.cpu.reg_write(reg.UC_ARM64_REG_SP, stack)
      self.cpu.reg_write(reg.UC_ARM64_REG_X30, stop)
      try:
        self.cpu.emu_start(address, stop + 4, count=1_000_000)
      except Exception as error:
        raise AssertionError(f"Emblem boundary PC {self.cpu.reg_read(reg.UC_ARM64_REG_PC):#x}; entry {address:#x}") from error
      assert self.cpu.reg_read(reg.UC_ARM64_REG_PC) == stop
      return self.cpu.reg_read(reg.UC_ARM64_REG_X0)

    def snapshot():
      return [bytes(self.cpu.mem_read(bond, 0x48)) for _, _, bond in self.definitions]

    # Native chapter-cap calculation is exercised, not replaced with a fixed threshold.
    cap_bond = self.definitions[9][2]
    blocked = self.alloc()
    assert call(self.game + 0x02B4DD10, cap_bond, 10, blocked) == 1000
    self.unlocked.add(self.pointer(cap_bond + 0x10))
    assert call(self.game + 0x02B4DD10, cap_bond, 10, blocked) == 1100
    self.unlocked.clear()
    before = snapshot()
    call(hooks["HUB_INIT"], self.hub)
    self.is_main = False
    call(hooks["HUB_TICK"], self.hub)
    self.is_main = True
    self.qword(self.hub + 0x38, self.alloc())
    call(hooks["HUB_TICK"], self.hub)
    assert snapshot() == before and self.scans == 0
    self.qword(self.hub + 0x38, 0)
    call(hooks["HUB_TICK"], self.hub)
    expected = {0, 1, 2, 7, 8} if enabled else set()
    assert {i for i, (_, _, bond) in enumerate(self.definitions) if self.level(bond) != before[i][0x28]} == expected
    for i, (_, _, bond) in enumerate(self.definitions):
      if i in expected:
        assert self.level(bond) == before[i][0x28] + 1
        assert self.exp(bond) == self.level(bond) * 100
      else:
        assert bytes(self.cpu.mem_read(bond, 0x48)) == before[i]
    assert len(self.abilities) == len(expected)
    assert all(self.level(bond) == 1 and self.exp(bond) == 0 for bond in self.initialized)
    assert len({bond for bond, _ in self.abilities}) == len(expected)
    assert self.updated == ([units[0], units[1]] if enabled else [])
    assert self.cleared == (["PID_fixture_0", "GID_fixture_0",
      "PID_fixture_1", "GID_fixture_0", "PID_fixture_2", "GID_fixture_0",
      "PID_fixture_0", "GID_linked", "PID_fixture_1", "GID_fixture_2"] if enabled else [])
    assert [self.number(self.pointer(unit + 0x130) + 0x10) for unit in units] == ([5, 5, 5, 1, 1, 1, 1, 1] if enabled else [1] * 8)
    assert not self.pointer(self.hub + 0x38)
    after, scans = snapshot(), self.scans
    self.idle = True
    for _ in range(16):
      call(hooks["HUB_TICK"], self.hub)
    self.idle = False
    assert snapshot() == after and self.scans == scans

    # A newly ready talk completes on menu opening without changing its selection.
    waiting = self.definitions[3][2]
    self.write(waiting + 0x2A, struct.pack("<H", 499))
    self.integer(self.menu + 0xA0, 2)
    call(menu_hook, self.parent)
    assert self.level(waiting) == (5 if enabled else 4)
    assert self.number(self.menu + 0xA0) == 2 and not self.pointer(self.menu + 0x38)
    settled = snapshot()
    rewards = len(self.abilities)
    call(menu_hook, self.parent)
    assert snapshot() == settled and len(self.abilities) == rewards

    # A no-op native progression must not acquire aptitudes or completion records.
    if enabled:
      self.write(waiting + 0x28, bytes([4]))
      self.write(waiting + 0x2A, struct.pack("<H", 499))
      self.failed_pair = (gods[0], units[3])
      records = len(self.cleared)
      call(menu_hook, self.parent)
      assert self.level(waiting) == 4 and len(self.abilities) == rewards
      assert len(self.cleared) == records
      self.failed_pair = None
      call(menu_hook, self.parent)
      assert self.level(waiting) == 5 and len(self.abilities) == rewards + 1

    # No automatic progression, UI or scans in post-battle/other contexts.
    self.write(waiting + 0x28, bytes([4]))
    self.write(waiting + 0x2A, struct.pack("<H", 499))
    for sequence in (2, 3, 5, 6):
      self.integer(self.user + 0x28, sequence)
      call(hooks["HUB_INIT"], self.hub)
      self.scans = 0
      call(hooks["HUB_TICK"], self.hub)
      call(menu_hook, self.parent)
      assert self.scans == 0 and self.level(waiting) == 4
      assert not self.pointer(self.menu + 0x38)
    self.active = False
    self.qword(self.game + 0x0628DD48, original_pool_method)

