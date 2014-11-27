#!/usr/bin/python
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import pdb

# Load data
gen_col=np.load('Gender.npy')
SalaryDisclosure=np.load('SalaryDisclosure.npy')

# Identify males and females
male=gen_col < -.47
male=male.reshape(-1)
female=gen_col > .47
female=female.reshape(-1)

# Get Salary 
sal_col=SalaryDisclosure[:,4].astype(np.float)
ben_col=SalaryDisclosure[:,5].astype(np.float)
total_comp=sal_col+ben_col

# Get index for job titles
JobTitle=SalaryDisclosure[:,3]
# Find all cells that contain the word profesor
profs=np.char.find(JobTitle, 'Professor')>-1

astprof=np.char.find(JobTitle,'Assistant Professor')>-1
assprof=np.char.find(JobTitle,'Associate Professor')>-1
fullprof=profs*np.logical_not(assprof)*np.logical_not(astprof)

#pdb.set_trace()

# Set up data for graphing
# Female
female_m=np.zeros(3)
female_m[0]=np.mean(total_comp[astprof & female])
female_m[1]=np.mean(total_comp[assprof & female])
female_m[2]=np.mean(total_comp[fullprof & female])
female_sem=np.zeros(3)
female_sem[0]=stats.sem(total_comp[astprof & female])
female_sem[1]=stats.sem(total_comp[assprof & female])
female_sem[2]=stats.sem(total_comp[fullprof & female])
# Male
male_m=np.zeros(3)
male_m[0]=np.mean(total_comp[astprof & male])
male_m[1]=np.mean(total_comp[assprof & male])
male_m[2]=np.mean(total_comp[fullprof & male])
male_sem=np.zeros(3)
male_sem[0]=stats.sem(total_comp[astprof & male])
male_sem[1]=stats.sem(total_comp[assprof & male])
male_sem[2]=stats.sem(total_comp[fullprof & male])

#Graph Mean
n_groups=3
fig, ax=plt.subplots()
index=np.arange(n_groups)
bar_width=0.35
plt.ylim(100000,180000)

opacity=0.4
error_config={'ecolor':'0.3'}

rects1=plt.bar(index, female_m, bar_width,
        alpha=opacity, color='r', yerr=female_sem,
        error_kw=error_config,label='Women')

rects2=plt.bar(index+bar_width, male_m, bar_width,
        alpha=opacity, color='b', yerr=male_sem,
        error_kw=error_config, label='Men')

plt.ylabel('Compensation')
plt.title('Pay by Rank and Sex')
plt.xticks(index+bar_width, ('Assistant Professor', 'Associate Professor',
    'Professor'))

#plt.legend()

plt.tight_layout()

# Set up data for graphing
# Female
female_s=np.zeros(3)
female_s[0]=sum(total_comp[astprof & female])
female_s[1]=sum(total_comp[assprof & female])
female_s[2]=sum(total_comp[fullprof & female])
# Male
male_s=np.zeros(3)
male_s[0]=sum(total_comp[astprof & male])
male_s[1]=sum(total_comp[assprof & male])
male_s[2]=sum(total_comp[fullprof & male])

#Graph Mean
n_groups=3
fig, ax=plt.subplots()
index=np.arange(n_groups)
bar_width=0.35

opacity=0.4
error_config={'ecolor':'0.3'}

rects1=plt.bar(index, female_s, bar_width,
        alpha=opacity, color='r',
        error_kw=error_config,label='Women')

rects2=plt.bar(index+bar_width, male_s, bar_width,
        alpha=opacity, color='b',
        error_kw=error_config, label='Men')

plt.ylabel('Compensation')
plt.title('Pay by Rank and Sex')
plt.xticks(index+bar_width, ('Assistant Professor', 'Associate Professor',
    'Professor'))

#plt.legend()

#plt.tight_layout()
plt.show()


# Access Names
# Make new gender criteria abs (.48)
# To get boolean with two criteria
# unknown=((Gender<=.47) & (Gender >=.47))
# Names=SalaryDisclosure[:,2]
# Names=Names.reshape(-1,1)
