import os
from os.path import join, getsize
import re
import pandas as pd 


def cfs_decision(cfs,non_cfs):
    if cfs == []:
        return non_cfs
    else:
        return cfs 

if __name__== "__main__":
    base = 'C:/Users/spencer.klug/MORNINGSTAR INC/Fight Club - Valuations Filings/India/Filings/$ To Process/Financial Forms'
    errors =[]
    final_filings = []

    """
    Searches through filings and if there are consolidated financial statements only returns
    the financial statements with "cfs" included in the document 
    """
    for batch in os.listdir(base):
        pbids = f'C:/Users/spencer.klug/MORNINGSTAR INC/Fight Club - Valuations Filings/India/Filings/$ To Process/Financial Forms/{batch}/'
        for pbid in os.listdir(pbids):
            pbid_folders = f'C:/Users/spencer.klug/MORNINGSTAR INC/Fight Club - Valuations Filings/India/Filings/$ To Process/Financial Forms/{batch}/{pbid}/Annual Returns and Balance Sheet eForms/'
            non_cfs_pdf_files = []
            cfs_pdf_files = []
            try:
                for pdfs in os.listdir(pbid_folders):
                    filing = f'C:/Users/spencer.klug/MORNINGSTAR INC/Fight Club - Valuations Filings/India/Filings/$ To Process/Financial Forms/{batch}/{pbid}/Annual Returns and Balance Sheet eForms/{pdfs}'
                    if re.search('CFS',pdfs):
                        cfs_pdf_files.append(filing)
                    else:
                        non_cfs_pdf_files.append(filing)
            except Exception as e:
                errors.append(e)
            final_filings.append(cfs_decision(cfs_pdf_files,non_cfs_pdf_files))
    print(final_filings)
    #pd.DataFrame(final_filings).to_excel('files.xlsx', index=False)




