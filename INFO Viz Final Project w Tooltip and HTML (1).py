#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd 
import numpy as np      
    

county_vax_df = pd.read_csv("Provisional_COVID-19_Death_Counts_in_the_United_States_by_County.csv")
#Link to this Data set  
#https://data.cdc.gov/Vaccinations/COVID-19-Vaccinations-in-the-United-States-County/8xkx-amqh 
# Make sure we also turn in this csv file with the submission 

vax_df = pd.read_json('https://data.cdc.gov/resource/d6p8-wqjm.json') 
#Link to this Data Set:  
#https://data.cdc.gov/Public-Health-Surveillance/Rates-of-COVID-19-Cases-or-Deaths-by-Age-Group-and/d6p8-wqjm


# ## Data Sets for the Personalized Graphs

# In[2]:


vax_df = vax_df.drop(columns=['crude_booster_ir', 'crude_primary_series_only_ir','crude_unvax_ir', 
                              'crude_booster_irr', 'crude_irr', 'continuity_correction','age_adj_booster_ir', 
                              'age_adj_vax_ir', 'age_adj_unvax_ir','age_adj_booster_irr', 'age_adj_irr','month'])   
 
vax_df['mmwr_week'] = vax_df['mmwr_week']*10 + 0
vax_df['date'] = pd.to_datetime(vax_df['mmwr_week'], format='%Y%W%w')
print(vax_df.shape)
vax_df.head()       


# In[3]:


vax_df = vax_df.drop(columns=['mmwr_week'],axis=1)


# In[4]:


df = vax_df.set_index('date').groupby([pd.Grouper(freq='W'),'age_group','outcome','vaccine_product']).sum() 
df.head()


# In[5]:


# Reset index to create separate columns for `date`, `age_group`, `outcome`, and `vaccine_product`
df = df.reset_index()

# Melt the dataframe to transform it into a long format
melted_data = pd.melt(df, id_vars=['date', 'age_group', 'outcome', 'vaccine_product'], value_vars=['boosted_with_outcome', 'primary_series_only_with_outcome', 'unvaccinated_with_outcome'], var_name='Vaccination Status') 
melted_data.head()  


# ## Data set for Universal Graph (the map) 

# In[6]:


county_vax_df = county_vax_df.drop_duplicates(subset = 'FIPS County Code')      
county_vax_df['% of Total Deaths Related to Covid'] = ((county_vax_df['Deaths involving COVID-19'] 
                                                              / county_vax_df['Deaths from All Causes'])*100).round(2)  

county_vax_df.head()


# ## The DashBoard 

# In[7]:


import altair as alt
from vega_datasets import data
import pandas as pd

counties = alt.topo_feature(data.us_10m.url, 'counties')
states = alt.topo_feature(data.us_10m.url, 'states')
source = county_vax_df

deaths = melted_data
#print(deaths.head())
#print(type(deaths))

age_group = ['5-11', '12-17', '18-49', '50-64', '65+', 'all_ages']   

vaccine_product = ['all_types', 'Janssen', 'Moderna', 'Pfizer']

outcome = ['case','death']

age_dropdown = alt.binding_select(options=age_group, name='Select Age Group')
outcome_dropdown = alt.binding_select(options= outcome, name='Select Outcome') 
vaccine_dropdown = alt.binding_select(options = vaccine_product, name='Select Vaccine Product') 

age_selection = alt.selection_single(fields=['age_group'], bind=age_dropdown)
outcome_selection = alt.selection_single(fields=['outcome'], bind=outcome_dropdown) 
vaccine_selection = alt.selection_single(fields =['vaccine_product'],bind=vaccine_dropdown)

line = alt.Chart(deaths.reset_index()).mark_line().encode(
    x = 'date',
    y = 'value:Q', 
    color = 'Vaccination Status:N',
    tooltip = ['date', 'value'] 
).properties(
    title=['Personalized Visulization: Cases and Deaths for Boosted Individuals']  
).add_selection( 
    outcome_selection 
).add_selection( 
    age_selection 
).add_selection( 
    vaccine_selection
).transform_filter( 
    outcome_selection 
).transform_filter( 
    age_selection  
).transform_filter( 
    vaccine_selection 
).interactive()


highlight = alt.selection_single(on='mouseover', fields=['id'], empty='none')

plot = alt.Chart(counties).mark_geoshape().encode(
    color=alt.condition(highlight, alt.value('red'), '% of Total Deaths Related to Covid:Q'),
    tooltip=['County name:O','% of Total Deaths Related to Covid:Q']
).transform_lookup(
    lookup='id',
    from_=alt.LookupData(source, 'FIPS County Code', ['% of Total Deaths Related to Covid', 'County name'])
).add_selection(highlight).project(
    type='albersUsa'
).properties(
    width=900,
    height=600,
)

outline = alt.Chart(states).mark_geoshape(stroke='blue', fillOpacity=0).project(
    type='albersUsa'
).properties(
    width=700,
    height=400
)

m = alt.layer(plot,outline).properties(title=["Universal Visulaization: % of Total Deaths Attributed to Covid-19 per County"]) 

final_plots = m & line 


# In[8]:


final_plots


# In[9]:


# Note: In order to get the proper graphs the "Select Outcome"  
# and the "Select Age Group" Filters  
# must be changed atleast once each


# In[10]:


get_ipython().system('pip install altair_saver')


# In[11]:


import altair_saver

# Save the chart as an HTML file
altair_saver.save(final_plots, 'INFO Visualization Final Project.html')


# In[12]:


from IPython.display import HTML

# Define the file path of the HTML file
file_path = './INFO Visualization Final Project.html'

# Create an HTML string with a hyperlink to the HTML file
html_string = f'<a href="{file_path}" target="_blank">Open HTML file</a>'

# Display the HTML string in the notebook output
HTML(html_string)


# In[ ]:




