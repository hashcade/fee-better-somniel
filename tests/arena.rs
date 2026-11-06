use fee_better_somniel::arena::{DESCRIPTOR_COUNT, QUICK_ORDER};

#[test]
fn shortcut_order_retains_every_native_growth_step_once_and_in_order() {
  assert_eq!(QUICK_ORDER.len(), DESCRIPTOR_COUNT);
  assert_eq!(&QUICK_ORDER[..8], &[2, 3, 7, 8, 9, 10, 11, 13]);
  for step in [7, 8, 9] {
    assert_eq!(QUICK_ORDER.iter().filter(|index| **index == step).count(), 1);
  }
  assert!(QUICK_ORDER.iter().all(|i| *i < DESCRIPTOR_COUNT));
  assert!(QUICK_ORDER[8..].iter().all(|i| *i == 13));
  for presentation in [0, 1, 4, 5, 6, 12] {
    assert!(!QUICK_ORDER.contains(&presentation));
  }
}
