import typing
import glob, os, csv
from parsing import CQASMParser
from metrics.longestRepeatingSubcircuit import longestRepeatingSubcircuit
from metrics.paths import getPathStats
from multiprocessing import Pool, Value
from threading import Lock

OUTPUT_FILE = os.path.dirname(os.path.realpath(__file__)) + "/result.csv"

files = glob.glob(os.path.dirname(os.path.realpath(__file__)) + "/metrics/data/*.qasm")

files = files[:5]
files = ["metrics/data/3_17_13.qasm", "metrics/data/4_49_16.qasm"]

lock = Lock()
counter = Value('i', 0)

statistics = sorted([
    "FileName",
    "SubcircuitIndex",
    "LengthOfLongestRepeatingSubcircuit",
    "NumberOfRepetitionsOfLongestRepeatingSubcircuit",
    "NumberOfGatesInCriticalPath",
    "MaxNumberOfTwoQubitGatesInCriticalPath",
    "NumberOfCriticalPaths",
    "NumberOfCriticalPathsWithMaxTwoQubitsGates",
    "PathLengthMean",
    "PathLengthStandardDeviation",
])

def writeToFile(data: dict):
    lock.acquire()
    with open(OUTPUT_FILE, "a") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=statistics)
        assert(sorted(data.keys()) == statistics)
        writer.writerow(data)
    
    global counter
    print(f"Done {counter.value} / {len(files)} files")
    counter.value += 1
    lock.release()


def processFile(fileName):
    try:
        ast = CQASMParser.parseCQASMFile(fileName)
    except Exception as e:
        print(f"File {fileName} gave error: {e}")
        return

    for index, subcircuit in enumerate(ast.subcircuits):
        repeatingSubcircuitStats = longestRepeatingSubcircuit(subcircuit.instructions)
        lengthOfLongestRepeatingSubcircuit = len(repeatingSubcircuitStats["LongestRepeatingSubcircuit"])
        numberOfRepetitionsOfLongestRepeatingSubcircuit = repeatingSubcircuitStats["NumberOfRepetitionsOfLongestRepeatingSubcircuit"]

        pathStats = getPathStats(subcircuit.instructions)

        thisSubcircuitData = {
            "FileName": os.path.basename(fileName),
            "SubcircuitIndex": index,
            "LengthOfLongestRepeatingSubcircuit": lengthOfLongestRepeatingSubcircuit,
            "NumberOfRepetitionsOfLongestRepeatingSubcircuit": numberOfRepetitionsOfLongestRepeatingSubcircuit,
            "NumberOfGatesInCriticalPath": pathStats["NumberOfGatesInCriticalPath"],
            "MaxNumberOfTwoQubitGatesInCriticalPath": pathStats["MaxNumberOfTwoQubitGatesInCriticalPath"],
            "NumberOfCriticalPaths": pathStats["NumberOfCriticalPaths"],
            "NumberOfCriticalPathsWithMaxTwoQubitsGates": pathStats["NumberOfCriticalPathsWithMaxTwoQubitsGates"],
            "PathLengthMean": pathStats["PathLengthMean"],
            "PathLengthStandardDeviation": pathStats["PathLengthStandardDeviation"],
        }

        writeToFile(thisSubcircuitData)


if __name__ == "__main__":
    with open(OUTPUT_FILE, "w") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=statistics)
        writer.writeheader()
    
    for f in files:
        processFile(f)

    # with Pool(8, initargs = (counter, )) as p:
    #     p.map(processFile, files)
