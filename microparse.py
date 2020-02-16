#!/bin/python3


class rawFile(object):

    def __init__(self, filename, isVerbose=False, isVeryVerbose=False):
        '''
        a raw microplate devices file to be decoded.
        expects a filename.
        '''
        self.filename = filename
        self.isVerbose = isVerbose
        self.isVeryVerbose = isVeryVerbose
        self.numHeaderLines = 3

        if self.isVeryVerbose:

            print("Reading file " + self.filename)

        with open(self.filename, encoding="latin-1") as file:
            self.removeHeader(file)
            boundaryList = self.generateBoundaryList(file)

        with open(self.filename, encoding="latin-1") as file:

            self.chunks = chunkList(boundaryList, fileContent,
                                    isVerbose=self.isVerbose,
                                    isVeryVerbose=self.isVeryVerbose)

    def removeHeader(self, fileIterable):
        '''
        The above line gets rid of header information. In the future this
        may be used in order to parse files differently, but for our
        purposes where we just want to extract data from the series runs of
        the microplate reader, this is okay.
        '''

        for i in range(0, self.numHeaderLines):
            next(fileIterable)

    def generateBoundaryList(self, fileIterable):
        '''
        Uses the whitespace formatting to generate a sequence to break a raw
        file into time domain chunks.
        '''

        boundaryList = [i - self.numHeaderLines for i, line in
                        enumerate(fileIterable) if line == "\t\t\n"]

        if self.isVeryVerbose:

            print("generated boundaryList for :" + self.filename)
            print(boundaryList)

        return boundaryList

    def decode(self, useNumPy=False):
        '''
        Decodes a rawFile and returns a decodedFile to use.
        '''
        timeSeries = []
        tempSeries = []
        experiments = []

        for experiment in range(0, self.chunks.chunkLength):
            experiments.append([])
            '''
            Taking advantage of the fact that each line in a chunk corresponds
            to a different experiment series here. This sets up the correct no.
            of lists to organize experimentData into.
            '''

        for chunk in self.chunks:

            timeSeries.append(chunk.secondsElapsed)
            tempSeries.append(chunk.temperature)

            for experiment in range(0, len(chunk.experiments)):
                experiments[experiment].append(chunk.experiments[experiment])

        return parsedFile(timeSeries, tempSeries, experiments, useNumPy,
                          isVerbose=self.isVerbose,
                          isVeryVerbose=self.isVeryVerbose)


class chunk(object):

    def __init__(self, lines, isVerbose=False, isVeryVerbose=False):
        '''
        A data object used in chunkList. Expects a set of lines that
        make up a file chunk in the rawFile.fileContent
        '''
        self.rawFileChunk = lines
        self.isVerbose = isVerbose
        self.isVeryVerbose = isVeryVerbose

        self.secondsElapsed = 0
        self.temperature = 0
        self.experiments = []

        self.processRawFileChunk()

    def __len__(self):
        return len(self.rawFileChunk)

    def processRawFileChunk(self):
        '''
        Extracts data from a chunk. The experiment data is returned as
        a list with each value being from a different series.
        '''

        def getSecondsElapsed():
            '''
            Gets the time of recording of the datachunk
            '''

            def transformStringTimeToSeconds(stringTime):
                '''
                takes a string representation with values formatted as
                hh:mm:ss and converts it to a list of elapsed seconds.
                '''

                hhmmssStrings = stringTime.split(":")
                hhmmssValues = [int(xx) for xx in hhmmssStrings]

                if len(hhmmssValues) == 1:

                    secondsElapsed = hhmmssValues[0]

                elif len(hhmmssValues) == 2:

                    secondsElapsed = 60 * hhmmssValues[0] \
                        + hhmmssValues[1]

                elif len(hhmmssValues) == 3:

                    secondsElapsed == 3600 * hhmmssValues[0] \
                        + 60 * hhmmssValues[1] + hhmmssValues[2]

                return secondsElapsed

            self.secondsElapsed = \
                transformStringTimeToSeconds(self.rawFileChunk[0]
                                             .split()[0])

        def getTemperature():
            '''
            Gets the temperature at the time of recording for the data
            chunk
            '''
            self.temperature = float(self.rawFileChunk[0].split()[1])

        def getExperiments():
            '''
            Gets the data for the set of experiments taken at
            self.secondsElapsed
            '''
            # Handle the first line
            data = [float(self.rawFileChunk[0].split()[2])]
            # Handle the rest
            for line in self.rawFileChunk[1:]:
                data.append(float(line.split()[0]))

            self.experiments = data

        getSecondsElapsed()
        getTemperature()
        getExperiments()


