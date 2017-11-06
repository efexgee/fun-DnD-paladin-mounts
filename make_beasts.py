#!/usr/bin/env python

import json
import re
import pandas as pd
import numpy as np

INFILE="5e-SRD-Monsters.json"
OUTFILE="mounts.xlsx"


def squish_dict(dic):
    if isinstance(dic, dict):
        return ": ".join(map(str,list(dic.values())))
    else:
        return ""

def expand_column(table, col_name):
    col_id = table.columns.get_loc(col_name)

    expanded_column = table[col_name].apply(pd.Series).applymap(squish_dict)
    expanded_column.rename(columns=lambda label: "_".join([col_name, str(label + 1)]), inplace=True)
    
    return pd.concat([table.iloc[:, 0:col_id], expanded_column, table.iloc[:,col_id + 1:]], axis="columns")

with open(INFILE) as f:
    monsters = json.load(f)

# exclude any list entries which are not monsters (don't have a "name" (the license))
# grab only: Large Beasts which are not Evil
mounts = [creature for creature in monsters if 'name' in creature and creature['type'] == "beast" and creature['size'] == "Large" and not re.search("evil", creature['alignment'])]

# drop the columns we filtered on above since they are the same for all entries
mounts_table = pd.DataFrame(mounts).drop(["alignment","type","size"],axis="columns")
# drop any columns which contain only NaN or blanks
mounts_table = mounts_table.replace('',np.nan).dropna(axis="columns",how="all")
# replace any remaining NaNs with blanks
mounts_table.replace(np.nan,'',inplace=True)

# re-order the columns
new_order = ["name", "challenge_rating", "hit_points", "hit_dice", "armor_class", "speed", "strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma", "senses", "perception", "stealth", "special_abilities", "actions", "languages"]
mounts_table = mounts_table[new_order]

# expand the nested columns into multiple columns
mounts_table = expand_column(mounts_table, "actions")
mounts_table = expand_column(mounts_table, "special_abilities")

# replace underscores in column headers
mounts_table.rename(columns=lambda col: col.replace("_", " "), inplace=True)

mounts_table.to_excel(OUTFILE, index=False)
