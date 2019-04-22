import json
import re
from pathlib import Path

def clean_lines(src, pattern):
    new_src = []
    for line in src:
        line = re.sub(pattern, "", line)
        new_src.append(line)
    return new_src


if __name__ == "__main__":
    ipynbs = [f for f in Path().glob("*.ipynb")]
    revised_dir = Path('revised')
    for nb_file in ipynbs:
        with open(nb_file, 'r', encoding='utf8') as nb:
            nb = json.load(nb)
        for cell in nb['cells']:
            if cell['cell_type'] == 'code':
                cell['source'] = clean_lines(cell['source'], ">>>.*?")
        with open(revised_dir/nb_file, 'w', encoding='utf8') as new_nb:
            json.dump(nb, new_nb)


