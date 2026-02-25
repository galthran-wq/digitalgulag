mod buffer_sync;

#[cfg(target_os = "linux")]
mod capture_linux;

#[cfg(target_os = "macos")]
mod capture_macos;
