#!/usr/bin/python
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import math
import os
import scipy
from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm
import unicodedata
from hammock import Hammock as GenderAPI
from tempfile import TemporaryFile
outfile=TemporaryFile()

# Load data
#gen_col=np.load('Gender.npy')
SalaryDisclosure=np.load('SalaryDisclosure.npy')
df=pd.DataFrame(data=SalaryDisclosure,
                columns=['University','Last Name','First Name','Job Title',
                'Salary','Benefits'])

#convert to correct data types
df['Salary']=df['Salary'].astype('float')
df['Benefits']=df['Benefits'].astype('float')

# Create column for total compensation
df['TotalCompensation']=df['Salary'] + df['Benefits']

# Identify individuals who are professors (by level)
df['Rank']=['Assistant Professor' if np.char.find(x,'Assistant Professor') >-1 
    else 'Associate Professor' if np.char.find(x, 'Associate Professor') >-1 
    else 'Professor' if np.char.find(x,'Professor') > -1 else 'Faculty' if 
    np.char.find(x,'Faculty')>-1 else 'Non Faculty' 
    for x in df['Job Title']]

# Generate a dataframe that only contain professors with rank
RankList=['Assistant Professor','Associate Professor', 'Professor']
# sexlist=['male','female']
df_f=df[df['Rank'].isin(RankList)]
# df_fc=df_f[['University','Rank','TotalCompensation']]

# Create a pivot table to figure out number by university and rank
num_rank=pd.pivot_table(df_f, values='TotalCompensation', 
               index=['University'],columns=['Rank'], aggfunc='count')
                       
# Create a list of Universities that have at least 30 cases per rank
all_uni=list(num_rank.index.values)
all_rank=list(num_rank.columns.values)
good_unis=[]
for uni in all_uni:
    for r in all_rank:
        #print num_val.loc[uni,r]
        if num_rank.loc[uni,r] < 30 or math.isnan(num_rank.loc[uni,r]):
            break
        if r=='Professor':
            good_unis.append(uni)

# Select cases in universities with at least 20 cases by rank
df_redux=df_f[df_f['University'].isin(good_unis)]
df_redux['SexVal']=0
nrows=len(df_redux)
gen_col=np.zeros((nrows, 1), dtype='float')
# Get Names to Gender
outfile=TemporaryFile()
r=0
for index, row in df_redux.iterrows():
#for r in range(nrows):
    print nrows-r
    firstname=unicodedata.normalize('NFKD', row['First Name']).encode('ascii','ignore')
    surname=unicodedata.normalize('NFKD', row['Last Name']).encode('ascii','ignore')  
    gendre=GenderAPI("http://api.namsor.com/onomastics/api/json/gendre/" + firstname +'/' +  surname)
    resp=gendre.GET()
    sex=(resp.json().get('scale'))
    gen_col[r]=sex    
    r=r+1
#np.save('Gender.npy', gen_col)
outfile.seek(0)

# Identify males and females (use list comprehension to add to data frame)
df_redux['Sex']=[('male' if x < -.47 else ('female' if x > .47 else 'unknown')) for 
    x in gen_col]

sexlist=['male','female']
df_mf=df_redux[df_redux['Sex'].isin(sexlist)]

# Create pivot table with count of men and women by University and Rank
num_by_RS=pd.pivot_table(df_mf,values='TotalCompensation',
                         index=['Sex'],columns=['Rank'],
                         aggfunc='count')
num_by_uni=pd.pivot_table(df_mf, values='TotalCompensation', 
                       index=['University','Sex'],columns=['Rank'], 
                       aggfunc='count')

# Save data file to text for statistical analysis
#df_fc_redux.to_csv('sexsalary.txt', encoding='utf-8')
np.save('sexsalary.npy', df_mf)

#Create pivot table of means and standard deviations for all cases
comp_by_RS= pd.pivot_table(df_mf,values='TotalCompensation', 
                       index=['Sex'],columns=['Rank'])
