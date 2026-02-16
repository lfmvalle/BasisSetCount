<p align="center">
  <a href="../README.md">
    <img src="https://img.shields.io/badge/↩-README-white?style=for-the-badge">
  </a>
  <a href="installation.md">
    <img src="https://img.shields.io/badge/◀ - Installation-blue?style=for-the-badge">
  </a>
  <a href="usage_enum.md">
    <img src="https://img.shields.io/badge/▶ - Enumeration of atomic orbitals-blue?style=for-the-badge">
  </a>
</p>

# Atoms and unique basis sets information

Let `bscount` be the alias poiting to this script and `[output_file]` a generic output with 50 atoms.

## Basic arguments
`$ bscount [output_file]` <br> Outputs the number of atoms, ghost atoms, and unique basis set from `[output_file]`. <br> This information is always printed.

`$ bscount [output_file] -a` <br> The **-a** argument outputs a table with detailed information about the atoms from the basis set section of the `[output_file]`.

`$ bscount [output_file] -b` <br> The **-b** argument outputs a table with detailed information about unique basis sets from `[output_file]`.

## Combining arguments
`$ bscount [output_file] -a -b` <br> Outputs tables for both atom and unique basis sets from `[output_file]`, respectively.

> **NOTE:** <br> The order of the parameters passed in the script call dictates the order of the output.