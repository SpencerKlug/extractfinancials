import os
from os.path import join
import re
import pandas as pd 



if __name__== "__main__":
    base = 'C:/Users/spencer.klug/MORNINGSTAR INC/Fight Club - Valuations Filings/India/Filings/$ To Process/Financial Forms'
    final_files = []

    for root, dirs, files in os.walk(base):
        if ('annual returns and balance sheet eforms') in root.lower():
            non_cfs_pdfs = []
            cfs_pdfs = []
            for file in files:
                full_path = os.path.join(root, file).replace("\\","/")
                if re.search('cfs',full_path.lower()):
                    cfs_pdfs.append(full_path)
                else:
                    non_cfs_pdfs.append(full_path)
            if cfs_pdfs == []:
                for pdf in cfs_pdfs:
                    final_files.append(pdf)
            else:
                for pdf in non_cfs_pdfs:
                    final_files.append(pdf)
    print(final_files)
    





