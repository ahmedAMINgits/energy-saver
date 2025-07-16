#ill import some necessary libraries of python here 

import pandas as pd 
import streamlit as st
import datetime 
import plotly.express as px

st.title("AI POWERED SMART ENERGY SAVER")

myfile=st.file_uploader("Upload your weekly energy usages excel datasheet: ",type=['xlsx'])
if myfile : 
    df=pd.read_excel(myfile)

    df["Day"]=df["Day"].astype(str)#making sure that the day column elements are sring type rather than numbers/hidden excel format


    today=datetime.datetime.today().strftime("%A")# getting todays name to be used as default*


    specific_col= [col for col in df.columns if col not in ["Day","Time","Total Consumption (kWh)","Date"] ] #basically separating appliance columns


## the bar chart portion 

    st.subheader("Stacked Bar Chart: Appliance Usage by Hour") 
    week_day = df['Day'].unique().tolist() #it creats a list of days to be used in the dropdown (if user wants to see another days usages)

    selected_day= st.selectbox("Select the day for bar chart",week_day,index=week_day.index(today) if today in week_day else 0 ) #basically a dropdown box user can select a specific day by default itll show today's day

    selected_day2= df[df["Day"]==selected_day]

    selected_day3= selected_day2[["Time"]+specific_col]

    selected_day3_melted = selected_day3.melt(id_vars='Time', value_vars=specific_col, var_name='Appliance', value_name='Usage')

    bar=px.bar (selected_day3_melted, 
             x="Time",
             y="Usage",
             color="Appliance",
             title=f' Hourly Appliance Usage Breakdown - {selected_day}',
             labels={"Usage":"kWh"} 

             )
    bar.update_layout(barmode="stack") 
    bar.update_layout(title_x=0.5, xaxis=dict(dtick=1), legend_title_text='Appliances')
    st.plotly_chart(bar, use_container_width=True)



#pie chart portion 
    st.subheader("Pie Chart: Appliance Usage Share") 

    selected_din=st.selectbox("Select the day for the pie chart",week_day,index=week_day.index(today) if today in week_day else 0)
    selected_din2= df[df["Day"]==selected_din]
    selected_din3= selected_din2[specific_col].sum().reset_index()
    selected_din3.columns=["Appliance","Usage"]

    pie=px.pie(
        selected_din3,
        values="Usage",
        names="Appliance",
        title=f"Appliance usage share - {selected_din}"

    )
    pie.update_layout(title_x=0.5)
    st.plotly_chart(pie,use_container_width=True)

    # a daily total consumption line chart 
    st.subheader("LINE CHART FOR THE WHOLE WEEK!!") 

    daily_total= df.groupby("Day")["Total Consumption (kWh)"].sum().reset_index()

    line=px.line(daily_total,x="Day",y="Total Consumption (kWh)",title="Total Daily Energy Consumption")
    st.plotly_chart(line,use_container_width=True)  



#prediction part yuoiii

    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import train_test_split

    big_df = pd.read_excel("energy_usage_20_weeks_cleaned.xlsx") #thats the big file which contain 20 weeks of data 
    big_df["Date"] = pd.to_datetime(big_df["Date"])
    big_df["Day"] = big_df["Date"].dt.dayofweek  # 0=Monday, ..., 6=Sunday
    big_df["Hour"] = big_df["Time"] 


    feature_cols = ["Day", "Hour", "AC", "Fridge", "Fan", "Light", "Heater", "Computer"]
    target_col = "Total Consumption (kWh)"
    X = big_df[feature_cols]
    y = big_df[target_col]


    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    today_int=datetime.datetime.today().weekday()
    tomorrow = ( today_int + 1) % 7
    hours = list(range(24))
    same_day_df = big_df[big_df["Day"] == today_int]  # all rows from today's day
    latest_date = same_day_df["Date"].max()  # find the latest date for today’s day
    latest_row = same_day_df[same_day_df["Date"] == latest_date].iloc[-1]  # last hour of that date (ill use the last hour to be used as the closest for the prediction )

    tomorrow_data = pd.DataFrame({
    "Day": [tomorrow] * 24,
    "Hour": hours,
    "AC": [latest_row["AC"]] * 24,
    "Fridge": [latest_row["Fridge"]] * 24,
    "Fan": [latest_row["Fan"]] * 24,
    "Light": [latest_row["Light"]] * 24,
    "Heater": [latest_row["Heater"]] * 24,
    "Computer": [latest_row["Computer"]] * 24
     })
    #actual prediction
    X_tomorrow = tomorrow_data[feature_cols]  # use same features used in training
    predicted_usage = model.predict(X_tomorrow)
    total_predicted_kwh = round(sum(predicted_usage), 2)

    tomorrow_name = (datetime.datetime.today() + datetime.timedelta(days=1)).strftime("%A")

    st.subheader(f"Predicted Total Energy Usage for {tomorrow_name}")

    st.metric(label="Estimated kWh", value=f"{total_predicted_kwh} kWh")

    #suggestions part !!!!

    df_pred = pd.DataFrame({
    "Hour": hours,
    "Predicted_kWh": predicted_usage
    })

   
    high_threshold = df_pred["Predicted_kWh"].quantile(0.75)  # picking top 25%
    low_threshold = df_pred["Predicted_kWh"].quantile(0.25)   # picking lowest 25%

    high_usage = df_pred[df_pred["Predicted_kWh"] > high_threshold]

    low_usage = df_pred[df_pred["Predicted_kWh"] < low_threshold]

    suggestions = []
    
    if not high_usage.empty:
     peak_hour_range = f"{high_usage['Hour'].min():02d}:00 – {high_usage['Hour'].max():02d}:00"
     suggestions.append(f" High energy usage between {peak_hour_range}. Consider reducing appliance use.")

    if not low_usage.empty:
     low_hour_range = f"{low_usage['Hour'].min():02d}:00 – {low_usage['Hour'].max():02d}:00"
     suggestions.append(f"Low energy demand between {low_hour_range}. U dont need need to consider here.")

    st.subheader("AI Smart Suggestions for Energy Saving")

    for tip in suggestions:
     st.markdown(f"- {tip}")






