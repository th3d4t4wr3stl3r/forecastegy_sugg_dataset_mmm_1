import streamlit as st
import pandas as pd
import altair as alt

st.title("Budget Analysis App")

curr_point_df = pd.read_csv('/workspaces/forecastegy_sugg_dataset_mmm_1/data/current_points.csv')
mROI_plotting = pd.read_csv('/workspaces/forecastegy_sugg_dataset_mmm_1/data/mROI_plotting.csv')

# Charting

# 1. Slider

# Instantiate the slider
fb_slider = alt.binding_range(min=0, max=10000,step=100,name='Facebook Budget    ')
gg_slider = alt.binding_range(min=0, max=10000,step=100,name='Google Ads Budget    ')
tt_slider = alt.binding_range(min=0, max=10000,step=100,name='TikTok Budget    ')

# Param Value
fb_budget = alt.param(name='fb_budget',value=0, bind=fb_slider)
gg_budget = alt.param(name='gg_budget',value=0, bind=gg_slider)
tt_budget = alt.param(name='tt_budget',value=0, bind=tt_slider)

# 2. Base Layer
base_chart = alt.Chart(mROI_plotting).add_params(fb_budget, gg_budget, tt_budget)

# 3. Curve Layer
curves = base_chart.mark_line().encode(
  x = alt.X('spend',
              axis=alt.Axis(title='Spend ($)')),     # ← rename x-axis
    y = alt.Y('sat_curve_pts',
              axis=alt.Axis(title='mROI')),  # ← rename y-axis
  color = 'channel'
)

# 4.1 Base Points
base_points = base_chart.encode(
    color='channel'
)

# 4.2 Optimal Points
opt_points = base_points.transform_window(
    max_sat='max(sat_curve_pts)',
    groupby=['channel'],
    frame=[None, None]
).mark_point(
    filled=True, 
    shape='diamond', 
    size=200
).encode(
    x='spend:Q',
    y='sat_curve_pts:Q',
    tooltip=['channel', 'spend', 'sat_curve_pts']
).transform_filter(
    alt.datum.sat_curve_pts == alt.datum.max_sat
).transform_calculate(
    label_text='"Optimum " + datum.channel + " spend : " + format(datum.spend, "$,.2f")'
)

# Optimal Labels
opt_labels = opt_points.mark_text(
    align='left', 
    dx=5,       # Shift the label 5 pixels to the right
    dy=-5
).encode(
    x='spend:Q',
    y='sat_curve_pts:Q',
    text='label_text:N'
)

# 4.3 Current Points
current_points = alt.Chart(curr_point_df).mark_point(
    filled=True, 
    shape='diamond', 
    size=200
).encode(
    x='spend',
    y='sat_curve_pts',
    color='channel:N'
).transform_calculate(
    label_text='"Current " + datum.channel + " spend : " + format(datum.spend, "$,.2f")'
)

# Current Labels
current_labels = current_points.mark_text(
    align='left', 
    dx=-5,       # Shift the label 5 pixels to the right
    dy=10
).encode(
    x='spend:Q',
    y='sat_curve_pts:Q',
    text='label_text:N'
)

# 5. Slider Integration
def make_slider_point(chart, channel, budget):
    return (
        chart
        .transform_filter(
            f"datum.channel == '{channel}'"
        )
        .transform_calculate(
            budget_value=f"{budget.name}",                    # param → field
            dist="abs(datum.spend - datum.budget_value)"     # use datum.budget_value
        )
        .transform_window(
            sort=[{"field": "dist", "order": "ascending"}],
            window=[{"op": "rank", "as": "rank"}]
        )
        .transform_filter("datum.rank == 1")
        .mark_point(
            filled=False,
            size=250,
                     # now works again
            strokeWidth=5
        )
        .encode(
            x="spend:Q",
            y="sat_curve_pts:Q",
            color="channel:N", 
            tooltip=["channel", "spend", "sat_curve_pts"]
        )
    )

fb_point = make_slider_point(base_chart, 'facebook', fb_budget)
gg_point = make_slider_point(base_chart, 'google_ads', gg_budget)
tt_point = make_slider_point(base_chart, 'tiktok', tt_budget)

# Don't forget to call the created items!!!
chart = curves + opt_points + opt_labels + current_points + current_labels + fb_point + gg_point + tt_point

st.altair_chart(chart)