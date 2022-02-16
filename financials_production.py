import extract_financials as ef 
import PyPDF2 as pypdf
from bs4 import BeautifulSoup
import pandas as pd 
from datetime import date
import logging

FORMAT = '%(asctime)s:%(levelname)s:%(lineno)d:%(message)s'
logging.basicConfig(level=logging.DEBUG, filename='extract_financials.log',format=FORMAT)

def csv_output(dataframe):
    dataframe = dataframe[dataframe['FINANCIALS_EXTRACTED'] == True]
    df = pd.read_excel('./EntityID.xlsx')
    final_df = pd.merge(dataframe,df,left_on='PBID',right_on='PBID')
    final_df = final_df.drop(columns=['PBID','FILEDATE','PROCESSED_DATE','FINANCIALS_EXTRACTED','FILEPATH','Unnamed: 0'])
    final_df = final_df.rename(columns={'ENTITYID':'id'})
    final_df['ann'] = True
    final_df['qtr'] = False
    final_df['ttm'] = False
    final_df['fiscalQuarter'] = pd.PeriodIndex(final_df['periodEndDate'], freq='Q').quarter
    final_df['fiscalYear'] = pd.PeriodIndex(final_df['periodEndDate'], freq='Q').year
    final_df['currency'] = 32
    final_df['preliminaryType'] = False
    final_df['originalType'] = True
    final_df['periodType'] = '1'
    return final_df


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
            financials_data = ef.CalculatedFields.income_taxes(financials_data)
            financials_data = ef.CalculatedFields.profit_after_tax(financials_data)

        return financials_data


if __name__== "__main__":
    df = pd.read_excel('12_10_files.xlsx')
    list_of_rows = df.iloc[2500:2700].to_dict('records')
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
            
    pd.DataFrame(results).to_excel('t_Batch4.xlsx', index=False)
    excel_output = pd.DataFrame(results)
    csv_output_results = csv_output(excel_output)
    csv_output_results.to_csv('results.csv')