//! Settle one native Sommie petting reward without creating an interaction scene.

pub const PET_FOUND: usize = 0x02AEE390;
pub const PET_DONE: usize = 0x02AEF8F0;
pub const PET_COMPLETE: usize = 0x02AEF6F0;
pub const PET_ADD_POINT: usize = 0x02AEED20;
pub const PET_PARAM: usize = 0x0203BB40;
pub const PET_SET_BOND: usize = 0x0250ECC0;

pub const TEXT_SIGNATURES: &[(usize, [u32; 4])] = &[
  (0x02AEE390, [0xD10103FF, 0xA9017BFD, 0x910043FD, 0xF90013F5]),
  (0x02AEF8F0, [0xD10103FF, 0xA9017BFD, 0x910043FD, 0xF90013F5]),
  (0x02AEF6F0, [0xD10103FF, 0xA9017BFD, 0x910043FD, 0xF90013F5]),
  (0x02AEED20, [0xA9BE7BFD, 0xA9014FF4, 0x910003FD, 0x2A0003F3]),
  (0x0203BB40, [0xA9BD7BFD, 0xF9000BF5, 0x910003FD, 0xA9024FF4]),
  (0x0250ECC0, [0xA9BD7BFD, 0xF9000BF5, 0x910003FD, 0xA9024FF4]),
  // Original petting: IsDoneStrok -> MascotParamData.GetValue -> AddPoint.
  (0x01E54CD0, [0x94326B08, 0x37000100, 0xF0022228, 0xF9411D08]),
  // GetBond resolves the reward ItemData before tail-calling DoneStrok.
  (0x0203A714, [0x90021348, 0xF9459508, 0xF9400100, 0xB0021268]),
  (0x0203A750, [0xA9414FF4, 0xAA1F03E0, 0xA8C27BFD, 0x142AD3E5]),
  // PieceOfBondGainSequence reads the item's Power, then uses the native setter.
  (0x0280B780, [0xB40000E1, 0xB9404828, 0x7100451F, 0x54000081]),
  (0x0280B8A0, [0xF94002E0, 0x9766E0B3, 0xB9406C08, 0x0B140101]),
];

#[cfg(target_os = "switch")]
pub(crate) unsafe fn settle() {
  use crate::native::{base, field, metadata, user_data, Method, Object};
  use core::ptr;
  const NONE: Method = ptr::null();
  macro_rules! native {
    ($offset:expr, $signature:ty) => {
      core::mem::transmute::<usize, $signature>(base() + $offset)
    };
  }
  unsafe {
    if !native!(PET_FOUND, unsafe extern "C" fn(Method) -> bool)(NONE)
      || native!(PET_DONE, unsafe extern "C" fn(Method) -> bool)(NONE)
    {
      return;
    }
    // Use the same reward ID and point parameter as GetBond/Strok; neither
    // ItemGainSequence nor its currency popup may be bound by this automation.
    let reward_key = metadata(0x062A2B28);
    let item_method = metadata(0x06287888);
    let reward = native!(
      crate::collector::profile::ITEM_GET,
      unsafe extern "C" fn(Object, Method) -> Object
    )(reward_key, item_method);
    let user = user_data();
    if reward.is_null() || user.is_null() {
      return;
    }
    let point_key = metadata(0x0629B238);
    let points = native!(PET_PARAM, unsafe extern "C" fn(Object, Method) -> i32)(point_key, NONE);
    native!(PET_ADD_POINT, unsafe extern "C" fn(i32, Method))(points, NONE);
    let amount: i32 = field(reward, 0x70);
    if amount > 0 {
      // The original setter retains the wallet cap and cumulative acquisition
      // counter. Presentation-only clearing/text/popup calls are not needed.
      let current: i32 = field(user, 0x6C);
      native!(PET_SET_BOND, unsafe extern "C" fn(Object, i32, Method))(
        user,
        current + amount,
        NONE,
      );
    }
    native!(PET_COMPLETE, unsafe extern "C" fn(Method))(NONE);
  }
}
