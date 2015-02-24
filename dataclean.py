#!/usr/bin/python
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import pandas as pd
import pdb
import math

# Load data
gen_col=np.load('Gender.npy')
SalaryDisclosure=np.load('SalaryDisclosure.npy')
df=pd.DataFrame(data=SalaryDisclosure,
                columns=['University','First Name','Last Name','Job Title',
                'Salary','Benefits'])

#convert to correct data types
df['Salary']=df['Salary'].astype('float')
df['Benefits']=df['Benefits'].astype('float')

# Identify males and females (use list comprehension to add to data frame)
df['Sex']=[('male' if x < -.47 else ('female' if x > .47 else 'unknown')) for 
    x in gen_col]

# Create column for total compensation
df['TotalCompensation']=df['Salary'] + df['Benefits']

# Identify individuals who are professors (by level)
df['Rank']=['Assistant Professor' if np.char.find(x,'Assistant Professor') >-1 
    else 'Associate Professor' if np.char.find(x, 'Associate Professor') >-1 
    else 'Professor' if np.char.find(x,'Professor') > -1 else 'Faculty' if 
    np.char.find(x,'Faculty')>-1 else 'Non Faculty' 
    for x in df['Job Title']]
        
# Generate a dataframe with only professors with rank
RankList=['Assistant Professor','Associate Professor', 'Professor']
sexlist=['male','female']
df_f=df[df['Rank'].isin(RankList) & df['Sex'].isin(sexlist)]
df_fc=df_f[['University','Sex','Rank','TotalCompensation']]

# Create a pivot table to figure out number by cell
num_val=pd.pivot_table(df_fc, values='TotalCompensation', 
                       index=['University'],columns=['Rank'], aggfunc='count')
                       
# Create a list of Universities that have at least 20 cases per rank
all_uni=list(num_val.index.values)
all_rank=list(num_val.columns.values)
good_unis=[]
for uni in all_uni:
    for r in all_rank:
        #print num_val.loc[uni,r]
        if num_val.loc[uni,r] < 20 or math.isnan(num_val.loc[uni,r]):
            break
        if r=='Professor':
            good_unis.append(uni)

        
# Select cases in universities with at least 20 cases by rank
df_fc_redux=df_fc[df_fc['University'].isin(good_unis)]

# Save data file to text for statistical analysis
df_fc_redux.to_csv('sexsalary.txt', encoding='utf-8')

#Create pivot table of means and standard deviations for all cases
comp_by_RS= pd.pivot_table(df_fc_redux,values='TotalCompensation', 
                       index=['Sex'],columns=['Rank'])
comp_by_RS_std= pd.pivot_table(df_fc_redux,values='TotalCompensation', 
                       index=['Sex'],columns=['Rank'], 
                        aggfunc=np.std)
comp_by_RS_sem=comp_by_RS_std/np.sqrt(pd.pivot_table(df_fc_redux,values='TotalCompensation', 
                       index=['Sex'],columns=['Rank'], 
                        aggfunc='count'))
                        
#Graph overall mean and standard deviation for all cases
n_groups=3
fig, ax=plt.subplots()
index=np.arange(n_groups)
bar_width=0.35
plt.ylim(100000,220000)

opacity=0.4
error_config={'ecolor':'0.3'}

rects1=plt.bar(index, comp_by_RS.loc["female"], bar_width,
        alpha=opacity, color='r', yerr=comp_by_RS_sem.loc["female"],
       error_kw=error_config,label='Women')

rects2=plt.bar(index+bar_width, comp_by_RS.loc["male"], bar_width,
        alpha=opacity, color='b', yerr=comp_by_RS_sem.loc["male"],
        error_kw=error_config, label='Men')

plt.ylabel('Compensation')
plt.title('Pay by Rank and Sex (All Universities)')
plt.xticks(index+bar_width, ('Assistant Professor', 'Associate Professor',
    'Professor'))
plt.legend()
plt.tight_layout()

# Calculate means and standard error of the mean by university
comp_by_uni= pd.pivot_table(df_fc_redux,values='TotalCompensation', 
                       index=['University', 'Sex'],columns=['Rank'])
print comp_by_uni
comp_by_uni_std= pd.pivot_table(df_fc_redux,values='TotalCompensation', 
                       index=['University','Sex'],columns=['Rank'], 
                        aggfunc=np.std)
print comp_by_uni_std
comp_by_uni_sem=comp_by_uni_std/np.sqrt(pd.pivot_table(df_fc_redux,values='TotalCompensation', 
                       index=['University','Sex'],columns=['Rank'], 
                        aggfunc='count'))
print comp_by_uni_sem


#Graph Means for each university
for uni in good_unis:
    n_groups=3
    fig, ax=plt.subplots()
    index=np.arange(n_groups)
    bar_width=0.35
    plt.ylim(100000,220000)

    opacity=0.4
    error_config={'ecolor':'0.3'}

    rects1=plt.bar(index, comp_by_uni.loc[uni, "female"], bar_width,
                   alpha=opacity, color='r', yerr=comp_by_uni_sem.loc[uni, "female"],
                   error_kw=error_config,label='Women')

    rects2=plt.bar(index+bar_width, comp_by_uni.loc[uni, "male"], bar_width,
                   alpha=opacity, color='b', yerr=comp_by_uni_sem.loc[uni, "male"],
                    error_kw=error_config, label='Men')

    plt.ylabel('Compensation')
    plt.title(uni)
    plt.xticks(index+bar_width, ('Assistant Professor', 'Associate Professor',
    'Professor'))
    plt.legend()
    plt.tight_layout()   