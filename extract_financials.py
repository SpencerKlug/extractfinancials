import re
from datetime import datetime
import logging

# Dictionary containing the searchable values if using the xml/beautifulsoup form of extraction
HUMAN_EXTRACTION_XFA = {
    'periodEndDate':['to_date_cr','frm:curreportingdate','frcurreportingdatem:','frm:currfiyrtill','frm:currfiyrdateto','fy_end_date'],
    'totalRevenue':['total_revenue_cr','frm:curtotalrev'],
    'costOfRevenue':['cost_material_cr','frm:curmaterialcost'],
    'depreciationAmortizationExpense':['deprectn_amort_c','deprectn_amort_c','frm:curdepamortexpense','frm:curdeprecatn'],
    'interestExpense':['finance_cost_cr','frm:curfinancecost'],
    'otherOperatingExpenses':['other_expenses_c'],
    'totalOperatingExpenses':['total_expenses_c','frm:curtotalexpenses'],
    'incomeBeforeTaxes':['profit_bef_tax_c','frm:curprofitbfrtax'],
    #'incomeTaxes':['current_tax_cr','frm:curcurrenttax'], #Created a tax calculation since this isn't always avaiable 
    #'DEFERRED_TAX':['deferred_tax_cr','frm:curdeferredtax'], #Need to create a tax function
    'netIncome':['prof_loss_oper_c','frm:curprofitorlossfrmco','frm:curprofit_loss','prof_los_12_15_c'], #Net Income and Income After Tax
    'retainedEarnings':['reserve_surplus1','frm:currsrvandsurplus','frm:curreservsurplus'],
    'commonStock':['share_capital_cr','frm:cursharecptl','frm:curpaidupcaptl','frm:curshrarecptl'],
    'longTermDebt':['long_term_borr_c','frm:curlngtermborrow'],
    #'DEFERRED_TAX_LIABILITIES_NET':['deferred_tl_cr','frm:curdefrdtaxliabilities','frm:curdeftaxliab'], #DELETE
    'otherLiabilities':['other_lng_trm_cr','frm:curothrlngtrmborrow'],
    #'LONG_TERM_PROVISIONS':['long_term_prov_c','frm:curlngtermprovisions'], #DELETE
    'shortTermBorrowings':['short_term_bor_c','frm:curshorttermborrow'],
    'accountsPayable':['trade_payables_c','frm:curtradepayables'],
    'otherCurrentLiabilities':['other_curr_lia_c','frm:curothrcrntliabilities'],
    #'SHORT_TERM_PROVISIONS':['short_term_pro_c','frm:curshorttermprovisions'], #DELETE
    'propertyPlantEquipmentNet':['tangible_asset_c','frm:curtangibleassets'],
    'intangibleAssets':['intangible_ast_c','frm:curintangibleassets'],
    #'CAPITAL_WORK_IN_PROGRESS':['capital_wip_cr','frm:curcapitalwip'],
    #'INTANGIBLE_ASSETS_UNDER_DEVELOPMENT':['intangible_aud_c','frm:curintangibleasstsindev'],#DELETE
    'longTermInvestments':['non_curr_inv_cr','frm:curnoncrntinvstmnt'],
    'deferredIncomeTaxesCurrent':['deferred_ta_cr','frm:curdeftaxassetsnet'],
    #'LONG_TERM_LOANS_ADVANCES':['lt_loans_adv_cr','frm:curlongtermloans'],
    'otherCurrentAssets':['other_non_ca_cr','frm:curothrnoncrntassets'],
    'shortTermInvestments':['current_inv_cr','frm:curinvestment'],
    'inventoriesNet':['inventories_cr','frm:curinventories','frm:curinventries'],
    'totalReceivablesNet':['trade_receiv_cr','frm:curtradereceivables','frm:cursundrydebtrs'],
    'cashAndCashEquivalents':['cash_and_equ_cr','frm:curcastandeqvlnts','frm:curcshbnkbalnce'],
    'LOANS_AND_ADVANCES':['short_trm_loa_cr','frm:curshrttermloans'],
    'otherCurrentAssets':['other_curr_ca_cr','frm:curothrcrntassets','frm:curothrassts'],
    'totalAssets':['total_curr_rep','frm:curassetstotal']
              }

