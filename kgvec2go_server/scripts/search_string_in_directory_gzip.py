import gzip
import os

from pathlib import Path

# directory_in_str = '/work/jportisc/babelnet_rdf/'
directory_in_str = (
    "/work/jportisc/models/iteration_2/babelnet/mc1/sg200_babelnet_100_8_df_en_mc1"
)

for filename in os.listdir(directory_in_str):
    with gzip.open(directory_in_str + filename, "rt", encoding="utf-8") as file:
        with open("./temporary.txt", "w", encoding="utf-8") as file_to_write:
            print("Processing file: " + filename)
            for line in file:
                if "bn:cat_n_EN" in line:
                    print("FOUND")
                    file_to_write.write(line + "\n")
                    file_to_write.write(filename + "\n")
                    file_to_write.write(line + " " + filename + "\n")
                if "bn:Cat_n_EN" in line:
                    # if "http://babelnet.org/rdf/cat_n_EN" in line:
                    file_to_write.write(line + "\n")
                    file_to_write.write(filename + "\n")
                    file_to_write.write(line + " " + filename + "\n")
