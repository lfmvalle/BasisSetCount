[↩ README](../README.md) | [◀ Enumeration of $m_l$ functions](usage_enum.md) | [ Effective Core Potential basis sets ▶](ecp.md)

# Nomenclature of $m_l$ functions

Due to their complex mathematical forms, identifying **F**- and **G**-type orbitals proves to be quite hard. Remembering the order in which they are implemented in CRYSTAL is even harder, even after months - or maybe years - of practice.

To facilitate this identification, this script adopts a more concise plain-text nomenclature, described in the table below (you'll notice a pattern if you pay close attetion).

>**INFO:** <br> All the mathematical functions described here follows the same description and order found in [CRYSTAL 23 User's Manual](https://www.crystal.unito.it/include/manuals/crystal23.pdf).

| Order | Mathematical description of the $m_l$ function       | plain-text |
| :---: | :---                                                 | :--- |
|       | Description for **P** functions                      | |
| 1     | $x$                                                  | p [ x ] |
| 2     | $y$                                                  | p [ y ] |
| 3     | $z$                                                  | p [ z ] |
|       | Description for **D** functions                      | |
| 1     | $z^2 - x^2 - y^2$                                    | d [ z2 ] |
| 2     | $xz$                                                 | d [ xz ] |
| 3     | $yz$                                                 | d [ yz ] |
| 4     | $x^2 - y^2$                                          | d [ x2y2 ] |
| 5     | $xy$                                                 | d [ xy ] |
|       | Description for **F** functions                      | |
| 1     | $(2z^2 - 3x^2 - 3y^2)z$                              | f [ z2z ] |
| 2     | $(4z^2 - x^2 - y^2)x$                                | f [ z2x ] |
| 3     | $(4z^2 - x^2 - y^2)y$                                | f [ z2y ] |
| 4     | $(x^2 - y^2)z$                                       | f [ x2z ] |
| 5     | $xyz$                                                | f [ xyz ] |
| 6     | $(x^2 - 3y^2)x$                                      | f [ x2x ] |
| 7     | $(3x^2 - y^2)y$                                      | f [ x2y ] |
|       | Description for **G** functions                      | |
| 1     | $3x^4 + 6x^2y^2 - 24x^2z^2 + 3y^4 - 24y^2z^2 + 8z^2$ | g [ x4z2 ] |
| 2     | $(4z^2 - 3x^2 - 3y^2)xz$                             | g [ z2xz ] |
| 3     | $(4z^2 - 3x^2 - 3y^2)yz$                             | g [ z2yz ] |
| 4     | $6x^2z^2 - x^4 + y^4 - 6y^2z^2$                      | g [ x2z2 ] |
| 5     | $(6z^2 - x^2 - y^2)xy$                               | g [ z2xy ] |
| 6     | $(x^2 - 3y^2)xz$                                     | g [ x2xz ] |
| 7     | $(3x^2 - y^2)yz$                                     | g [ x2yz ] |
| 8     | $x^4 - 6x^2y^2 + y^4$                                | g [ x4y4 ] |
| 9     | $(x^2 - y^2)xy$                                      | g [ x2xy ] |