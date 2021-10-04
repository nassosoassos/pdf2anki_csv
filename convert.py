from io import StringIO

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
import os
import re
import glob
import csv

def file2txt(filename):
    output_string = StringIO()
    with open(filename, 'rb') as in_file:
        parser = PDFParser(in_file)
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.create_pages(doc):
            interpreter.process_page(page)

    return(output_string.getvalue())


file_dir = "data"
csv_file = "flashcards.csv"
pdf_tests = [ f for f in os.listdir(file_dir) if re.search(r'\d+\.pdf',f)]


with open(csv_file, 'w') as f:
    for ptest in pdf_tests:
        test_text = file2txt(os.path.join(file_dir,ptest))
        test_text = test_text.replace('138.', '138')
        test_text = test_text.replace('90.', '90')
        test_text = test_text.replace(':2.', ':2 .')
        test_text = test_text.replace(':1.', ':1 .')
        s_questions = re.findall("(\d{1,2})\.(.*?)(?=([^\d][\d]{1,2}\.[^\d\n])|($))", test_text, re.DOTALL)
        if len(s_questions)<3:
            s_questions = re.findall("(\d{1,2})\)(.*?)(?=([^\d][\d]{1,2}\)[^\d\.\n])|($))", test_text, re.DOTALL)

        if "6" in ptest:
            for i, qu in enumerate(s_questions):
                print("{} {}\n".format(i, qu))
        answers_text = file2txt(os.path.join(file_dir, ptest.replace('.','a.')))
        s_answers = re.findall("(\d+)\s*=(.*?)(?=([\d]+=)|($))", answers_text, re.DOTALL)
        if len(s_answers)==0:
            s_answers = re.findall("(\d+)\.(.*?)(?=([\d]+\.)|($))", answers_text, re.DOTALL)
        if len(s_answers)==0:
            s_answers = re.findall("(\d+)-(.*?)(?=([\d]+-)|($))", answers_text, re.DOTALL)
        if len(s_answers)==0:
            s_answers = re.findall("(\d+)\)(.*?)(?=([\d]+\))|($))", answers_text, re.DOTALL)
        if len(s_answers)<2:
            s_answers = re.findall("(\d+)([^\)]*?)(?=([\d]+)|($))", answers_text, re.DOTALL)

        print("{} {} {}".format(ptest, len(s_questions), len(s_answers)))
        if "6" in ptest:
            for i, qu in enumerate(s_answers):
                print("{} {}\n".format(i, qu))

        answers_map = {}
        for ans in s_answers:
            answers_map[ans[0]] = ans[1]

        for k, q in enumerate(s_questions):
            if str(k+1) in answers_map:
                f.write("{}\t{}\n".format(q[1].replace("\n","<br>"),answers_map[q[0]].replace("\n", "<br>")))