# Dictionary containing the searchable values if using the method .getFormTextFields()
HUMAN_GET_FORM_TEXT_FIELDS_DICTIONARY = {
    'periodEndDate':['EndCurrDate_D[0]','DateOfFinancialYrTo_D[0]','BalanceShtFromDate[0]','ToDate[0]','HiddenBalsheetDate_D[0]','HiddenBalDate_D[0]'],
    'totalRevenue':['CurTotalRev[0]','TotalCurrIncom_N[0]'],
    'costOfRevenue':['CurMaterialCost[0]'],
    'depreciationAmortizationExpense':['DepreAmorCurr_N[0]','DeprAmorCurr_N[0]','CurDepAmortExpense[0]'],
    'interestExpense':['InterestCurr_N[0]','CurFinanceCost[0]'],
    'otherOperatingExpenses':['CurOthrExpenses[0]','CurTotalExpenses[0]'],
    'totalOperatingExpenses':['TotalExpCurr_N[0]'],
    'incomeBeforeTaxes':['TotalCurrIncome_N[0]','CurProfitBfrTax[0]'],
    #'incomeTaxes':['IncomeTDefTCurr_N[0]'], #Need to create a tax function
    #'DEFERRED_TAX':[], #Need to create a tax function
    'netIncome':['CurProfit_Loss[0]'], #Net Income and Income After Tax
    'retainedEarnings':['ReservesSurpCur_N[0]','CurRsrvAndSurplus[0]','ResSur[0]'],
    'commonStock':['ShareCap[0]','TotPaidCap[0]','Total1Curr_N[0]'],
    'longTermDebt':['LongTerm[0]','CurLngTermBorrow[0]'],
    #'DEFERRED_TAX_LIABILITIES_NET':['DefLiabl[0]','CurDefrdTaxLiabilities[0]'], #DELETE
    'otherLiabilities':['LongLiabl[0]','CurOthrLngTrmBorrow[0]'],
    #'LONG_TERM_PROVISIONS':['CurLngTermProvisions[0]','LongProv[0]'], #DELETE
    'shortTermBorrowings':['ShortBorrow[0]','CurShortTermBorrow[0]'],
    'accountsPayable':['CurTradePayables[0]','Trade[0]'],
    'otherCurrentLiabilities':['CurrentLiabl[0]','CurOthrCrntLiabilities[0]'], 
    #'SHORT_TERM_PROVISIONS':['ShortProv[0]','CurShortTermProvisions[0]'], #DELETE
    'propertyPlantEquipmentNet':['TangAsset[0]','CurTangibleAssets[0]'],
    'intangibleAssets':['IntangAsset[0]','CurIntangibleAssets[0]'],
    #'CAPITAL_WORK_IN_PROGRESS':['CapWIPCurr_N[0]','CapWork[0]','CurCapitalWIP[0]'],
    'INTANGIBLE_ASSETS_UNDER_DEVELOPMENT':[], #DELETE
    'longTermInvestments':['NonCurrent[0]','CurNonCrntInvstmnt[0]','InvestmentCurr_N[0]'],
    'deferredIncomeTaxesCurrent':['DeffTaxAsstCurr_N[0]','DefTax[0]','CurDefTaxAssetsNet[0]'],
    #'LONG_TERM_LOANS_ADVANCES':['LoansAdvCurr_N[0]','LongLoan[0]','CurLongTermLoans[0]'], #DELETE
    'otherCurrentAssets':['CurOthrNonCrntAssets[0]','OtherAsset[0]','OthersCurr_N[0]'],
    'shortTermInvestments':[],
    'inventoriesNet':['CurInventories[0]','Inventory[0]','InventoriesCurr_N[0]'],
    'totalReceivablesNet':['ShortLoan[0]','CurTradeReceivables[0]'],
    'cashAndCashEquivalents':['CashBankBalCurr_N[0]','CurCastAndEqvlnts[0]','Cash[0]'],
    #'LOANS_AND_ADVANCES':['ShortLoan[0]','CurShrtTermLoans[0]'],
    'otherCurrentAssets':['OtherAsset[0]','CurOthrCrntAssets[0]'],
    'totalAssets':['CurAssetsTotal[0]','TotalCurr_N[0]']}

#Blank dictionaries one for XFA and one for Forms
XFA_ = {}
GET_FORM_TEXT_FIELDS_DICTIONARY = {}

#Putting the human readable dictionary into XFA_
for key, value in HUMAN_EXTRACTION_XFA.items():
    for v in value:
        XFA_[v] = key

#Putting the human readable dictionary into GET_FORM_TEXT_FIELDS_DICTIONARY
for key, value in HUMAN_GET_FORM_TEXT_FIELDS_DICTIONARY.items():
    for v in value:
        GET_FORM_TEXT_FIELDS_DICTIONARY[v] = key

# Creates an object from inputting thefilepath 
class FinancialYear:
    def __init__(self,pbid,year,file_path):
        self.__pbid = pbid
        self.__year = year
        self.__filepath = file_path
    
    def set_pbid(self, pbid):
        self.__pbid = pbid

    def set_year(self,year):
        self.__year = year

    def get_year(self):
        return self.__year

    def get_pbid(self):
        return self.__pbid
    
    def get_filepath(self):
        return self.__filepath
  
    @classmethod
    def from_filepath(cls,file_path: str):
        pbid = re.findall(r'[0-9][0-9][0-9]+\-[0-9][0-9]',file_path)[0]
        year = re.findall(r'[0-9][0-9]\-[0-9][0-9]\-[0-9][0-9][0-9][0-9]',file_path)[0]
        year = datetime.strptime(year, '%d-%m-%Y')
        return cls(pbid,year,file_path)

