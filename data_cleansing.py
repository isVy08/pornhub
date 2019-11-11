#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 20 22:10:02 2019

@author: vyvo
"""
import pandas as pd 
import numpy as np

df = pd.read_csv("raw_profile.csv")

df.columns 
#Remove ":" from column names 

d = {}
for col in df.columns: 
    d[col] = col.strip(":")
    
df = df.rename(columns=d)

## Now start cleaning each variables 

"""
NUMERICAL VARIABLE: 
Age, Subscribers, Total views, Height, Weight, Measurements
"""

#1. Name: Remove quotation marks " "
df.Name = df.Name.str.strip('"|" ')


#2. Subscribers / Total views: Remove white spaces and convert to numerical values, e.g., 862K to 862,000, 2M to 2,000,000

import re
def clean_string(value): 
    if 'K' in value: return eval(re.sub('\n|\t|,|K|M| ','',value))*1000 
    elif 'M' in value: return eval(re.sub('\n|\t|,|K|M| ','',value) )*1000000 
    else: return eval(re.sub('\n|\t|,|K|M| ','',value)) 

#Subscribers 
df['Subscribers'] = df['Subscribers'].apply(clean_string)

#Total views 
df['Total views'] = df['Total views'].apply(clean_string)

#3. Height: Get measures in cm 
df['Height in cm'] = df['Height'].str.extract(r'.\((.*)\)')
df['Height in cm'] = df['Height in cm'].str.strip("cm").astype('float64')

#4.Weight: Get measures in lbs  
df['Weight in lbs'] = df['Weight'].str.strip('\n|\t| ') 
df['Weight in lbs'] = df['Weight in lbs'].str.extract(r'(^\d*)').astype('float64') #or r'\d+(?= lbs)'

#4.Measurements: Split into 4 different values - Breast size, Cup size, Waist size & Hip size  
# e.g, 34D-23-25 -> Breast size = 34, Cup size = D, Waist size = 23 and Hip size = 25
body = df['Measurements'].str.split("-",expand=True) 
body[1].unique() #check unique values of a Series, contain space value ' ' 

#So, replace space with null values 
body[body == ''] = np.nan  

# Cup size & Breast size 
body[0] = body[0].str.strip('\n|\t| ') #remove white spaces
body['Cup size'] = body[0].str.extract(r'([A-Z]+)')  
body['Breast size'] = body[0].str.extract(r'(\d+)') 
body['Breast size'] = body['Breast size'].astype('float64') 

# Waist size 
body['Waist size'] = body[1].astype('float64')

# Hip size
body['Hip size'] = body[2].str.strip('\n|\t| ')
body['Hip size'] = body[2].astype('float64')


#Then, merge dataframe Body to original df  
df = pd.concat([df,body.iloc[:,3:]],axis=1) 
 

## For variable Age, it's more accurate to have Age calculated from Birthday information. 

"""
CATEGORICAL VAR: 
Background/Birthplace/Birth place/City and Country, Ethnicity/Hometown, 
Birthday/Born/Star Sign, Career Start and End/Career Status, 
Eye color, Fake boobs, Hair Color, Piercings, Tattoss, Interested in, Relationship Status, 
Interests and Hobbies, Turn Offs, Turn Ons, Website
"""
#1.Combine Birthplace, Background, City and Country to only Country and delete Ethnicity and Hometown 
df = df.drop(columns = ["Ethnicity","Hometown"])
a = df['Background'].fillna(df['Birth Place']).fillna(df['Birthplace']).fillna(df['City and Country'])
a = a.str.strip('\n|\t| ').str.split(",",expand=False)

#Get Country information only, exclude States/City, e.g., get Germany from [Bayern, Germany]
country = []

for element in a: 
    if element is np.nan: country.append(np.nan) 
    else: country.append(element[-1])

df['Country'] = pd.Series(country).str.strip(' ') #remove space & create new variable named Country

#Now check the values for consistency 
df['Country'].unique()

#We see that some values are ISO Code, some are Nationality 
#Then we map ISO Code to Country using library Pycountry & Nationality to Country using demonyms.csv 

demonyms = pd.read_csv("demonyms.csv") #import file mapping nationality to country

dem_dict = {} 
demonyms.head(3)

for i in range(demonyms.shape[0]): 
    dem_dict[demonyms.Nationality[i]] = demonyms.Country[i]
    
import pycountry as pcy #remember to install before usage
result = [] 

for element in df.Country: 
    if element is np.nan: result.append(np.nan)
    elif len(element) == 2: result.append(pcy.countries.get(alpha_2=element).name) #if it's Code, map to Country
    else:
        try:
            result.append(dem_dict[element]) #if it's Nationality, map to Country using dem_dict 
        except Exception: 
            result.append(element) #if error raised, this means value is already Country 
    

##Handle Odd values 
odd = []
for o in result: #check odd values
    if o not in list(demonyms.Country) and o not in odd: odd.append(o) 

result = pd.Series(result).replace({'Cherokee':'United States','United States of America':'United States','Jewish':'Israel','Republic of':'South Korea','Dominican Republic':'Dominica','Czechia':'Czech Republic','Native American':'United States','Cuban-American':'United States','Russian Federation':'Russia','Arabic':'Saudi Arabia'})
df.Country = result 

#2.Birthday / Star sign / Age 
#Some profiles have birth date information stored in variable Born, some in Birthday
df['Birthday'] = pd.to_datetime(df['Birthday'])
df['Born'] = pd.to_datetime(df['Born'])
df['Birthday'] = df['Birthday'].fillna(df['Born']) #combine into one

#Zodiac Signs 
star = []
for i in range(df.shape[0]): 
    if df['Birthday'][i].month == 12:
    	astro_sign = 'Sagittarius' if (df['Birthday'][i].day < 22) else 'Capricorn'
    elif df['Birthday'][i].month == 1:
    	astro_sign = 'Capricorn' if (df['Birthday'][i].day < 20) else 'Aquarius'
    elif df['Birthday'][i].month == 2:
    	astro_sign = 'Aquarius' if (df['Birthday'][i].day < 19) else 'Pisces'
    elif df['Birthday'][i].month == 3:
    	astro_sign = 'Pisces' if (df['Birthday'][i].day < 21) else 'Aries'
    elif df['Birthday'][i].month == 4:
    	astro_sign = 'Aries' if (df['Birthday'][i].day < 20) else 'Taurus'
    elif df['Birthday'][i].month == 5:
    	astro_sign = 'Taurus' if (df['Birthday'][i].day < 21) else 'Gemini'
    elif df['Birthday'][i].month == 6:
    	astro_sign = 'Gemini' if (df['Birthday'][i].day < 21) else 'Cancer'
    elif df['Birthday'][i].month == 7:
    	astro_sign = 'Cancer' if (df['Birthday'][i].day < 23) else 'Leo'
    elif df['Birthday'][i].month == 8:
    	astro_sign = 'Leo' if (df['Birthday'][i].day < 23) else 'Virgo'
    elif df['Birthday'][i].month == 9:
    	astro_sign = 'Virgo' if (df['Birthday'][i].day < 23) else 'Libra'
    elif df['Birthday'][i].month ==  10:
    	astro_sign = 'Libra' if (df['Birthday'][i].day < 23) else 'Scorpio'
    elif df['Birthday'][i].month == 11:
    	astro_sign = 'Scorpio' if (df['Birthday'][i].day < 22) else 'Sagittarius'
    else: astro_sign = pd.NaT
    star.append(astro_sign)
    
df['Star Sign'] = pd.Series(star)

#Now let's create variable Age. Before doing this, we need to check whether Year values come in the right format 
df['Birthday'].dt.year.unique()

#Some values exceed 2000, e.g. a pornstar born in 2059 where it's supposed to be 1959 
#or another born in 2017 while the minimum age to do porn is 18; it's supposed to 1917

df['Age'] = 2019 - df['Birthday'].dt.year.apply(lambda x: x-100 if x > 2002 else x)

#Drop records with Age >= 80 
df = df.drop(df[df.Age>=80].index)
df = df.reset_index(drop=True)


#3.Career Start End / Active status to Seniority Get the year start only 
df = df.drop(df[df['Career Status'] == "Inactive"].index) #Delete those inactive
df = df.reset_index(drop=True)
df['Seniority'] = df['Career Start and End'].str.strip('\n|\t| ').str.extract(r'(^\d+)').astype("float64")
df.Seniority = 2019 - df.Seniority 

#Delete Website, Interests and Hobbies, Turn offs, Turn ons: Many missing values and values very unstructured
df = df.drop(columns = ['Website','Interests and hobbie', 'Turn Offs', 'Turn Ons'])

#Boolean Eye Color, Fake Boobs, Hair Color, Piercings, Tattoss, Interested in, Relationship status, 
df['Fake Boobs'] = df['Fake Boobs'].str.strip('\n|\t| ')
df['Hair Color'] = df['Hair Color'].str.strip('\n|\t| ')
df['Piercings'] = df['Piercings'].str.strip('\n|\t| ')
df['Interested in'] = df['Interested in'].str.strip('\n|\t| ')
df['Relationship status'] = df['Relationship status'].str.strip('\n|\t| ')

#Hair Color: Those with many hair colors are assigned on this variable as Various 
a = df['Hair Color'].str.split(',',expand=False)

def hair(list_elem):
    if list_elem is np.nan: 
        return np.nan 
    elif len(list_elem) == 1: 
        return list_elem[-1]
    else: return "Various" 
df['Hair Color'] = a.apply(hair)

#Create one more variable on Verified status. 
#Notice that Verified pornstars have values in variable Birthplace while this variable named "Birth Place" for the Non-verified  
df['Verified'] = df['Birthplace'].fillna("Yes")
df['Verified'] = df['Verified'].apply(lambda x: "No" if x != "Yes" else "Yes") 


##FINAL DATASET 

new_df = df[['Name','Subscribers','Total views','Height in cm', 'Weight in lbs','Breast size','Cup size','Waist size','Hip size','Country','Birthday','Age','Star Sign','Seniority','Fake Boobs','Hair Color','Piercings','Interested in','Relationship status','Verified']]

p = pd.read_csv('pornstars.csv') #join with pornstar "directory" to get information on Rank and Video upload
new_df = new_df.join(p[['Name','Video_upload','Rank']].set_index('Name'),on='Name') 

data.to_csv('test.csv',index=False)

