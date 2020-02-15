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

## examples as a program
```shell
$ ./microparse.py molDeviceFile.txt
$ ls
molDeviceFile.csv  molDeviceFile.txt
$ ./microparse.py molDeviceFile.txt -o someOtherBetterName.csv
$ ls

```
## using in a python script:
place microparse in the directory of your project/import libraries
```python
import microparse

testfile = microparse.rawFile('molDeviceFile.txt')
decodedTestFile = testfile.decode()

# The actual data a file contains!
decodedTestFile.timeSeries
decodedTestFile.tempSeries
decodedTestFile.experiments
```
`timeSeries` and `tempSeries` attributes are lists of values, while `experiments` is a list of lists -- or rather, a list of experimentSeries (which is nicer to think about).

```
