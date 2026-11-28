import wordtree

import os
import glob

def read_xml_files(directory):
    xml_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.xml'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    print("opening: " + filepath)
                    xml_content = f.read()
                    xml_files.append(xml_content)
    return xml_files

directory_path = 'Z:\Proceedings\VisWeek\Vis-all_full_paper_pdfs-text-extraction-results\Vis-2021'
#you have to change the directory to the NAS' path on your computer (see wiki on how to access the NAS)

#directory_path = G:\Meu Drive\ResearchDataResults\0_Submissions\0_2_SystematicReview\Related

xml_contents = read_xml_files(directory_path)


documents = xml_contents
g = wordtree.search_and_draw(corpus = documents, keyword = "experience")
g.render() # creates a file world.dv.png