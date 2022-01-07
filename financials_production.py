import extract_financials as ef 
import PyPDF2 as pypdf
from bs4 import BeautifulSoup
import pandas as pd 
from datetime import date
import logging

FORMAT = '%(asctime)s:%(levelname)s:%(lineno)d:%(message)s'
logging.basicConfig(level=logging.DEBUG, filename='extract_financials.log',format=FORMAT)

def main(filepath):
    new_year = ef.DataExtration.from_filepath(filepath)
    with open(new_year.get_filepath(),'rb') as open_pdf:
        pdf_file_reader_object=pypdf.PdfFileReader(open_pdf,strict=False)
        pdf_object = ef.PdfSetup(pdf_file_reader_object)
        xfa = ef.findInDict('/XFA',pdf_file_reader_object.resolvedObjects)
        pdf_extraction_type = ef.PdfSetup.pdf_type(xfa)
        if pdf_extraction_type == 'form':
            form_data = pdf_file_reader_object.getFormTextFields()
            financials_year_form = new_year.extractform(form_data)
            financials_data = ef.DataTypeUpdate.update_data(financials_year_form)
        elif pdf_extraction_type == 'both':
            form_data = pdf_file_reader_object.getFormTextFields()
            financials_year_form = new_year.extractform(form_data)

            xml = pdf_object.xfa_extractor(xfa)
            base_soup = BeautifulSoup(xml,'lxml')
            financials_year_xml = new_year.extractxfa(base_soup)

            financials_data = ef.DataTypeUpdate.results_update(financials_year_xml,financials_year_form)
            financials_data = ef.DataTypeUpdate.update_data(financials_data)

        return financials_data


if __name__== "__main__":
    df = pd.read_excel('12_10_files.xlsx')
    list_of_rows = df.iloc[2500:3000].to_dict('records')
    results = []
    today = date.today()

    for row in list_of_rows:
        filepath = row['FILEPATH']
        try:
            financials_data = main(row['FILEPATH'])
            if len(financials_data) > 2:
                row['FINANCIALS_EXTRACTED'] = True
                row['PROCESSED_DATE'] = today
                for key, val in financials_data.items():
                    row[key] = val
            results.append(row)
        except Exception as e:
            logging.debug(f"ERROR: {e}; filepath: {filepath}",exc_info=True)
            row['error'] = e
            results.append(row)
            pass
    pd.DataFrame(results).to_excel('t_Batch1.xlsx', index=False)

