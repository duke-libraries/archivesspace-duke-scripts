import os, glob
from lxml import etree as ET
import datetime
import csv

#Python 3+

# Script generates an HTML report of new and updated finding aids (and counts) based on dates specified at runtime.
# Script takes as input a .txt file with a list of new EADIDs, the path to published EADs at Duke,the beginning and end dates of reporting period, and a destination path to save the report.
# This probably only makes sense in Duke context

new_eads_list = input('Path to EADID List CSV: ')
current_eads_path = input('Path to published EADs: ')
os.chdir(current_eads_path)

#today's date
today_date = datetime.datetime.today().strftime('%Y-%m-%d')

quarter_start_date = input("Quarter Start Date (YYYY-MM-DD): ")
quarter_end_date = input("Quarter End Date (YYYY-MM-DD): ")

#location to store text file of report
destination = input('Save report to: ')

f = open(destination+'new-ead-report'+today_date+'.html', 'w', encoding="utf-8")

with open(new_eads_list,'rt') as csvfile:
    reader = csv.reader(csvfile)
    new_eadid_list = []
    for row in reader:
        eadid = row[0].strip()
        new_eadid_list.append(eadid)
    print (str(len(new_eadid_list)) + " input EADs in file: " + str(new_eadid_list))


#Initialize some variables
#Create two file lists for new eads and updated eads and running counts
new_files = []
updated_files = []
all_eadid_list = []

#Read over EAD directory and get files modified after specified date.
for file in sorted(glob.glob("*.xml")):
    modified_time = os.path.getmtime(file)
    modified_time_iso = datetime.datetime.fromtimestamp(modified_time).strftime('%Y-%m-%d')
    eadid = file.replace(".xml","")
    all_eadid_list.append(eadid)
    

    if eadid in new_eadid_list:
        new_files.append(file)
        
    if eadid not in new_eadid_list:
        #only get subset of files modified during quarter (as specified at runtime)
        if quarter_start_date <= modified_time_iso <= quarter_end_date:
            updated_files.append(file)
            #print ("Updated EAD: " + eadid + " | " + modified_time_iso)

new_files_count = str(len(new_files))
updated_files_count = str(len(updated_files))

print (new_files_count + " new EADs in directory matching input: " + str(new_files))
print (updated_files_count + " updated EADs in directory: " + str(updated_files))

for item in new_eadid_list:
    if item not in all_eadid_list:
        print("WARNING: EADID/Filename Mismatch for: " + item)
        
#Write a new section for updated EADs
print ("writing new/updated finding aids to HTML file...")

#start writing out HTML file
f.write("<html><head><meta><title>Finding Aid Report</title></meta></head><body><p><a href=\"#new\">{2} New Finding Aids</a> <br> <a href=\"#updated\">{3} Updated Finding Aids</a> </p> <h2><a name=\"new\"></a>New Finding Aids ({0} to {1})</h2>".format(quarter_start_date, quarter_end_date,new_files_count, updated_files_count))

for file in new_files:
    xml_doc = ET.parse(file)
    root = xml_doc.getroot()
    namespace = "{urn:isbn:1-931666-22-9}"
    finding_aid_title = root.find(".//{0}archdesc/{0}did/{0}unittitle".format(namespace)).text
    finding_aid_dates = root.find(".//{0}archdesc/{0}did/{0}unitdate[1]".format(namespace)).text
    extent = root.find(".//{0}archdesc/{0}did/{0}physdesc/{0}extent[1]".format(namespace)).text
    eadid = root.find(".//{0}eadheader/{0}eadid".format(namespace))
    ead_location = eadid.get("url")
    abstract = root.find(".//{0}archdesc/{0}did/{0}abstract".format(namespace)).text
    
    #write a <div> for every new EAD
    f.write("<div><h3><a href=\"{3}\">{0}, {1}</a> ({2})</h3><p>{4}</p><hr></div>".format(finding_aid_title, finding_aid_dates, extent, ead_location, abstract))

#Updated Finding Aid Section Header
f.write("<h2><a name=\"updated\"></a>Updated Finding Aids ({0} to {1})</h2>".format(quarter_start_date, quarter_end_date))

for file in updated_files:
    xml_doc = ET.parse(file)
    root = xml_doc.getroot()
    namespace = "{urn:isbn:1-931666-22-9}"
    finding_aid_title = root.find(".//{0}archdesc/{0}did/{0}unittitle".format(namespace)).text
    finding_aid_dates = root.find(".//{0}archdesc/{0}did/{0}unitdate[1]".format(namespace)).text
    extent = root.find(".//{0}archdesc/{0}did/{0}physdesc/{0}extent[1]".format(namespace)).text
    eadid = root.find(".//{0}eadheader/{0}eadid".format(namespace))
    ead_location = eadid.get("url")
    #abstract = root.find(".//{0}archdesc/{0}did/{0}abstract".format(namespace)).text
    modified_time = os.path.getmtime(file)
    modified_time_iso = datetime.datetime.fromtimestamp(modified_time).strftime('%Y-%m-%d')
       
    #write a <div> for every updated EAD, just include titles, links, and modified dates
    f.write("<div><p><a href=\"{2}\">{0}, {1}</a> (updated: {3})</p></div>".format(finding_aid_title, finding_aid_dates, ead_location, modified_time_iso))

f.write("</body></html>")
f.close
print ("All Done!!")
