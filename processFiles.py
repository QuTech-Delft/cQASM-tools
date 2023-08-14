import typing
import glob, os, csv
from parsing import CQASMParser
from metrics.longestRepeatingSubcircuit import longestRepeatingSubcircuit
from multiprocessing import Pool, Value
from threading import Lock

OUTPUT_FILE = os.path.dirname(os.path.realpath(__file__)) + "/result.csv"

files = glob.glob(os.path.dirname(os.path.realpath(__file__)) + "/metrics/data/*.qasm")

files = files[:5]

lock = Lock()
counter = Value('i', 0)

statistics = sorted(["FileName", "SubcircuitIndex", "LengthOfLongestRepeatingSubcircuit", "NumberOfRepetitionsOfLongestRepeatingSubcircuit", "LengthOfCriticalPath"])

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
        res = longestRepeatingSubcircuit(subcircuit.instructions)
        lengthOfLongestRepeatingSubcircuit = len(res[0])
        numberOfRepetitionsOfLongestRepeatingSubcircuit = res[1]

        thisSubcircuitData = {
            "FileName": os.path.basename(fileName),
            "SubcircuitIndex": index,
            "LengthOfLongestRepeatingSubcircuit": lengthOfLongestRepeatingSubcircuit,
            "NumberOfRepetitionsOfLongestRepeatingSubcircuit": numberOfRepetitionsOfLongestRepeatingSubcircuit,
            "LengthOfCriticalPath": -1,
        }

        writeToFile(thisSubcircuitData)


if __name__ == "__main__":
    with open(OUTPUT_FILE, "w") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=statistics)
        writer.writeheader()

    with Pool(8, initargs = (counter, )) as p:
        p.map(processFile, files)
