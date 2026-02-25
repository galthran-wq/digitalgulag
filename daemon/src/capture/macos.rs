use crate::capture::ActivitySource;
use crate::error::Result;
use crate::events::WindowInfo;
use std::ffi::c_void;
use std::sync::atomic::{AtomicBool, Ordering};

use objc2_app_kit::NSWorkspace;
use objc2_core_foundation::{CFDictionary, CFNumber, CFString};
use objc2_core_graphics::{
    kCGWindowLayer, kCGWindowName, kCGWindowOwnerPID, CGWindowListCopyWindowInfo,
    CGWindowListOption,
};

static SCREEN_RECORDING_WARNED: AtomicBool = AtomicBool::new(false);

pub struct MacOSSource;

impl MacOSSource {
    pub fn new() -> Self {
        tracing::info!("macOS capture initialized (NSWorkspace + CGWindowList)");
        Self
    }

    /// Get the frontmost application's display name and PID.
    /// Does NOT require Screen Recording permission.
    fn get_frontmost_app(&self) -> Option<(String, i32)> {
        let workspace = NSWorkspace::sharedWorkspace();
        let app = workspace.frontmostApplication()?;

        let name = app.localizedName()?;
        let pid = app.processIdentifier();
        if pid <= 0 {
            return None;
        }

        Some((name.to_string(), pid))
    }

    /// Get the window title for a given PID using CGWindowListCopyWindowInfo.
    /// Requires Screen Recording permission for window titles.
    /// Returns None if permission not granted or no matching window found.
    fn get_window_title_for_pid(&self, target_pid: i32) -> Option<String> {
        let options =
            CGWindowListOption::OptionOnScreenOnly | CGWindowListOption::ExcludeDesktopElements;
        let window_list = CGWindowListCopyWindowInfo(options, 0)?;

        let count = window_list.len();
        let mut found_window = false;

        for i in 0..count {
            // SAFETY: i is within 0..count. The array contains CFDictionary entries
            // per CGWindowListCopyWindowInfo documentation.
            let dict_ptr = unsafe { window_list.value_at_index(i as isize) };
            if dict_ptr.is_null() {
                continue;
            }
            let dict = unsafe { &*(dict_ptr as *const CFDictionary) };

            // Check if this window belongs to our target PID
            let pid = cf_dict_get_i32(dict, &kCGWindowOwnerPID);
            if pid != Some(target_pid) {
                continue;
            }

            // Filter to normal windows (layer 0) — skip menubar, dock, etc.
            if cf_dict_get_i32(dict, &kCGWindowLayer).unwrap_or(-1) != 0 {
                continue;
            }

            found_window = true;

            // Extract window title — absent when Screen Recording permission not granted
            if let Some(title) = cf_dict_get_string(dict, &kCGWindowName) {
                if !title.is_empty() {
                    return Some(title);
                }
            }
        }

        if found_window && !SCREEN_RECORDING_WARNED.swap(true, Ordering::Relaxed) {
            tracing::warn!(
                "Window titles unavailable — grant Screen Recording permission to TimeOracle \
                 in System Settings > Privacy & Security > Screen Recording"
            );
        }

        None
    }
}

/// Extract an i32 value from a CFDictionary by CFString key.
fn cf_dict_get_i32(dict: &CFDictionary, key: &CFString) -> Option<i32> {
    let ptr = unsafe { dict.value(key as *const CFString as *const c_void) };
    if ptr.is_null() {
        return None;
    }
    unsafe { &*(ptr as *const CFNumber) }.as_i32()
}

/// Extract a String value from a CFDictionary by CFString key.
fn cf_dict_get_string(dict: &CFDictionary, key: &CFString) -> Option<String> {
    let ptr = unsafe { dict.value(key as *const CFString as *const c_void) };
    if ptr.is_null() {
        return None;
    }
    Some(unsafe { &*(ptr as *const CFString) }.to_string())
}

impl ActivitySource for MacOSSource {
    fn get_active_window(&self) -> Result<Option<WindowInfo>> {
        let (app_name, pid) = match self.get_frontmost_app() {
            Some(info) => info,
            None => return Ok(None),
        };

        let window_title = self.get_window_title_for_pid(pid).unwrap_or_default();

        Ok(Some(WindowInfo {
            app_name,
            window_title,
            url: None,
        }))
    }
}