comp_by_RS_std= pd.pivot_table(df_mf,values='TotalCompensation', 
                       index=['Sex'],columns=['Rank'], 
                        aggfunc=np.std)
comp_by_RS_sem=comp_by_RS_std/np.sqrt(pd.pivot_table(df_mf,values='TotalCompensation', 
                       index=['Sex'],columns=['Rank'], 
                        aggfunc='count'))
                        
# Create out directory for graphs
if not os.path.exists('Graphs'):
    os.makedirs('Graphs')                        
                       
# Make pie charts of percentage of men and women
# Pie chart of all men and women faculty on list
def plotPieGraph(Title):
    labels='Male','Female'
    sizes=[p_male,p_female]
    colors=['blue','red']
    explode=(0,0.1)
    fig=plt.pie(sizes,explode=explode,labels=labels, colors=colors,autopct='%1.1f%%',
        shadow=True, startangle=90)
    fig=plt.axis('equal')
    fig=plt.title(Title)
    return fig


p_female=(np.float(sum(num_by_RS.loc['female']))/(sum(num_by_RS.loc['female'])+
    sum(num_by_RS.loc['male'])))*100
p_male=100-p_female
plotPieGraph('All Faculty')
plt.savefig('Graphs/AllFaculty_pFem.png')
plt.close()

# Pie chart for all men and women faculty by rank
for rank in all_rank:
    p_female=(np.float(num_by_RS.loc['female', rank])/
            (num_by_RS.loc['female',rank]+
            num_by_RS.loc['male', rank]))*100
    p_male=100-p_female
    plotPieGraph(rank)
    plt.savefig('Graphs/' + rank + '.png')
    plt.close()

for uni in good_unis:
    p_female=(np.float(sum(num_by_uni.loc[uni,'female']))/
            (sum(num_by_uni.loc[uni,'female'])+
            sum(num_by_uni.loc[uni,'male'])))*100
    p_male=100-p_female
    plotPieGraph(uni)
    if 'Ottawa' in uni:
        plt.savefig('Graphs/University of Ottawa_pfem.png')    
    else:
        plt.savefig('Graphs/' + uni + '_pfem.png')
    plt.close()

    for rank in all_rank:
        p_female=(np.float(num_by_uni[rank].loc[uni,'female'])/
                (num_by_uni[rank].loc[uni, 'female']+
                num_by_uni[rank].loc[uni, 'male']))*100
        p_male=100-p_female
        plotPieGraph(uni + ' ' + rank)
        if 'Ottawa' in uni:
            plt.savefig('Graphs/University of Ottawa_' + rank + '_pfem.png') 
        else:
            plt.savefig('Graphs/' + uni + '_' + rank + '_pfem.png')
        plt.close()

#Graph overall mean compensations and standard error of the mean for all cases
def plotSalary_by_RankSex(Title, avg_comp, sem_comp):
    n_groups=3
    fig, ax=plt.subplots()
    index=np.arange(n_groups)
    bar_width=0.35
    plt.ylim(100000,220000)
    opacity=0.4
    error_config={'ecolor':'0.3'}
    plt.bar(index, avg_comp.loc["female"], bar_width,
                   alpha=opacity, color='r', yerr=sem_comp.loc["female"],
                   error_kw=error_config,label='Women')
    plt.bar(index+bar_width, avg_comp.loc["male"], bar_width,
                   alpha=opacity, color='b', yerr=sem_comp.loc["male"],
                    error_kw=error_config, label='Men')
    plt.ylabel('Compensation')
    plt.xticks(index+bar_width, ('Assistant Professor', 'Associate Professor',
                                 'Professor'))
    plt.title(Title)
    plt.legend()
    plt.tight_layout()
    return fig
    
plotSalary_by_RankSex(Title='Pay by Rank and Sex (All Universities)', 
                      avg_comp=comp_by_RS, sem_comp=comp_by_RS_sem)
plt.savefig('Graphs/PayRankSex.png')
plt.close()


# Calculate means and standard error of the mean by university
comp_by_uni= pd.pivot_table(df_mf,values='TotalCompensation', 
                       index=['University', 'Sex'],columns=['Rank'])
