# inspired by https://stackoverflow.com/questions/25598512/how-to-split-a-ipython-notebook
# Seperate the .ipynb according to subsection (##) and add chapter name to seperated files.
from pathlib import Path
import json
from pprint import pprint
import re
import string
import random
from copy import deepcopy

def id_generator(size=12, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
    """Generate random id.
    
    Args:
        size (int, optional): [description]. Defaults to 12.
        chars ([type], optional): [description]. Defaults to string.ascii_uppercase+string.ascii_lowercase+string.digits.
    
    Returns:
        str: an id random generated
    """
    return ''.join(random.choice(chars) for _ in range(size))

def copy_metadata(nb_data):
    """Copy metadata of notebook
    
    Args:
        nb_data (JSON): a json data load from jupyter notebook

    Returns:
        dict: metadate copied from nb_data
    """
    metadata = dict()
    metadata["metadata"] = nb_data["metadata"]
    metadata["nbformat"] = nb_data["nbformat"]
    metadata["nbformat_minor"] = nb_data["nbformat_minor"]
    return metadata

md_cell =   {
   "cell_type": "markdown",
   "metadata": {},
   "source": list()
  }

code_cell =  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": list()
  }

def add_cell(src, cell_temp, cache, sec_id):
    try:
        assert isinstance(cache[sec_id], list)
    except KeyError or AssertionError:
        cache[sec_id] = list() 
    cell = deepcopy(cell_temp)
    cell['source'] = src
    cache[sec_id].append(cell)

def process_nbcells(cells, regx):
    cell_dict = {}
    sec_cnt = 1
    for cell in cells:
        src = cell["source"]
        if cell["cell_type"] == "code":
            add_cell(src, code_cell, cell_dict, sec_cnt)
        else:
            match_line = 0
            for ix, line in enumerate(src, start=0):
                if regx.match(line):
                    add_cell(src[match_line:ix-1], 
                            md_cell, 
                            cell_dict, sec_cnt)
                    sec_cnt += 1
                    match_line = ix
            add_cell(src[match_line:], 
                    md_cell, 
                    cell_dict, sec_cnt)
    return cell_dict
            
if __name__ == "__main__":
    nb_dir = Path('../tmps')
    nb_files = [f for f in nb_dir.glob("Chapter*.ipynb")]
    regx = re.compile("## ")

    for ci, chapter in enumerate(nb_files, start=1):
        # Make chapter directory
        chapter_dir = nb_dir/chapter.stem
        if not chapter_dir.is_dir():
            chapter_dir.mkdir()

        # Load chapter data
        with open(chapter, encoding='utf8') as data_file:    
            nb_data = json.load(data_file)
        chapter_metadata = copy_metadata(nb_data)
        
        # Process cells data
        sec_cells = process_nbcells(nb_data['cells'], regx)

        for si, cell in sec_cells.items():
            print(f"{ci}.{si}", type(cell),len(cell))
            section_content = deepcopy(chapter_metadata)
            section_content["cells"] = cell
            section_fname = f"Section {ci}.{si}.ipynb"
            with open(chapter_dir/section_fname, 'w', encoding='utf8') as sf:
                json.dump(section_content, sf, ensure_ascii=False, indent=4)


        
    