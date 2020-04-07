# Restaurant Risk

This repository contains the files used to create Restaurant Risk, an app that assesses the risk of opening a restaurant at a given NYC street address and suggests some alternative locations.

## Data Acquisition and Cleaning

I used NYC Open Data's Food Permits Requests database to estimate the restauration duration for all NYC restaurants starting in 2010. I am using NYC Department of Health guidelines, which state that restaurants must renew their food permits every year, as the basis for my approach. Thus, the cleanliness and accuracy of my data is a function of the NYC DOH'S recordkeeping. The creation and cleaning of this dataset can be found in 'food_pmt_clean.ipynb'. 

I merged the permit request data with a variety of spatial data taken from the Census and other NYC Open Data sources (subway entrances, restaurant grades, etc.) The spatial joins of these datasets can be found in 'geopandas_restaurant_address.ipynb'.

More information about NYC Food Permit requests can be found here: https://www1.nyc.gov/nycbusiness/description/food-service-establishment-permit/about

## Analysis

The linear amd random forest regressions I ran and accompanying validation and analysis can be found in 'restaurants_regressions.ipynb'. I used the models to predict the number of years a restaurant would stay open given closure rates since 2010.

## Flask Web App

Finally, I built the web app for my product using the files in the 'Flask restaurant' folder. The final product is hosted on an AWS server.  