#print comp_by_uni
comp_by_uni_std= pd.pivot_table(df_mf,values='TotalCompensation', 
                       index=['University','Sex'],columns=['Rank'], 
                        aggfunc=np.std)
#print comp_by_uni_std
comp_by_uni_sem=comp_by_uni_std/np.sqrt(pd.pivot_table(df_mf,values='TotalCompensation', 
                       index=['University','Sex'],columns=['Rank'], 
                        aggfunc='count'))

#Graph overall mean compensations and standard error of the mean by university
def plotSalary_by_RankSexUni(Title, avg_comp, sem_comp, x):
    n_groups=3
    fig, ax=plt.subplots()
    index=np.arange(n_groups)
    bar_width=0.35
    plt.ylim(100000,220000)
    opacity=0.4
    error_config={'ecolor':'0.3'}
    plt.bar(index, avg_comp.loc[x, "female"], bar_width,
                   alpha=opacity, color='r', yerr=sem_comp.loc[x, "female"],
                   error_kw=error_config,label='Women')
    plt.bar(index+bar_width, avg_comp.loc[x, "male"], bar_width,
                   alpha=opacity, color='b', yerr=sem_comp.loc[x, "male"],
                    error_kw=error_config, label='Men')
    plt.ylabel('Compensation')
    plt.xticks(index+bar_width, ('Assistant Professor', 'Associate Professor',
                                 'Professor'))
    plt.title(Title)
    plt.legend()
    plt.tight_layout()
    return fig

for uni in good_unis:    
    plotSalary_by_RankSexUni(Title= uni + 'Pay by Rank and Sex', 
                      avg_comp=comp_by_uni, sem_comp=comp_by_uni_sem,x=uni )
    if 'Ottawa' in uni:
        plt.savefig('Graphs/Pay_University of Ottawa.png')
    else:
        plt.savefig('Graphs/Pay_' + uni + '.png')
    plt.close() 
    # Load data
#sexsalary=np.load('sexsalary.npy')
formula = 'TotalCompensation ~ C(Sex) + C(Rank) + C(Sex):C(Rank)'
lm = ols(formula, df_mf).fit()
anova_rslt=(anova_lm(lm))
print anova_rslt

rank_lst=np.unique(df_mf.Rank.values)
for rnk in rank_lst:
    print rnk
    df_rnk=df_mf[df_mf['Rank']==rnk]
    m_comp=df_rnk.TotalCompensation[df_rnk['Sex']=='male']
    f_comp=df_rnk.TotalCompensation[df_rnk['Sex']=='female']
    #Check for equality of variances and run appropriate test    
    eq_var=scipy.stats.levene(m_comp, f_comp)
    if eq_var[1] < 0.05:
        print "unequal var"
        print scipy.stats.ttest_ind(m_comp, f_comp, equal_var=False)
    else:
        print "equal var"
        print scipy.stats.ttest_ind(m_comp, f_comp)
    
# Run Anovas for all schools to examine whether there is an effect of sex,
#rank, and interaction between sex and rank

for uni in good_unis:
    print uni
    df_school=df_mf[df_mf['University']==uni]
    formula = 'TotalCompensation ~ C(Sex) + C(Rank) + C(Sex):C(Rank)'
    lm = ols(formula, df_school).fit()
    print(anova_lm(lm))
 
    for rnk in rank_lst:
        print rnk
        df_sch_rnk=df_school[df_school['Rank']==rnk]
        m_comp=df_sch_rnk.TotalCompensation[df_sch_rnk['Sex']=='male']
        f_comp=df_sch_rnk.TotalCompensation[df_sch_rnk['Sex']=='female']
        #Check for equality of variances and run appropriate test    
        eq_var=scipy.stats.levene(m_comp, f_comp)
        if eq_var[1] < 0.05:
            print scipy.stats.ttest_ind(m_comp, f_comp, equal_var=False)
        else:
            print scipy.stats.ttest_ind(m_comp, f_comp)