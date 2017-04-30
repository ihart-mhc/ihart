# Change Log
All notable changes to the iHart server will be documented in this file.
This project does its best to adhere to [Semantic Versioning](http://semver.org/).

## [Dev]
### Fixed
- The program quits when the "X" button in the window is clicked

### Added
- There is now a Python client.

### Changed
- Messages are sent as JSON instead of a custom format. This is *not* backwards compatible with the Flash client, and there are no plans to update it. The Java client and the Python client use JSON.
- The Java client library API for accessing event information has been updated.

## [2.3.1]
### Fixed
- The `--cameraindex` flag should be recognized when autostarting as well as during normal startup.

## [2.3] -- 2016-02-24
### Added
- `--autostart` and `--cameraindex` command-line flags allow the server to be started immediately, bypassing the startup window.
- A default area of interest covering most of the screen is created when the server starts.

## [2.2] -- 2016-02-11
### Added
- Allow user to resize start and control windows.

### Changed
- Faces and help images are enabled in the exported application.

## [2.1] -- 2015-02-11
### Added
- Allow user to quit at startup.

### Changed
- Remove regions of interest by right-clicking with the mouse instead of using the reset interest areas trackbar.

### Fixed
- The "Quit" trackbar actually works as the camera object is properly disposed when exiting.
- Help window no longer freezes program.

## [2.0] -- ??
- Initial port of the server to Python.

## [1.0] -- ??
- Original server, made with Processing.
