# -*- coding: utf-8 -*-
import requests
import urllib.request
import io
import warnings

from lxml import html
from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine

week_number = 0

def parse_vecka():
    answer = requests.get('http://www.vecka.nu')
    root = html.fromstring(answer.text)
    for child in root.xpath('//time'):
        global week_number
        week_number = child.text
    print('Det är nu vecka %s' % week_number)

def parse_kompassen():
    print("### KOMPASSEN ###")
    answer = requests.get('http://www.restaurangkompassen.se/index.php?option=com_content&view=article&id=64&Itemid=66')
    root = html.fromstring(answer.text)
    friday_found = False
    for child in root.xpath('//div[@class="screen"]/div/div/div'):
        if friday_found and child.text:
            print(child.text)
        elif child.text and "fredag" in child.text.lower():
            friday_found = True


def parse_teknikparken():
    print("### TEKNIKPARKEN ###")
    answer = requests.get('http://www.restaurangteknikparken.se/index.php?option=com_content&view=article&id=46')
    root = html.fromstring(answer.text)
    friday_found = False
    for child in root.xpath('//div[@class="screen"]/div/div/div'):
        if friday_found and child.text:
            print(child.text)
        elif child.text and "fredag" in child.text.lower():
            friday_found = True

def parse_gs():
    print("### Gourmetservice ###")
    answer = requests.get('http://www.geflegourmetservice.se/lunch.php')
    root = html.fromstring(answer.text)

    for child in root.xpath('//div[@class="left_holder"]/p')[1:3]:
        print(child.text_content())


def parse_hemlingby():
    print("### HEMLINGBY ###")
    answer = requests.get('http://www.gavle.se/Uppleva--gora/Idrott-motion-och-friluftsliv/Friluftsliv-och-motion/Hemlingby-friluftsomrade/Hemlingbystugan/Fika-och-ata/')
    root = html.fromstring(answer.text)
    for child in root.xpath('//a'):
        if child.text and "meny vecka" in child.text.lower() and week_number in child.text.lower():
            hemlingby_link='http://www.gavle.se' + child.get('href')
            break
    textAsArray = parse_pdf(hemlingby_link)
    fridaysFood = getFoodFromPDFArray(textAsArray)
    print(fridaysFood)
    
#Takes url to pdf file and returns text split on newline into array
def parse_pdf(pdf_url):
    warnings.filterwarnings('ignore', category=Warning, append=True)

    remote_file = urllib.request.urlopen(pdf_url).read()
    memory_file = io.BytesIO(remote_file)
    parser = PDFParser(memory_file)
    doc = PDFDocument()
    parser.set_document(doc)
    #Warning sometimes, error in pdf?
    doc.set_parser(parser)
    doc.initialize('')
    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    warnings.resetwarnings()
    warnings.filterwarnings('always', category=Warning, append=True)

    ret = []
    # Process each page contained in the document.
    for pageIdx, page in enumerate(doc.get_pages()):
        ret.append([])
        interpreter.process_page(page)
        layout = device.get_result()
        for idx, lt_obj in enumerate(layout):
            if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
                if len(lt_obj.get_text().strip()) > 0:
                    ret[pageIdx].append((lt_obj.get_text().splitlines()))
    return ret

def getFoodFromPDFArray(pdfArray):
    correctWeek = False
    ret = ""
    for page in pdfArray:
        for idx, line in enumerate(page):
            #Check if correct week
            if ("vecka " +  week_number + ":") in line[0]:
                correctWeek = True;
                continue;
            #If correct week and day is fredag
            elif correctWeek and "fredag" in line[0].lower():

                #If the line is bigger than 1 it contains the food after 'fredag'
                if len(line) > 1:
                    for x in range(1, len(line)):
                        ret += line[x] + "\n"
                #The line only contained 'fredag' so the food is in the line after 'fredag'
                else:
                    line = page[idx+1]
                    for x in range(0, len(line)):
                        ret += line[x] + "\n"
                return ret

    return "Oops something went wrong"

def parse_gustafsbro():
    print("### Gustafsbro ###")
    answer = requests.get('http://www.gavlelunch.se/gustafsbro.asp')
    root = html.fromstring(answer.text)
    friday_found = False

    #Get friday from table
    for weekdayTable in root.xpath('//body/font/table/tr[1]/td[1]/div/table'):
        for day in weekdayTable.xpath('tr[1]/td[1]/font/strong'):
            if day.text and "fredag" in day.text.lower():
                friday_found = True
                break

    #If friday is found print food
    if friday_found:
           for food in weekdayTable.xpath('tr[2]/td[1]/font/ul/li'):
               print(food.text)
    else:
           print("Oops something went wrong")

def main():
    parse_vecka()
    parse_teknikparken()
    parse_kompassen()
    parse_hemlingby()
    parse_gs()
    parse_gustafsbro()
    
if __name__ == '__main__':
    main()
