[↩ README](../README.md) | [◀ Installation](installation.md) | [Enumeration of $m_l$ functions ▶](usage_enum.md)

# Atoms and unique basis sets information

Let `bscount` be the alias poiting to this script and `[output_file]` a generic output with 50 atoms.

## Informations about atoms
`$ bscount [output_file] -a` <br> Outputs a table with information about the atoms from `[output_file]`, but not their basis sets.

## Information about unique basis sets
`$ bscount [output_file] -b` <br> Outputs a table with information about unique basis sets from `[output_file]`.

## Combined information
`$ bscount [output_file]` ; or <br> `$ bscount [output_file] -a -b` <br> Combines the functionalities of both atom and unique basis set information from `[output_file]`.

> **NOTE:** <br> The order of the parameters passed in the script call dictates the order of the output.