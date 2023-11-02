from pandas import read_csv

def_matchups = {}
off_matchups = {}

for gen in [1, 2, 6]:
    """Reading the source files"""
    def_df = read_csv(f"Type_Matchups/defensive_gen{gen}.txt", delimiter="\t", index_col=0)
    off_df = read_csv(f"Type_Matchups/offensive_gen{gen}.txt", delimiter="\t", index_col=0)

    """Converting strings to lists of strings"""
    for col in def_df.keys():
        for row in def_df.index:
            if def_df[col][row] == "None":
                def_df[col][row] = []
            else:
                def_df[col][row] = def_df[col][row].split(", ")

    for col in off_df.keys():
        for row in off_df.index:
            if off_df[col][row] == "None":
                off_df[col][row] = []
            else:
                off_df[col][row] = off_df[col][row].split(", ")

    """Adding the dataframes to the dictionaries"""
    def_matchups[gen] = def_df
    off_matchups[gen] = off_df

if __name__ == "__main__":
    print(def_matchups)