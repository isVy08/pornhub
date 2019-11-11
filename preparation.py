#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: vyvo
This deals with preparing data before analysis, which involves checking for duplications, 
and handling missing values   

"""

import pandas as pd 
import matplotlib.pyplot as plt  
import numpy as np

pd.options.display.float_format = '{:f,.2f}'.format
pd.set_option('display.max_columns', 500)

#Import data

data = pd.read_csv('final.csv')

#Duplicated rows 
data[data.duplicated()] 

#Non null values 
data.count() 



# -------------- 

"""
Dependent variables: Subscribers

Numerical Variables: Age, Height in cm, Weight in lbs, Total views, Video_upload, Rank
Breast size, Waist size, Hip size, Seniority 

Categorical variables: Cup size, Country, Star Sign, Fake Boobs, Hair Color, Interested in, 
Relationship status, Piercings, Birthday 
"""

#Name: Most popular First Name and Last Name  

data.Name.str.split(' ',expand=True).iloc[:,0].value_counts().head(5) #top 5 first names 
data.Name.str.split(' ',expand=True).iloc[:,1].value_counts().head(5) #top 5 last names 


#Age / Height / Weight 
data['Age'].hist() # distribution a little left-skewed, fill median in missing values 
data['Age'].fillna(data.Age.median(),inplace=True)
data.Age.mean()

data['Height in cm'].hist() #distribution approx normal, fill mean
data['Weight in lbs'].hist() #distribution approx normal, fill mean 

data['Height in cm'].fillna(data['Height in cm'].mean(),inplace=True)
data['Height in cm'].mean()

data['Weight in lbs'].fillna(data['Weight in lbs'].mean(),inplace=True)
data['Weight in lbs'].mean()

## Other numerical variables: Fill average values if she is verified pornstar 
no = data.loc[data.Verified == 'No',:].index
yes = data.loc[data.Verified == 'Yes',:].index

#Breast size 
data['Breast size'].hist(by=data['Fake Boobs']) # distribution left-skewed, fill median 
data['Breast size'].groupby(data['Fake Boobs']).mean() #same median values whether boobs are fake
cupmed = data['Breast size'].median() 
for i in yes: 
    if np.isnan(data.loc[i,'Breast size']): data.loc[i,'Breast size'] = cupmed 

data['Breast size'].mean()   

#Check Linear Regression between Weight and Waist size / Hip size 

for var in ['Waist size','Hip size']:
    a = data[[var,'Weight in lbs']].dropna()
    print(np.corrcoef(a.iloc[:,0], a.iloc[:,1]))
    plt.scatter(a.iloc[:,0], a.iloc[:,1], label=var) 
    plt.legend()

#Waist & Hip size is highly correlated with Weight --> Using linear regression for imputation

#Waist size 
from sklearn.linear_model import LinearRegression
a = data[['Waist size','Weight in lbs']].dropna()
X = a.iloc[:,1].to_numpy().reshape(-1,1)
y = a.iloc[:,0].to_numpy()

reg = LinearRegression().fit(X, y)
reg.score(X, y) #Rsq 
b1 = reg.coef_[0]
b0 = reg.intercept_

for i in yes:
    if np.isnan(data.loc[i,'Waist size']): data.loc[i,'Waist size'] = data.loc[i,'Weight in lbs']*b1 + b0

data['Waist size'].describe()

#Hip size

a = data[['Hip size','Weight in lbs']].dropna()
X = a.iloc[:,1].to_numpy().reshape(-1,1)
y = a.iloc[:,0].to_numpy()

reg = LinearRegression().fit(X, y)
reg.score(X, y) #Rsq 
b1 = reg.coef_[0]
b0 = reg.intercept_

for i in yes:
    if np.isnan(data.loc[i,'Hip size']): data.loc[i,'Hip size'] = data.loc[i,'Weight in lbs']*b1 + b0

data['Hip size'].describe()


#Seniority 
data.Seniority.hist() #left-skewed, fill median      
senmed = data.Seniority.median()
for i in yes: 
    if np.isnan(data.loc[i,'Seniority']): data.loc[i,'Seniority'] = senmed
    
data.Seniority.describe()    

## Categorical variables - If verified, fill mode values. Otherwise, fill 'Not revealed' 
cat = data.select_dtypes(include="object").drop(columns=['Name','Birthday','Verified']).columns 
for col in cat:
    mode = data[col].mode()[0]
    data.loc[yes,col] = data.loc[yes,col].fillna(mode)

    

#double check non-null values         
data.count()



# CORRELATION VS. SUBSCRIBERS
#Examinine distribution 
plt.hist(data['Subscribers'],bins=50)
plt.title("Histogram of Subscribers")
data['Subscribers'].describe()
data['Subscribers'].quantile(0.9)

#Scatter plot with Subscribers 
for var in ['Age','Height in cm','Weight in lbs','Breast size','Waist size','Hip size','Video_upload']: 
    plt.scatter(data[var],data['Subscribers'])
    title = '{} vs. Subscribers, n = {}'.format(var,data[var].count())
    plt.title(title)
    plt.xlabel(var)
    plt.ylabel('Subscribers')
    plt.show()


row = data.shape[0]
total_sub = data['Subscribers'].sum()
top20_sub = data['Subscribers'].sort_values(ascending=False).head(round(0.2*row)).sum()
idx = data['Subscribers'].sort_values(ascending=False).head(round(0.2*row)).index
top20_sub/total_sub #top 20% pornstars take up around 87% of total subscribers 

#%total video uploads 
data.loc[idx,'Video_upload'].sum()/(data['Video_upload'].sum())

#Subscribers by Verified 
data['Subscribers'].groupby(data['Verified']).mean().plot(kind="barh",title="Subscribers by Verified Status, n = 11395")


#Subscribers by Fake Boobs 
total_fb = data[data['Fake Boobs'] == "Yes"].shape[0]

data['Breast size'].groupby(data['Fake Boobs']).mean().plot(kind="barh")
data['Subscribers'].groupby(data['Fake Boobs']).mean().plot(kind="barh",title="Subscribers by Fake Boobs, n = 4021")

#Combine those cup sizes with less than 100 sample sizes and assign as "Others"
b = data['Cup size'].value_counts(sort=False).sort_values(ascending=False)
data['Cup size'] = data['Cup size'].replace([b[b<=100].index],'Others')
data.loc[data['Fake Boobs'] == 'Yes','Subscribers'].groupby(data['Cup size']).mean().sort_values(ascending=True).plot(kind="barh",title="Subscribers with Fake Boobs by Cup size, n = 276")

#Subscribers by Star Sign 

data['Star Sign'].value_counts().plot("barh")
data['Subscribers'].groupby(data['Star Sign']).mean().sort_values(ascending=True).plot(kind="barh",title="Subscribers by Zodiac Sign, n = 11395")





