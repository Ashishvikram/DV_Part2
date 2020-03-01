#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import altair as alt
import pandas as pd 

//Preprocessing of data
def pre_city(df):
    preprocess_df = df.dropna(how='all')
    preprocess_df = df.dropna(how='any', subset=['CITY'])
    city = preprocess_df[['LONC', 'LATC', 'CITY']]
    city.columns = ['lon','lat','city']
    return city;


def pre_temp(df):
    preprocess_df = df.dropna(how='any', subset=['TEMP'])
    temperatures = preprocess_df[['LONT','TEMP','DAYS','MON', 'DAY']]
    temperatures['DAY'] = temperatures['DAY'].astype('str')
    temperatures['DAY'] = temperatures['DAY'].str.strip('.0')
    temperatures['MON'] = temperatures['MON'].astype('str')
    temperatures['day'] = temperatures[['DAY', 'MON']].agg('-'.join, axis=1)
    temperatures = temperatures.drop(columns=['MON', 'DAY'])
    temperatures = temperatures.replace('nan-nan', np.nan)
    temperatures.columns = ['lon','temp','days','date']
    temperatures["date"] = temperatures.fillna("").apply(axis=1, func=lambda row: "{}°C  {}".format(row[1], row[3].replace("-", ",")))
    return temperatures;
    
def pre_army(df):
    army = df[['LONP','LATP','SURV','DIR','DIV']]
    army.columns = ['lon','lat','surv','dir','division']
    army = army.sort_values(by=["division", "surv"], ascending=False)
    return army;

def chart_create(temp,army,city):
    temperatures = temp
    troops = army
    cities = city
    
    troops_chart = alt.Chart(troops).mark_trail().encode(
        longitude='lon:Q',
        latitude='lat:Q',
        size=alt.Size(
            'surv',
            scale=alt.Scale(range=[1, 75]),
            legend=None
        ),
        detail='division',
        color=alt.Color(
            'dir',
            scale=alt.Scale(
                domain=['A', 'R'],
                range=['#FFE0B2', '#A1887F']
            ),
            legend=None
        ),
    )

    troops_text = troops.iloc[::2, :].copy()
    troops_text["lon"] += 0.13 * (troops_text["division"])
    troops_text["lat"] += troops_text["dir"].replace({"A": 0.35, "R": -0.21})

    x_encode_chart = alt.X(
        'lon:Q',
        scale=alt.Scale(domain=[troops["lon"].min(), troops["lon"].max()]),
        axis=alt.Axis(title="Longitude", grid=True))

    y_encode_chart = alt.Y(
        'lat:Q',
        scale=alt.Scale(domain=[troops["lat"].min() -1 , troops["lat"].max() +1]),
        axis=alt.Axis(title="Latitude", grid=True, orient="right"))

    troops_text_chart = alt.Chart(troops_text).mark_text(
        font='Helvetica Neue',
        fontSize=8,
        fontStyle='italic',
        angle=280
    ).encode(
        longitude='lon:Q',
        latitude='lat:Q',
        text='surv'
    )

    cities_chart = alt.Chart(cities).mark_text(
        font='Helvetica Neue',
        fontSize=10,
        fontStyle='italic',
        dx=-4
    ).encode(
        longitude='lon:Q',
        latitude='lat:Q',
        text='city',
    )
    
    x_encode = alt.X(
        'lon:Q',
        scale=alt.Scale(domain=[troops["lon"].min(),troops["lon"].max()]),
        axis=alt.Axis(title="Longitude", grid=True))
    
    y_encode = alt.Y(
        'temp',
        axis=alt.Axis(title="Temperature on Retreat", grid=True,orient='right'),
        scale = alt.Scale(domain=[temperatures["temp"].min() - 10, temperatures["temp"].max() + 10]))
    
    temperatures_chart = alt.Chart(temperatures).mark_line(
        color="#F44336"
    ).encode(
        x=x_encode,
        y=y_encode,
    ) + alt.Chart(temperatures).mark_text(
        dx=10,
        dy=30,
        font='Copperplate',
        fontSize=14
    ).encode(
        x=x_encode,
        y=y_encode,
        text='date',
    )

    temperatures_chart = temperatures_chart.properties(height=200)
    
    map_chart = troops_chart + cities_chart + troops_text_chart + alt.Chart(troops).mark_text().encode(
        x=x_encode_chart,
        y=y_encode_chart,
    )
    
    final_chart = alt.vconcat(map_chart, temperatures_chart).configure_view(
        width=1200,
        height=800,
        strokeWidth=0
    ).configure_axis(
        grid=True,
        labelFont="Copperplate",
        titleFont="Copperplate",
    )

    return final_chart


def main():
    df = pd.read_csv('minard-data.csv')
    city = pre_city(df)
    temp = pre_temp(df)
    army = pre_army(df)
    chart = chart_create(temp,army,city)
    chart.save('minard.svg')
  
if __name__== "__main__":
  main()



    