# Used to define the PDF and ensure the same format   
class PdfSetup:
    def __init__(self,pdf_reader):
        self.__pdf = pdf_reader 

    """
    For some filings the xml data is not available. If the data is not avialable then we only want to use form method  
    Using the xml/beautifulsoup method is much more accurate and comprehensive   
    """

    def pdf_type(xfa_data):
        if xfa_data:
            document_type = 'both'
        else:
            document_type = 'form'
        return document_type  
    
    # Function returns the proper version of XML data. Data is only contained in 7 or 11, comparing amount of data in each response to return the best result
    def xfa_extractor(self,xfa_base):
        seven = xfa_base[7].getObject().getData()
        eleven =  xfa_base[11].getObject().getData()
        if len(seven) > len(eleven):
            return seven
        else:
            return eleven

# Class is used to extract financials either in xfa or .getFormTextFields style 
# The format of data (xfa vs. .getFormTextFields) depends on how old the document is  
class DataExtration(FinancialYear):
    # A large portion of the documets contain data in xml format where it is needed to grab data using beautifulsoup 
    # Taking the beautifulsoup data and iterating through possible bs4 search names & adding non-null values into a dictionary   
    def extractxfa(self,soup):
        financial_year = {}
        for key, value in XFA_.items():
            for soup_value in soup.findAll(key):
                if soup_value.text != '':
                    financial_year[value] = soup_value.text
        return financial_year

    # Some entities data is only able to be extracted through pypdf's .getFormTextFields 
    # the key is an item we are looking for/matches EX_GETTEXT dictionary and the value we receive is not == None
    def extractform(self,form_dictionary):
        financial_year = {}
        for key, value in form_dictionary.items():
            if key in GET_FORM_TEXT_FIELDS_DICTIONARY.keys() and not re.search('None',str(value)):
                financial_year[GET_FORM_TEXT_FIELDS_DICTIONARY[key]] = value
        return financial_year

# Calculating 
class CalculatedFields:

    def income_taxes(financial_dictionary):
        if (financial_dictionary.keys() >= {'netIncome','incomeBeforeTaxes'}) == True:
            financial_dictionary['incomeTaxes'] = (financial_dictionary['incomeBeforeTaxes'] - financial_dictionary['netIncome'])
            return financial_dictionary
        else:
            return financial_dictionary

    def profit_after_tax(financial_dictionary):
        if ('netIncome') in financial_dictionary.keys():
            financial_dictionary['incomeAfterTaxes'] = financial_dictionary['netIncome']
            return financial_dictionary
        else:
            return financial_dictionary

# Updates a variable data type   
class DataType: 
    #Turn all financial figures into int data type 
    def non_year(non_year):
        #some values come with commas 
        int_ = str(non_year)
        int_ = int(float(int_.replace(',','')))
        value = int(float(int_))
        value = (value/1000)
        return value
    
    #Turn date into datetime
    def year(dictionary_year):
        if '-' in dictionary_year:
            #searching for the financial format YYYY-MM-DD since some pdf's include seconds 
            year = re.findall('[0-9]*\-[0-9][0-9]\-[0-9][0-9]',dictionary_year)[0]
            value = datetime.strptime(year, '%Y-%m-%d')
        elif re.search('/',dictionary_year):
            sp = dictionary_year.split('/')
            if sp[0] > sp[1]:
                value = datetime.strptime(dictionary_year, '%d/%m/%Y')
            elif sp[0] < sp[1]:
                value = datetime.strptime(dictionary_year, '%m/%d/%Y')
            elif sp[0] == sp[1]:
                value = datetime.strptime(dictionary_year, '%m/%d/%Y')
        return value

# Updates an entire dictionary values into the correct data type using methods from the DataType class 
# update_data only returns non-0 values since we do not want 0's showing in the platform
class DataTypeUpdate:
    
    def update_data(financial_dictionary):
        if financial_dictionary == None:
            updated_financial_dictionary = {}
            return updated_financial_dictionary
        updated_financial_dictionary = {}   
        for item in financial_dictionary.items():
            if item[0] == 'periodEndDate':
                dict_value = DataType.year(item[1])
                updated_financial_dictionary[item[0]] = dict_value
            else:
                dict_value = DataType.non_year(item[1])
                if dict_value != 0:
                    updated_financial_dictionary[item[0]] = dict_value
        return updated_financial_dictionary
    
    def results_update(financials_year_xml,financials_year_form):
        if len(financials_year_xml) > len(financials_year_form):
            return financials_year_xml
        elif len(financials_year_form) > len(financials_year_xml):
            return financials_year_form

# Search through underlying data for /XFA items
def findInDict(needle, haystack):
    for key in haystack.keys():
        try:
            value=haystack[key]
        except:
            continue
        if key==needle:
            return value
        if isinstance(value,dict):            
            x=findInDict(needle,value)            
            if x is not None:
                return x







