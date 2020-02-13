#!/bin/python3

def parse(filename, useNumpy=False):
    ''' a parser for Molecular Devices microplate reader files, to convert to
        a .csv, numpy vectors, or lists '''

    def transformRemoveHeader(lineList):
        ''' The above line gets rid of header information. In the future this
            may be used in order to parse files differently, but for our
            purposes where we just want to extract data from the series runs of
            the microplate reader, this is okay. '''

        return lineList[3:]

    def generateBoundaryList(noHeaderLineList):
        ''' Generates the series of partitioning values which divide the
            filecontent into time-domain structured table rows '''

        return [i for i, line in enumerate(noHeaderLineList)
                if line == '\t\t\n']

    def generateChunkList(boundaryList, noHeaderLineList):
        ''' generates 'chunks' or vertical slices of all series data at one
            timepoint via the values in boundaries. '''

        chunkList = []

        previousBound = 0
        for bound in boundaryList:
            chunkList.append(noHeaderLineList[previousBound:bound])
            previousBound = bound + 1

        return chunkList

    def transformStringTimeToSeconds(stringTime):
        ''' takes a stringList with values formatted as hh:mm:ss and converts
            it to a list of elapsed seconds. '''

        hhmmssStrings = stringTime.split(":")
        hhmmssValues = [int(xx) for xx in hhmmssStrings]

        if len(hhmmssValues) == 1:

            secondsElapsed = hhmmssValues[0]

        elif len(hhmmssValues) == 2:

            secondsElapsed = 60 * hhmmssValues[0] + hhmmssValues[1]

        elif len(hhmmssValues) == 3:

            secondsElapsed == 3600 * hhmmssValues[0] \
                + 60 * hhmmssValues[1] + hhmmssValues[2]

        return secondsElapsed

    def getSeparatedChunkData(chunk):
        ''' Extracts data from a chunk. The experiment data is returned as a
            list with each value being from a different series. '''

        secondsData = 0
        temperatureData = 0
        experimentData = []

        currentLine = 0
        for line in chunk:
            ''' recall that using split() without any parameters will remove
                all whitespace. '''
            lineSplitList = line.split()
            if currentLine == 0:
                secondsData = transformStringTimeToSeconds(lineSplitList[0])
                temperatureData = float(lineSplitList[1])
                experimentData.append(float(lineSplitList[2]))
            else:
                experimentData.append(float(lineSplitList[0]))

            currentLine += 1

        return [secondsData, temperatureData, experimentData]

    def generateAllSeries(chunkList):
        ''' Takes a chunklist and gets data for all the chunks and organizes
            that data into time-domain lists. '''

        chunkLength = len(chunkList[0])

        experimentSeriesList = []
        timeSeries = []
        tempSeries = []

        for experiment in range(0, chunkLength):
            experimentSeriesList.append([])
        ''' Taking advantage of the fact that each line in a chunk corresponds
            to a different experiment series here. This sets up the correct no.
            of lists to organize experimentData into. '''

        for chunk in chunkList:

            time, temp, experimentData = getSeparatedChunkData(chunk)

            currentExperimentSeries = 0
            for experimentValue in experimentData:

                experimentSeriesList[currentExperimentSeries].append(
                    experimentValue)
                currentExperimentSeries += 1

            timeSeries.append(time)
            tempSeries.append(temp)

        return [timeSeries, tempSeries, experimentSeriesList]

    def convertAllSeriesToNumpy(allSeriesList):

        import numpy as np

        timeNumpySeries = np.array(allSeriesList[0])
        tempNumpySeries = np.array(allSeriesList[1])
        experimentNumpySeriesList = [np.array(experimentSeries)
                                     for experimentSeries in allSeriesList[2]]

        return [timeNumpySeries, tempNumpySeries, experimentNumpySeriesList]

    '''
    Begin Function
    '''
    with open(filename, encoding='utf-8') as file:
        content = file.readlines()

    content = transformRemoveHeader(content)
    boundaries = generateBoundaryList(content)
    chunks = generateChunkList(boundaries, content)

    if useNumpy is True:
        allSeries = convertAllSeriesToNumpy(generateAllSeries(chunks))
    else:
        allSeries = generateAllSeries(chunks)

    return allSeries


def writeToCSV(filename, parsedFileObject):

    numberOfRows = len(parsedFileObject[0])
    numberOfSeriesColumns = len(parsedFileObject[2])

    def makeHeader(parsedFileObject):
        seriesHeaders = []
        for seriesnumber in range(1, numberOfSeriesColumns + 1):
            seriesHeaders.append("Series No. {}".format(seriesnumber))
        return ['Time (s)', 'Temperature (C)'] + seriesHeaders

    def makeRow(parsedFileObject, rowNumber):
        ''' makes a row of a csv table using the parsed file object and an
            arbitrary row number '''
        timeTempColumns = [parsedFileObject[0][rowNumber],
                           parsedFileObject[1][rowNumber]]
        experimentColumns = [experimentSeries[rowNumber] for experimentSeries
                             in parsedFileObject[2]]

        return timeTempColumns + experimentColumns

    import csv

    with open(filename, 'w') as csvfile:

        writer = csv.writer(csvfile)
        writer.writerow(makeHeader(parsedFileObject))
        for currentRow in range(0, numberOfRows):
            writer.writerow(makeRow(parsedFileObject, currentRow))


def main():

    import argparse

    parser = argparse.ArgumentParser(description='A small program to convert '
                                                 'Molecular Devices microplate'
                                                 ' reader .txt files to the '
                                                 '.csv format, or to be used '
                                                 'in Python 3 scripts.',
                                     epilog='Written by Matthew B. Wilson '
                                            '2020')
    parser.add_argument('input', metavar='input', type=str, help='''\
                        The input Molecular Devices text file.''', nargs='?')
    parser.add_argument('-o', '--output', metavar='output', type=str, help='''\
                        (optional) The output .csv file name''', nargs='?',)

    args = parser.parse_args()
    assert args.input is not None,"Need an input file!" 

    if args.output:
        writeToCSV(args.output, parse(args.input))
    else:
        writeToCSV(args.input.split('.')[0] + '.csv', parse(args.input))

    return 0


if __name__ == '__main__':
    main()
