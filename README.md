# microparse

A small Python program to parse Molecular Devices microplate reader .txt files to CSV or numpy vectors.
Can be used standalone or included as part of another program.

**usage**: `microparse.py` `[-h]` `[-i INPUT [INPUT ...]]` `[-o OUTPUT [OUTPUT ...]]` `[-v]` `[-vv]`

A small program to convert Molecular Devices microplate reader .txt files to
the .csv format, or to be used in Python 3 scripts.

| argument                                              | Description                                                 |
|-------------------------------------------------------|-------------------------------------------------------------|
|  -h, --help                                           | show this help message and exit                             |
|  -i INPUT [INPUT ...], --input INPUT [INPUT ...]      | the input Molecular Devices text filenames.                 |
|  -o OUTPUT [OUTPUT ...], --output OUTPUT [OUTPUT ...] | the output .csv filenames. (autogenerated if not specified) |
|  -v, --verbose                                        | enables debug printing                                      |
|  -vv, --veryverbose                                   | extra debug printing

## examples as a program

```shell
$ ./microparse.py molDeviceFile.txt
$ ls
molDeviceFile.csv  -i molDeviceFile.txt
$ ./microparse.py -i molDeviceFile.txt -o someOtherBetterName.csv
$ ls
molDeviceFile.csv  molDeviceFile.txt  someOtherBetterName.csv
```
You may also run `microparse.py -h` for help at any time.

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

If you want `timeSeries`, `tempSeries`, or the series in `experiments` to return as numpy arrays/vectors, set `useNumPy` to `True` when decoding:

```python
import microparse

testfile = microparse.rawFile('molDeviceFile.txt')
decodedTestFile = testfile.decode(useNumPy=True)

# The actual data a file contains! But they're NumPy arrays!
decodedTestFile.timeSeries
decodedTestFile.tempSeries
decodedTestFile.experiments
```