class chunkList(object):

    def __init__(self, boundaryList, fileContent, isVerbose=False,
                 isVeryVerbose=False):
        '''
        generates 'chunks' or vertical slices of all series data at one
        timepoint via the values in boundaries.
        '''
        self.data = []
        self.isVerbose = isVerbose
        self.isVeryVerbose = isVeryVerbose

        previousBound = 0
        for bound in boundaryList:
            self.data.append(chunk(fileContent[previousBound:bound],
                                   isVerbose=self.isVerbose,
                                   isVeryVerbose=self.isVeryVerbose))
            previousBound = bound + 1

        self.chunkLength = len(self.data[0])
        self.__chunkIndex = 0

        if self.isVeryVerbose:

            print("finished instantiating chunkList")

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return self

    def __next__(self):
        if self.__chunkIndex >= len(self):
            raise StopIteration
        else:
            self.__chunkIndex += 1
            return self.data[self.__chunkIndex - 1]


class parsedFile(object):

    def __init__(self, timeSeries, tempSeries, experiments, useNumPy=False,
                 isVerbose=False, isVeryVerbose=False):

        self.isVerbose = isVerbose
        self.isVeryVerbose = isVeryVerbose

        if useNumPy:

            import numpy
            self.timeSeries = numpy.array(timeSeries)
            self.tempSeries = numpy.array(tempSeries)
            self.experiments = [numpy.array(experiment) for
                                experiment in experiments]
        else:
            self.timeSeries = timeSeries
            self.tempSeries = tempSeries
            self.experiments = experiments

    def writeToCSV(self, filename):

        numberOfRows = len(self.timeSeries)
        numberOfSeriesColumns = len(self.experiments)

        def makeHeader():
            seriesHeaders = []
            for seriesnumber in range(1, numberOfSeriesColumns + 1):
                seriesHeaders.append("Series No. {}".format(seriesnumber))
            return ['Time (s)', 'Temperature (C)'] + seriesHeaders

        def makeRow(rowNumber):
            ''' makes a row of a csv table using the parsed file object and an
                arbitrary row number '''
            timeTempColumns = [self.timeSeries[rowNumber],
                               self.tempSeries[rowNumber]]
            experimentColumns = [experiment[rowNumber] for experiment
                                 in self.experiments]

            return timeTempColumns + experimentColumns

        if self.isVeryVerbose:

            print("Finished processing csv table for ")


        import csv

        with open(filename, 'w') as csvfile:

            writer = csv.writer(csvfile)
            writer.writerow(makeHeader())
            for currentRow in range(0, numberOfRows):
                writer.writerow(makeRow(currentRow))

        if self.isVerbose:

            print("Wrote output csv file: " + filename)


def main():

    import argparse
    import pathlib

    def processFile(filename, output=None, isVerbose=False,
                    isVeryVerbose=False):
        '''
        Takes an inputfile and makes it a .csv, named output.csv if output is
        provided
        '''

        filepath = pathlib.Path(filename)

        if not filepath.exists():

            print(filename + ": file does not exist")
            return 1

        if output:

            rawFile(filename,
                    isVerbose=isVerbose,
                    isVeryVerbose=isVeryVerbose).decode().writeToCSV(output)
        else:

            if isVeryVerbose:
                print("auto-generated output filename: " +
                      filename.split(".")[0] + ".csv")

            rawFile(filename,
                    isVerbose=isVerbose,
                    isVeryVerbose=isVeryVerbose)\
                .decode().writeToCSV(filename.split(".")[0] + ".csv")

    parser = argparse.ArgumentParser(description='A small program to convert '
                                                 'Molecular Devices microplate'
                                                 ' reader .txt files to the '
                                                 '.csv format, or to be used '
                                                 'in Python 3 scripts.',
                                     epilog='Written by Matthew B. Wilson '
                                            '2020')

    parser.add_argument('-i', '--input', type=str, help='''\
                        The input Molecular Devices text filenames.''',
                        nargs='+')

    parser.add_argument('-o', '--output', type=str, help='''\
                        the output .csv filenames.''', nargs='+')

    parser.add_argument('-v', '--verbose', action='store_true', help='''\
                        enables debug printing''')

    parser.add_argument('-vv', '--veryverbose', action='store_true', help='''\
                        extra debug printing''')

    args = parser.parse_args()

    if args.input:

        if args.output:

            if len(args.output) != len(args.input):
                print('error: number of outputs must match number of inputs')
                return 1

            for inputFile, outputFile in zip(args.input, args.output):

                processFile(inputFile, output=outputFile,
                            isVerbose=(args.verbose or args.veryverbose),
                            isVeryVerbose=args.veryverbose)

        else:

            for inputFile in args.input:

                processFile(inputFile,
                            isVerbose=(args.verbose or args.veryverbose),
                            isVeryVerbose=args.veryverbose)

        print("done. {} files processed.".format(len(args.input)))

    else:

        parser.print_help()

    return 0


if __name__ == '__main__':
    main()
