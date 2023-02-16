import os
import xml.etree.ElementTree as ET
import re
import csv
import requests
import json
from collections import defaultdict
from typing import DefaultDict

versions = ["icd10", "icd10cm", "icd10au"]
base = './data/'
anchor_filepath= f'{base}icd10-anchors.csv'

def def_dict_value() -> str:
    return "Not_Found"

def get_anchors(num_chapters: int) -> DefaultDict:
    """fetches the ICD-10 anchors(blocks) from the WHO website"""
    anchors = defaultdict(def_dict_value)

    print('fetching icd10 anchors from WHO website...')
    try:
        root= requests.get('https://icd.who.int/browse10/2019/en/JsonGetRootConcepts?useHtml=false')

        if root.status_code != 200:
            raise HttpRequestError("Unable to fecth the root concepts")

        chapters = root.json()

        for chapter in chapters[0:num_chapters]:
            chapter_id = chapter['ID']
            sec_req = requests.get(f'https://icd.who.int/browse10/2019/en/JsonGetChildrenConcepts?ConceptId={chapter_id}&useHtml=false&showAdoptedChildren=true')

            if sec_req.status_code != 200:
                raise HttpRequestError("Unable to fetch the sections")

            sections = sec_req.json()
            for section in sections:
                section_label = format_label(label=re.sub(',', '', section['label']))
                print(section_label)
                
                section_id = section['ID']
                
                block_req = requests.get(f'https://icd.who.int/browse10/2019/en/JsonGetChildrenConcepts?ConceptId={section_id}&useHtml=false&showAdoptedChildren=true')

                if block_req.status_code != 200:
                    raise HttpRequestError('Unable to fetch the blocks')
                
                blocks = block_req.json()
                for block in blocks:
                    block_label = format_label(label=re.sub(',', '', block['label']))
                    block_id = block['ID']
                    anchors[block_id]=block_label
        return anchors           

    except HttpRequestError as e:
        print(e)

    except json.JSONDecodeError as e:
        print(e)
    
    except ValueError as e:
        print(e)

class HttpRequestError(Exception):
    """This exception is raised when the get request fails"""


def format_label(label: str, pos: str = 'first') -> str:
    """
    Removes the code from the label

    the label will be either like 'xxx ******' or '****** xxx'.
    This will removes 'xxx' from the label

    returns: str
    """
    new_label = ''
    new_label = label.split()
    if pos == 'first':
        new_label.pop(0)
    else:
        new_label.pop()
    
    new_label = ' '.join(new_label)
    return new_label


def write_list_to_file(filename: str, codes: list) -> None:
    """Writes data to a file"""
    if type(codes) != list:
        raise ValueError(f'The second argument is expected to be a list but got {type(codes)}')

    print('Saving data to the file')
    with open (filename, 'w') as file:
        write = csv.writer(file)
        write.writerows(codes)
    print('Completed!')
    print('====================================')

def write_dict_to_file(filename: str, dict: DefaultDict) -> None:
    if type(dict) != defaultdict:
        raise ValueError(f'The second argument is expected to be a dictionary but got {type(dict)}')
    print('Saving dict to the file')
    with open(filename, "w") as file:
        write = csv.writer(file)
        write.writerows(dict.items())


def get_icd10_codes(filename: str, num_chapters: int = 1) -> None:
    """
    Fetchs icd10 data from the WHO website and saves to a file.

    args:
        filename: str
        num_chapters: int, default is 1
    
    """

    code_list = []

    print('fetching icd10 data from WHO website...')
    try:
        root= requests.get('https://icd.who.int/browse10/2019/en/JsonGetRootConcepts?useHtml=false')

        if root.status_code != 200:
            raise HttpRequestError("Unable to fecth the root concepts")

        chapters = root.json()

        for chapter in chapters[0:num_chapters]:
            chapter_id = chapter['ID']
            sec_req = requests.get(f'https://icd.who.int/browse10/2019/en/JsonGetChildrenConcepts?ConceptId={chapter_id}&useHtml=false&showAdoptedChildren=true')

            if sec_req.status_code != 200:
                raise HttpRequestError("Unable to fetch the sections")

            sections = sec_req.json()
            for section in sections:
                section_label = format_label(label=re.sub(',', '', section['label']))
                print(section_label)
                
                section_id = section['ID']
                
                block_req = requests.get(f'https://icd.who.int/browse10/2019/en/JsonGetChildrenConcepts?ConceptId={section_id}&useHtml=false&showAdoptedChildren=true')

                if block_req.status_code != 200:
                    raise HttpRequestError('Unable to fetch the blocks')
                
                blocks = block_req.json()
                for block in blocks:
                    block_label = format_label(label=re.sub(',', '', block['label']))
                    block_id = block['ID']

                    code_req = requests.get(f'https://icd.who.int/browse10/2019/en/JsonGetChildrenConcepts?ConceptId={block_id}&useHtml=false&showAdoptedChildren=true')

                    if code_req.status_code != 200:
                        raise HttpRequestError('Unable to fetch the codes')

                    codes = code_req.json()
                    if len(codes) == 0:
                        code_list.append([block_id, block_label, '', block_label, section_label])
                        continue

                    for code in codes:
                        code_id = re.sub(r'[.]', '', code['ID'])
                        code_label = format_label(label=re.sub(',', '', code['label']))

                        code_list.append([code_id, code_label, '', block_label, section_label])
        
        write_list_to_file(filename, code_list)

    except HttpRequestError as e:
        print(e)

    except json.JSONDecodeError as e:
        print(e)
    
    except ValueError as e:
        print(e)


