//! Skip only the combat presentation of a shortcut-owned arena session.

pub const CREATE_COMBAT: usize = 0x01CA3000;
pub const DESCRIPTOR_COUNT: usize = 14;
// Keep both native fades, all three growth steps, and End. Setup, WaitBegin,
// StartFight, WaitFinish, Result and their matching rendering Exit are omitted.
pub const QUICK_ORDER: [usize; DESCRIPTOR_COUNT] =
  [2, 3, 7, 8, 9, 10, 11, 13, 13, 13, 13, 13, 13, 13];

pub const TEXT_SIGNATURES: &[(usize, [u32; 4])] = &[
  (0x01CA3000, [0xD101C3FF, 0xA9017BFD, 0x910043FD, 0xA9026FFC]),
  (0x01CA3144, [0xF9400260, 0x528001C1, 0x979FBBD5, 0xAA0003F5]),
];

#[cfg(target_os = "switch")]
pub(crate) mod native {
  use super::*;
  use crate::native::{field, reference, Method, Object};

  pub(crate) fn install() {
    skyline::install_hooks!(create_combat);
  }

  #[skyline::hook(offset = CREATE_COMBAT)]
  fn create_combat(
    parent: Object,
    calculator: Object,
    simulation: Object,
    emblem: bool,
    special: bool,
    exp: i32,
    method: Method,
  ) {
    call_original!(parent, calculator, simulation, emblem, special, exp, method);
    unsafe {
      if !crate::facilities::native::is_quick_arena(parent) {
        return;
      }
      let child: Object = field(parent, 0x38);
      if child.is_null() {
        return;
      }
      let descriptors: Object = field(child, 0x10);
      if descriptors.is_null() || field::<usize>(descriptors, 0x18) < DESCRIPTOR_COUNT {
        return;
      }
      let original: [Object; DESCRIPTOR_COUNT] =
        core::array::from_fn(|i| field(descriptors, 0x20 + i * 8));
      for (i, source) in QUICK_ORDER.into_iter().enumerate() {
        reference(descriptors, 0x20 + i * 8, original[source]);
      }
    }
  }
}
