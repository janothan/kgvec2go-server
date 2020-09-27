
file_name = "./en_dbnary_ontolex.nt"
key_word = "cheetah"
with open(file_name) as file:
    for line in file.readlines():
        if key_word in line:
            print(line)