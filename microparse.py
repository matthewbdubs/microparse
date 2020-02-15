#!/bin/python3


class rawFile(object):

    def __init__(self, filename):
        '''
        a raw microplate devices file to be decoded.
        expects a filename.
        '''
        with open(filename, encoding="utf-8") as file:
            rawContent = file.readlines()
            fileContent = self.removeHeader(rawContent)

        self.chunks = chunkList(self.generateBoundaryList(fileContent),
                                fileContent)

    def removeHeader(self, rawContent):
        '''
        The above line gets rid of header information. In the future this
        may be used in order to parse files differently, but for our
        purposes where we just want to extract data from the series runs of
        the microplate reader, this is okay.
        '''

        return rawContent[3:]

    def generateBoundaryList(self, fileContent):
        '''
        Uses the whitespace formatting to generate a sequence to break a raw
        file into time domain chunks.
        '''
        return [i for i, value in enumerate(fileContent) if value == "\t\t\n"]

    def decode(self):
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

        return parsedFile(timeSeries, tempSeries, experiments)


class chunk(object):

    def __init__(self, lines):
        '''
        A data object used in chunkList. Expects a set of lines that
        make up a file chunk in the rawFile.fileContent
        '''
        self.rawFileChunk = lines

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

    def __init__(self, boundaryList, fileContent):
        '''
        generates 'chunks' or vertical slices of all series data at one
        timepoint via the values in boundaries.
        '''
        self.data = []

        previousBound = 0
        for bound in boundaryList:
            self.data.append(chunk(fileContent[previousBound:bound]))
            previousBound = bound + 1

        self.chunkLength = len(self.data[0])
        self.__chunkIndex = 0

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

    def __init__(self, timeSeries, tempSeries, experiments):

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

        import csv

        with open(filename, 'w') as csvfile:

            writer = csv.writer(csvfile)
            writer.writerow(makeHeader())
            for currentRow in range(0, numberOfRows):
                writer.writerow(makeRow(currentRow))


def main():

    import argparse
    import pathlib

    parser = argparse.ArgumentParser(description='A small program to convert '
                                                 'Molecular Devices microplate'
                                                 ' reader .txt files to the '
                                                 '.csv format, or to be used '
                                                 'in Python 3 scripts.',
                                     epilog='Written by Matthew B. Wilson '
                                            '2020')
    parser.add_argument('INPUT', type=str, help='''\
                        The input Molecular Devices text file.''')
    parser.add_argument('-o', '--output', metavar='output', type=str, help='''\
                        (optional) The output .csv file name.
                        If left blank, will be the input filename with
                        extension .csv''',)

    args = parser.parse_args()

    file = pathlib.Path(args.INPUT)
    if not file.exists():
        print(args.INPUT + ": file does not exist")
        return 1

    file = rawFile(args.INPUT)
    processedFile = file.decode()

    if args.output:
        processedFile.writeToCSV(args.output)
    else:
        processedFile.writeToCSV(args.INPUT.split('.')[0] + '.csv')

    return 0


if __name__ == '__main__':
    main()
