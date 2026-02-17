<p align="center">
  <a href="../README.md">
    <img src="https://img.shields.io/badge/↩-README-white?style=for-the-badge">
  </a>
  <a href="nomenclature.md">
    <img src="https://img.shields.io/badge/◀ - Nomenclature of atomic orbitals-blue?style=for-the-badge">
  </a>
  <a href="ghost.md">
    <img src="https://img.shields.io/badge/▶ - Ghost atoms-blue?style=for-the-badge">
  </a>
</p>

# Effective Core Potential basis sets

Currently, *Effective Core Potential* (ECP) basis sets are distinguished from *all-electron* basis sets only upon printing information.

Both ECP and all-electron basis sets use the same parsing logic for gathering information. This means that the enumeration follows the same rules, and both types of basis sets are enumerated in the same way.

The type of basis set is collected from the `PSEUDOPOTENTIAL INFORMATION` section of the output file.

>**IMPORTANT NOTE:** <br> Tests with ECP basis sets were done using a [*Hay and Wadt Small-Core (HAYWSC) ECP for Ag atoms*](https://www.crystal.unito.it/Basis_Sets/silver.html#Ag_HAYWSC-2111d31G_kokalj_1998_unpub). <br> Problems indentifying other types of ECP basis sets are very unlikely, **but it may occur**. Please treat the results carefully when dealing with ECP basis sets, and make sure to comunicate any issues you found.