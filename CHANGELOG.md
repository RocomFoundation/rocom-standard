# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added
- `illegal.json` with prohibited phrases list
- `file_check.py` - registry path resolution utility for illegal.json (designed with the help of Mistral Vibe)

### Changed
- Added `.vibe` to `.gitignore`
- Restructured `.github/workflows/pages.yml` workflow (added pull trigger, conditional job execution)
- Updated `check_site_match` job in pages.yml to use nested steps structure for running `python file_check.py` (designed with the help of Mistral Vibe)
- Enhanced `file_check.py` with full CLI scanner: loads illegal phrases, scans spec/ directory for matches, supports case-sensitive flag and custom directory (designed with the help of Mistral Vibe)

## Release History

Refer to the [CP Registry](spec/cp-registry.md) for detailed change tracking of Correction Proposals and Supplements.
