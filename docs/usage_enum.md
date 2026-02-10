[↩ README](../README.md) | [◀ Atoms and unique basis sets information](usage_info.md) | [Nomenclature of atomic orbitals ▶](nomenclature.md)

# Enumeration of atomic orbitals

Let `bscount` be the alias poiting to this script and `[output_file]` a generic output with 50 atoms.

## Enumeration for one or more atoms
`$ bscount [output_file] 41` <br> Outputs the enumeration of atomic orbitals for atom 41 of `[output_file]`.

`$ bscount [output_file] 41 45` <br> Outputs the enumeration of atomic orbitals for atoms 41 and 45 of `[output_file]`.

`$ bscount [output_file] 41-45` <br> Outputs the enumeration of atomic orbitals for atoms 41 to 45 (inclusive) of `[output_file]`.

## Enumeration for ghost atoms

`$ bscount [output_file] x` <br> Outputs the enumeration of atomic orbitals for all *ghost atoms* of `[output_file]`.

## Combined enumerations

`$ bscount [output_file] 12 41-45 x 24-26` <br> Outputs the enumeration of atomic orbitals for atom 12, atoms 41 to 45 (inclusive), all ghost atoms, and atoms 24 to 26 (inclusive) from `[output_file]`, respectively.

> **NOTE:** <br> The order of the parameters passed in the script call dictates the order in which the output is printed.