def icd10cm_to_csv(filename: str, num_chapters: int = 1) -> None:
    """
    Generates icd10cm csv file from the xml file

    args:
        filename: str,
        num_chapters: int, (default is 1),

    <root>  ----------------------------- document root
        <chapter> ----------------------- chapter
            <section> ------------------- section
                <diag> ------------------ block             <--- xxx
                    <diag> -------------- code              <--- xxxx
                        <diag> ---------- sub-code          <--- xxxxx
                            <diag> ------ sub-sub-code      <--- xxxxxx (not considered)

    """
    anchors = defaultdict()
    if not os.path.exists(anchor_filepath):
        raise FileNotFoundError(f'Couldn\'t find {anchor_filepath}.')

    with open(anchor_filepath, 'r') as file:
        for line in csv.reader(file):
            key, value = line
            anchors[key]=value

    doc = ET.parse(f'{base}icd10cm-tabular-2022.xml')
    chapters = doc.getroot().findall('chapter')
    code_list = []
    
    print('processing icd10cm xml file')
    for chapter in chapters[0:num_chapters]:
        """chapter"""
        sections = chapter.findall('section')

        for section in sections:
            """chapter > section"""
            section_text = format_label(label=re.sub(',', '', section.find('desc').text), pos='last')
            blocks = section.findall('diag')

            for block in blocks:
                """chapter > section > block"""
                block_code = block.find('name').text
                block_text = anchors.get(block_code)
                diags = block.findall('diag')

                if len(diags) == 0:
                    """
                    in case if the block itself is the code. 
                    e.g., (A33, Tetanus neonatorum), (B03, Smallpox)
                    """
                    code_list.append([block_code, block_text, '', block_text, section_text])
                    continue

                for diag in diags:
                    """chapter > section > block > code"""
                    diag_code = re.sub(r'[.]', '', diag.find('name').text)
                    diag_text = re.sub(',', '', diag.find('desc').text)

                    sub_diags = diag.findall('diag')
                    if len(sub_diags) > 0:
                        for sub_diag in sub_diags:
                            """chapter > section > block > code > sub-code"""
                            sub_diag_code = re.sub(r'[.]', '', sub_diag.find('name').text)
                            sub_diag_text = re.sub(',', '', sub_diag.find('desc').text)
                            code_list.append([sub_diag_code, sub_diag_text, diag_text, block_text, section_text])
                        # lets add the diag itself as another entry to our code list
                        # uncomment the continue statement below if don't want to include
                        # continue
                    code_list.append([diag_code, diag_text,'', block_text, section_text])
    try:
        write_list_to_file(filename, code_list)
    except ValueError as e:
        print(e)
    
    except FileNotFoundError as e:
        print(e)


if __name__ == "__main__":
    num_chapters = 1
    anchor = defaultdict()

    ## this must be called first before the rest
    if not os.path.exists(anchor_filepath):
        anchors = get_anchors(num_chapters)
        write_dict_to_file(anchor_filepath, anchors)
    
    if not os.path.exists(f'{base}{versions[0]}.csv'):
        get_icd10_codes(filename=f'{base}{versions[0]}.csv', num_chapters=num_chapters)
    
    if not os.path.exists(f'./data/{versions[1]}.csv'):
        icd10cm_to_csv(filename=f'{base}{versions[1]}.csv', num_chapters=num_chapters)