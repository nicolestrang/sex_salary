#!/usr/bin/python
import requests
from bs4 import BeautifulSoup
import numpy as np

salary=requests.get('http://www.fin.gov.on.ca/en/publications/' +
                    'salarydisclosure/pssd/orgs.php?organization' + 
                    '=universities&year=2013')

# Clean up html
soup=BeautifulSoup(salary.text, 'html5lib')
text=soup.get_text()
# break into lines and remove leading and trailing space on each
lines = (line.strip() for line in text.splitlines())

# Pull out the data from html text
data=[]
gooddata=False
for line in lines:
    if len(line.strip())>0:
        if gooddata or "Taxable Benefits" in line:
            if "Taxable Benefits" in line:
                gooddata=True
            elif  "First" in line and "page" in line:
                gooddata=False
            else:
                data.append(line.strip())
                gooddata=True
data_pg=np.array(data)
try:
    data_array=np.concatenate((data_array, data_pg), axis=0)    
except NameError:
    data_array=np.array(data)

# Delete 2 indices where person had two titles
data_array=np.delete(data_array,23326)
data_array=np.delete(data_array,22348)
data_array=np.reshape(data_array,(-1,6))
nrows=len(data_array)

for r in range(nrows):
    col_idx=[4,5]
    for col in col_idx:
        c=data_array[r,col].strip().lstrip("$")
        c=c.replace(',','')
        float(c)
        data_array[r,col]=c
sal_col=data_array[:,4].astype(np.float)
ben_col=data_array[:,5].astype(np.float)
total_comp=sal_col + ben_col
total_comp=total_comp.reshape(-1,1)

np.save('SalaryDisclosure.npy', data_array)