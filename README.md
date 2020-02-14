# microparse
A small Python program to parse Molecular Devices microplate reader .txt files to CSV or numpy vectors.
Can be used standalone or included as part of another program.

**usage:** `microparse.py` `[-h]` `[-o output]` `INPUT`

| positional argument   | description                           |
|-----------------------|---------------------------------------|
| input                  | The input Molecular Devices text file.|

| optional argument                       | description                           |
|-----------------------------------------|---------------------------------------|
| `-h`, `--help`                          | show this help message and exit       |
|  `-o` `[output]`, `--output` `[output]` | (optional) The output .csv file name. If left blank, will be the input filename with extension .csv  |
