Rescale IV data to another tempature
====================================
A litte python script to rescale IV data of Si sensors to another tempature and plot the results and the reference data with ROOT.

Installation
------------
Download the [python script](rescale.py) and setup your root env (e.g. initroot 5.34) before calling the script.

Usage
-----
You can get a overview of all option by calling the script without any args:
```bash
python path/to/rescale.py
```

Example
-------
If you want to rescale a measurement done at -40C to -25C you can call the script like this:
```bash
python path/to/rescale.py --skip 0 Data_40C.txt ReferenceData_40C.txt -25 "A nice plot title" "Data -40#circC" "Data -25#circC" "Data rescaled to -25#circC with 1.12 eV gap"
```

License
-------
For the GPL see the [LICENSE](LICENSE) file.

rescale.py - Rescale IV data to another tempature
Copyright (C) 2015 Jan Luca Naumann

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
