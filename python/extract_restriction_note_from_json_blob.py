import csv
import json

#Works with CSV output from: https://github.com/duke-libraries/archivesspace-duke-scripts/blob/master/sql/access_restriction_notes_on_aos.sql

input_csv = input('Input CSV: ')
output_csv = input("Output CSV: ")

with open(input_csv,'rt', newline='', encoding='utf-8') as csvfile, open(output_csv,'wt', newline='', encoding='utf-8') as csvout:
    csvin = csv.reader(csvfile)
    next(csvin, None) #ignore header row
    csvout = csv.writer(csvout)

    for i, row in enumerate(csvin):

        note_text = row[9]
        
        note_text = note_text.replace('\n','')
        
        note_json = json.loads(note_text)
        
        #Only works for multi-part notes (used for Restrictions)
        for subnote in note_json['subnotes']:
            content = subnote['content']
        
        print (content)
        
        row.append(content)
        
        with open(output_csv,'at', newline='', encoding='utf-8') as csvout:
                writer = csv.writer(csvout)
                writer.writerow(row)