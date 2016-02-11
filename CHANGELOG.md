# Change Log
All notable changes to the iHart server will be documented in this file.
This project does its best to adhere to [Semantic Versioning](http://semver.org/).

## [Development]
### Added
- Allow user to resize start and control windows.

### Changed
- Use release() method instead of deleting self.videoCapture variable when quitting.

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
