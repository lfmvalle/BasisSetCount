<p align="center">
  <a href="../README.md">
    <img src="https://img.shields.io/badge/↩-README-white?style=for-the-badge">
  </a>
</p>

# Changelog

All notable changes to this project will be documented in this file.

---

## [0.2.0] - 2026-03-10

### Added
- Parsing of Mulliken population analysis from output files.

### Changed
- Decimal numbers from output files are parsed to Decimal objects;
- Improved internal parsing structure for output sections;
- Reshaped entire TextStyle class to wrapper functions for strings. Styled strings are now strings with style keywords compatible with Rich implementations.

---

## [0.1.0] - 2026-03-09

### Added
- Initial release with versioning;
- Basis set extraction from calculation outputs.