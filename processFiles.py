import typing
import glob, os, csv
from parsing import CQASMParser
from metrics.longestRepeatingSubcircuit import longestRepeatingSubcircuit
from metrics.paths import getPathStats
from multiprocessing import Pool, Value

OUTPUT_FILE = os.path.dirname(os.path.realpath(__file__)) + "/result.csv"


# MAX_NUM_LINES = 50000
# files = []

# for f in glob.glob(os.path.dirname(os.path.realpath(__file__)) + "/metrics/data/*.qasm"):
#     num_lines = sum(1 for _ in open(f))

#     if num_lines > MAX_NUM_LINES:
#         files.append(f)

files = glob.glob(os.path.dirname(os.path.realpath(__file__)) + "/metrics/data/*.qasm")

# files = ["/shares/bulk/plehenaff/cQASM-tools/metrics/data/q=11_s=89_2qbf=022_1.qasm"]

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
    with open(OUTPUT_FILE, "a") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=statistics)
        assert(sorted(data.keys()) == statistics)
        writer.writerow(data)
    
    global counter
    counter.value += 1
    print(f"Done {counter.value} / {len(files)} files")

def processFile(fileName):
    try:
        ast = CQASMParser.parseCQASMFile(fileName)

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
        
    except Exception as e:
        print(f"File {fileName} gave error: {e} and was not processed")

        return
    


if __name__ == "__main__":
    # print(f"Will process files: {files}")

    with open(OUTPUT_FILE, "w") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=statistics)
        writer.writeheader()
    
    # for f in files:
    #     print(f"processing {f}")
    #     processFile(f)
    
    with Pool(8, initargs = (counter, )) as p:
        p.map(processFile, files)
