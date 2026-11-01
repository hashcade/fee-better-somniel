//! Native Emblem bond conversation settlement without dialogue or reward UI.

use crate::{
  cleaning::{
    automatic::{GOD_DATA, GOD_POOL, GOD_POOL_METHOD},
    GET_STATE as GOD_FORCE_TYPE,
  },
  cooking::UNIT_PID,
  native::{base, field, list_count, metadata, object_at, Method, Object},
};
use core::ptr;
use std::collections::BTreeSet;

pub const EMBLEM_BOND: usize = 0x023405B0;
pub const EMBLEM_CAN_TALK: usize = 0x023305D0;
pub const EMBLEM_LEVEL_UP: usize = 0x02334310;
pub const EMBLEM_UPDATE_STATE: usize = 0x02334340;
pub const EMBLEM_RELIANCE_LEVEL: usize = 0x02336260;
pub const INHERIT_APTITUDE: usize = 0x01A3DD90;
pub const CLEAR_RELIANCE: usize = 0x02A62B80;

#[allow(dead_code)]
pub const TEXT_SIGNATURES: &[(usize, [u32; 4])] = &[
  (0x023405B0, [0xF9401C00, 0xAA1F03E2, 0x14203B8A, 0xD503201F]),
  (0x023305D0, [0xA9BF7BFD, 0x910003FD, 0xF9401C00, 0xAA1F03E2]),
  (0x02334310, [0xA9BF7BFD, 0x910003FD, 0xF9401C00, 0xAA1F03E2]),
  (0x02334340, [0xA9BE7BFD, 0xF9000BF3, 0x910003FD, 0xAA0003F3]),
  (0x02336260, [0xA9BF7BFD, 0x910003FD, 0xF9401C00, 0xAA1F03E2]),
  (0x01A3DD90, [0xA9BE7BFD, 0xA9014FF4, 0x910003FD, 0xB4000201]),
  (0x02A62B80, [0xA9BD7BFD, 0xF9000BF5, 0x910003FD, 0xA9024FF4]),
  (0x02099730, [0xF9403E60, 0xAA1F03E2, 0xF9403661, 0x940A72C9]),
];

const NONE: Method = ptr::null();

macro_rules! native {
  ($address:expr, $signature:ty) => {
    core::mem::transmute::<usize, $signature>(base() + $address)
  };
}

pub(super) unsafe fn settle(units: Object) {
  unsafe {
    let Some(unit_count) = list_count(units) else { return };
    let units: BTreeSet<usize> = (0..unit_count)
      .filter_map(|index| object_at(units, index))
      .filter(|unit| !unit.is_null())
      .map(|unit| unit as usize)
      .collect();
    let method = metadata(GOD_POOL_METHOD);
    if method.is_null() {
      return;
    }
    let pool = native!(GOD_POOL, unsafe extern "C" fn(Method) -> Object)(method);
    if pool.is_null() {
      return;
    }
    // GodPool.GetEnumerator uses its used list, not a List header on the pool.
    let gods: Object = field(pool, 0x28);
    let Some(count) = list_count(gods) else { return };
    let mut seen = BTreeSet::new();
    for index in 0..count {
      let Some(god) = object_at(gods, index).filter(|god| !god.is_null()) else { continue };
      if !seen.insert(god as usize)
        || field::<u8>(god, 0x4A) != 0
        || field::<u8>(god, 0x4B) != 0
        || !matches!(
          native!(GOD_FORCE_TYPE, unsafe extern "C" fn(Object, Method) -> i32)(god, NONE),
          0 | 3
        )
      {
        continue;
      }
      for &unit in &units {
        settle_pair(god, unit as Object);
      }
    }
  }
}

unsafe fn settle_pair(god: Object, unit: Object) {
  unsafe {
    let bond =
      native!(EMBLEM_BOND, unsafe extern "C" fn(Object, Object, Method) -> Object)(god, unit, NONE);
    if bond.is_null() {
      return;
    }
    // Settle ordinary C/B/A bond talks, not special S-rank relationship events.
    let rank = native!(EMBLEM_RELIANCE_LEVEL, unsafe extern "C" fn(Object, Object, Method) -> i32)(
      god, unit, NONE,
    );
    if !(0..=2).contains(&rank)
      || !native!(EMBLEM_CAN_TALK, unsafe extern "C" fn(Object, Object, Method) -> bool)(
        god, unit, NONE,
      )
    {
      return;
    }
    let before: u8 = field(bond, 0x28);
    native!(EMBLEM_LEVEL_UP, unsafe extern "C" fn(Object, Object, Method))(god, unit, NONE);
    if u16::from(field::<u8>(bond, 0x28)) != u16::from(before) + 1 {
      return;
    }
    // ReferenceMenuItem's native settlement updates equipped state, aptitudes
    // and both achievement keys. Only its UI presentation is omitted.
    native!(EMBLEM_UPDATE_STATE, unsafe extern "C" fn(Object, Method))(god, NONE);
    native!(INHERIT_APTITUDE, unsafe extern "C" fn(Object, Object, Method))(unit, god, NONE);
    let pid = native!(UNIT_PID, unsafe extern "C" fn(Object, Method) -> Object)(unit, NONE);
    native!(CLEAR_RELIANCE, unsafe extern "C" fn(Object, Method))(pid, NONE);
    let data = native!(GOD_DATA, unsafe extern "C" fn(Object, Method) -> Object)(god, NONE);
    if !data.is_null() {
      native!(CLEAR_RELIANCE, unsafe extern "C" fn(Object, Method))(
        field::<Object>(data, 0x20),
        NONE,
      );
    }
  }
}
