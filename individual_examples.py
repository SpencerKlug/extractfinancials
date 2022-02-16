import extract_financials as ef 
import PyPDF2 as pypdf
from bs4 import BeautifulSoup
import pandas as pd 

#from extract_financials_.extract_financials import DataExtration 
data = {}


n_3 = 'C:/Users/spencer.klug/MORNINGSTAR INC/Fight Club - Valuations Filings/India/Filings/$ To Process/Financial Forms/Batch 1/184622-23/Annual Returns and Balance Sheet eForms/Form AOC-4(XBRL)-05102018_signed%05-10-2018.pdf'
pi = 'C:/Users/spencer.klug/MORNINGSTAR INC/Fight Club - Valuations Filings/India/Filings/$ To Process/Financial Forms/Batch 1/161456-32/Annual Returns and Balance Sheet eForms/Form 23AC-121007%12-10-2007.pdf'
n_4 = 'C:/Users/spencer.klug/MORNINGSTAR INC/Fight Club - Valuations Filings/India/Filings/$ To Process/Financial Forms/Batch 5/129225-97/Annual Returns and Balance Sheet eForms/Form23AC-310114 for the FY ending on-310312%31-01-2014.pdf'
get_forms = 'C:/Users/spencer.klug/MORNINGSTAR INC/Fight Club - Valuations Filings/India/Filings/$ To Process/Financial Forms/Batch 1/161457-31/Annual Returns and Balance Sheet eForms/Form 23AC-191108%18-11-2008.pdf'
b = 'C:/Users/spencer.klug/MORNINGSTAR INC/Fight Club - Valuations Filings/India/Filings/$ To Process/Financial Forms/Batch 1/183208-60/Annual Returns and Balance Sheet eForms/Form 23ACA-080908-Revised-1%07-09-2008.pdf'
t = 'C:/Users/spencer.klug/MORNINGSTAR INC/Fight Club - Valuations Filings/India/Filings/$ To Process/Financial Forms/Batch 1/221962-42/Annual Returns and Balance Sheet eForms/Frm23ACA-241110 for the FY ending on-310310%30-11-2010.pdf'
ten = 'C:/Users/spencer.klug/MORNINGSTAR INC/Fight Club - Valuations Filings/India/Filings/$ To Process/Financial Forms/Batch 1/183208-60/Annual Returns and Balance Sheet eForms/Form23AC-081010 for the FY ending on-310310%10-10-2010.pdf'
six_eight = 'C:/Users/spencer.klug/MORNINGSTAR INC/Fight Club - Valuations Filings/India/Filings/$ To Process/Financial Forms/Batch 1/184620-16/Annual Returns and Balance Sheet eForms/Frm23ACA-121011 for the FY ending on-310310%13-10-2011.pdf'
a = 'C:/Users/spencer.klug/MORNINGSTAR INC/Fight Club - Valuations Filings/India/Filings/$ To Process/Financial Forms/Batch 1/222298-39/Annual Returns and Balance Sheet eForms/Form 23ACA XBRL-191213-181213 for the FY ending on-310313%18-12-2013.pdf'
aoc4 = 'C:/Users/spencer.klug/MORNINGSTAR INC/Fight Club - Valuations Filings/India/Filings/$ To Process/Financial Forms/Batch 5/60912-37/Annual Returns and Balance Sheet eForms/Form AOC-4-051115%05-11-2015.pdf'
full = 'C:/Users/spencer.klug/MORNINGSTAR INC/Fight Club - Valuations Filings/India/Filings/$ To Process/Financial Forms/Batch 1/183695-05/Annual Returns and Balance Sheet eForms/Form AOC-4-010116%01-01-2016.pdf'
test = 'C:/Users/spencer.klug/MORNINGSTAR INC/Fight Club - Valuations Filings/India/Filings/$ To Process/Financial Forms/Batch 1/183208-60/Annual Returns and Balance Sheet eForms/Frm23ACA-101009 for the FY ending on-310309%13-10-2009.pdf'

df = pd.read_excel('./EntityID.xlsx')
dt = df.to_dict('records')

new_year = ef.DataExtration.from_filepath(test)
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
        
    print(financials_data)

