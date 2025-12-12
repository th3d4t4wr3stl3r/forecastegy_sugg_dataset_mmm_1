import streamlit as st
import pandas as pd
import altair as alt
from shared_components import sidebar_content

sidebar_content()

st.title("Simple MMM With 3 Channels")
st.divider()
# Model Explanation
st.markdown('''
### Model Explanation 
            
Model is an Ordinary Least Squares (OLS) model fitted with Heteroscedasticity and Autocorrelation Consistent standard errors. OLS seemed the most appropriate for this simple dataset assuming that the data did not violate any of the assumptions.

___
            
#### Brief Model Summary
1. R-squared (0.852): Our model is robust and explains 85.2\% of the variation in Sales over the modeled period.
This shows a good fit for our marketing mix model and gives us high confidence in the derived channel impacts.

2. F-statistic & Prob (F-statistic): The overall model is highly statistically significant (Prob ≈0.000), confirming 
that the marketing spend variables are collectively driving a measurable and meaningful impact on sales.

3. Covariance Type (HAC): We used HAC (Robust) Standard Errors to account for time-series effects like autocorrelation
and heteroscedasticity). This means the precision and significance levels we report for each channel are reliable.

4. Durbin-Watson (1.691): This value is close to the ideal 2.0, suggesting that we have effectively addressed any 
significant time-lag or autocorrelation issues in the model structure.

___

#### Coefficient Analysis	
| Coefficient (Volume/Units) | Value | Client Interpretation |
| :--- | :--- | :--- |
| **Baseline (const)** | 5,802 | Organic Foundation: This is the sales volume generated without paid media—driven by brand equity, distribution, seasonality, and word-of-mouth. This is the sales floor. |
| **TikTok (saturation\_tiktok)** | 4,981 | Highest Volume Driver: TikTok delivers the largest incremental sales volume among all media channels. |
| **Google Ads (saturation\_google\_ads)** | 2,731 | Strong Incremental Volume: A significant, reliable driver of sales, likely capturing high-intent demand. |
| **Facebook (saturation\_facebook)** | 2,682 | Steady Incremental Volume: Contributes substantial volume, likely balancing upper and lower-funnel activity. |

The above coefficients must be taken with a grain of salt. Higher incremental sales volume does not necessarily translate to higher profitability. 
            
''')

# ---------------------------------------------------------------
# Forest Plot
data = {
    'Channel': ['Baseline', 'Facebook', 'Google Ads', 'TikTok'],
    'Coefficient': [5802.32, 2682.10, 2731.15, 4981.21],
    'Lower_CI': [5398.50, 2293.63, 2347.35, 4642.94],
    'Upper_CI': [6206.14, 3070.56, 3114.95, 5319.48]
}
df_coef = pd.DataFrame(data)
channel_order = ['Baseline', 'TikTok', 'Google Ads', 'Facebook']

# Define the shared X-axis encoding with the rotated label
x_encoding = alt.X(
    'Channel:N', 
    sort=channel_order, 
    title='Marketing Channel / Baseline',
    axis=alt.Axis(labelAngle=0, titleFontWeight='bold') 
)

# 1. Create the Rule mark for The Error Bar
error_bars = alt.Chart(df_coef).mark_rule().encode(
    x=x_encoding,
    y=alt.Y('Lower_CI:Q', title='Sales Volume Contribution', axis=alt.Axis(titleFontWeight='bold')),
    y2='Upper_CI:Q',
    tooltip=['Channel', alt.Tooltip('Lower_CI', format=',.0f', title='Lower Bound'), alt.Tooltip('Upper_CI', format=',.0f', title='Upper Bound')]
)

# 2. Create the Point mark for the Coefficient Estimate (The Dot)
point_estimate = alt.Chart(df_coef).mark_point(size=150, filled=True).encode(
    x=x_encoding,
    y=alt.Y('Coefficient:Q'),
    color='Channel:N',
    tooltip=['Channel', alt.Tooltip('Coefficient', format=',.0f')],
)

# 3. Add a horizontal line at zero
zero_line = alt.Chart(pd.DataFrame({'Zero': [0]})).mark_rule(color='lightgray', strokeDash=[3, 3]).encode(
    y='Zero:Q'
)

# 4. Combine the layers
coefficient_plot = (zero_line + error_bars + point_estimate).properties(
    title='Model Coefficient Estimates with 95% Confidence Intervals'
).interactive()

coefficient_plot

st.write('The size of the line on the circle marker shows the confidence interval of each value (smaller is better). The length of the error bar represents the precision. Shorter bars (like TikTok\'s) mean we have higher confidence in the true impact falling close to our estimate. Longer bars (if any were present) indicate more uncertainty or risk.')
# ---------------------------------------------------------------

st.markdown('''

___
#### Test and Validation
            
Test was 40\% of the Total dataset length and further split into Validation
            
| Phase | Split | RMSE | MAPE |
| :--- | :--- | :--- | :--- |
| **Test** | 60:20 Train:Test | 1201.89 | 0.095 |
| **Validation** | 20:20 Test:Validation | 868.8 | 0.067 |

''')

st.write()

# Train Test Validation plots
model_pred_df = pd.read_csv('data/model_results.csv')

mod_chart_test = alt.Chart(model_pred_df.melt(id_vars=['date'], value_vars=['y_test','y_pred_test']).dropna()).encode(
    x=alt.X('date', title='Date', axis=alt.Axis(labelAngle=0, titleFontWeight='bold')),
    y=alt.Y('value', title='Sales', axis=alt.Axis(titleFontWeight='bold')),
    color=alt.Color('variable', title='Test')
).mark_line().properties(
    title='Hold-Out Method (Test)'
).interactive()

mod_chart_val = alt.Chart(model_pred_df.melt(id_vars=['date'], value_vars=['y_val', 'y_pred_val']).dropna()).encode(
    x=alt.X('date', title='Date', axis=alt.Axis(labelAngle=0, titleFontWeight='bold')),
    y=alt.Y('value', title='Sales', axis=alt.Axis(titleFontWeight='bold')),
    color=alt.Color('variable', title='Validation')
).mark_line().properties(
    title='Hold-Out Method (Validation)'
).interactive()

mod_chart_test
mod_chart_val

st.write('As we can see in the plots above, the model is able to generalize quite well on unseen data as verified with 2 isolated datasets.')
st.divider()
# ---------------------------------------------------------------

st.subheader('Diminishing Returns Analysis')

# Saturation Volume plot
st.write('Parameters to calculate saturation were put through an OLS model and chosen based on the lowest Bayesian Information Criterion (BIC) score. In the below plots, we can see that for each channel, the returns plateau and do not show any tangible benefit even if spend is increased beyond a point (saturation point).')

plot_sat_df = pd.read_csv('data/plot_sat_df.csv')

plot_sat_curves = alt.Chart(plot_sat_df).encode(
    x=alt.X('adstock', title='Spend'),
    y=alt.Y('saturation', title='Saturation'),
    color=alt.Color('channel', title='Channel'),
).mark_line(
).properties(
    title='Saturation Plot'
).interactive()

plot_sat_curves

# ---------------------------------------------------------------

st.subheader('Budget Optimizer Tool')

st.markdown('''
Here below we can see the marginal Return on Investment (mROI) vs Simulated Marketing Spend. The current and optimum levels of average (mean) spend are also marked. We can see that all the channels are underspending before they each hit their optimum mROI efficiency mark. 
            
#### Data-driven reallocation to unlock $53k in annual efficiency gains while reducing total spend by 29%
            
1. All 3 channels are underspending.
2. Google Ads presents the best opportunity of increasing spend. mROI is almost at the optimal efficiency point. Highly recommend increasing it to $1,743.
3. Facebook has a current mROI of 0.07 because we are currently spending in the "cold start" zone. Increasing spend should unlock it's true potential. Gradual increases of spend while monitoring mROI suggested.
4. TikTok has the lowest optimum efficiency point at 0.7, which means that even at peak efficiency, we are losing \$0.3 per \$1, which suggests that a creative strategy or product-market fit issue might exist. Consider reallocating budget to Google Ads and Facebook.

##### Ideal Scenarios
| Channel | Current | Optimal | Change | Current MROI | Expected MROI | Weekly Impact | Annual Impact |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Google Ads** | $1,521 |$1,743 | +$222 | 2.5:1 | 3.3:1 | +$733/wk | +$38k/yr |
| **Facebook** | $2,216 | $3,687 | +$1,471 | ~0:1 | 1.7:1 | +$2,500/wk | +$130k/yr | 
| **TikTok** | $3,946 | $0 | -$3,946 | ~0:1 | N/A | +$1,184/wk* | +$62k/yr |
| **TOTAL** | $7,683 | $5,430 | -$2,253 | — | — | +$4,417/wk | +$230k/yr |

| Expected Outcome |
| :--- | 
| Weekly spend: -29% (\$7,683 → \$5,430) |
| Annual spend reduction: -\$117k |
| Portfolio efficiency: +35% |
| Annual contribution gain: +\$230k |
| Total annual impact: ~\$347k |
|                                       |
| **RISK MITIGATION**                      |
| Phased rollout with validation gates at each step.   |

''')

st.divider()

curr_point_df = pd.read_csv('./data/current_points.csv')
mROI_plotting = pd.read_csv('./data/mROI_plotting.csv')

# Charting Budget Tool

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
base_chart = alt.Chart(mROI_plotting).properties(
    width=800,
    height=400
).add_params(fb_budget, gg_budget, tt_budget)

# 3. Curve Layer
curves = base_chart.mark_line().encode(
  x = alt.X('spend', title='Marketing Spend'),
  y = alt.Y('sat_curve_pts', title='Marginal ROI'),
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
    tooltip=[
      alt.Tooltip("channel", title='Channel'),
      alt.Tooltip("spend", title='Spend', format='$.2f'),
      alt.Tooltip("sat_curve_pts", title='Marginal ROI', format='$.2f')
    ]
).transform_filter(
    alt.datum.sat_curve_pts == alt.datum.max_sat
).transform_calculate(
    label_text='"Optimum " + datum.channel + " spend : " + format(datum.spend, "$,.2f")'
)

# Optimal Labels
opt_labels = opt_points.mark_text(
    align='left',
    dx=10,       # Shift the label 5 pixels to the right
    dy=5
).encode(
    x='spend:Q',
    y='sat_curve_pts:Q',
    text='label_text:N',
    tooltip=[
      alt.Tooltip("channel", title='Channel'),
      alt.Tooltip("spend", title='Spend', format='$.2f'),
      alt.Tooltip("sat_curve_pts", title='Marginal ROI', format='$.2f')
    ]
)

# 4.3 Current Points
current_points = alt.Chart(curr_point_df).mark_point(
    filled=True,
    shape='diamond',
    size=200
).encode(
    x='spend',
    y='sat_curve_pts',
    color='channel:N',
    tooltip=[
      alt.Tooltip("channel", title='Channel'),
      alt.Tooltip("spend", title='Spend', format='$.2f'),
      alt.Tooltip("sat_curve_pts", title='Marginal ROI', format='$.2f')
    ]
).transform_calculate(
    label_text='"Current " + datum.channel + " spend : " + format(datum.spend, "$,.2f")'
)

# Current Labels
current_labels = current_points.mark_text(
    align='left',
    dx=-75,       # Shift the label 5 pixels to the left
    dy=-10
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
            tooltip=[
              alt.Tooltip("channel", title='Channel'),
              alt.Tooltip("spend", title='Spend', format='$.2f'),
              alt.Tooltip("sat_curve_pts", title='Marginal ROI', format='$.2f')
            ]
        )
    )

fb_point = make_slider_point(base_chart, 'facebook', fb_budget)
gg_point = make_slider_point(base_chart, 'google_ads', gg_budget)
tt_point = make_slider_point(base_chart, 'tiktok', tt_budget)

# Don't forget to call the created items!!!
budget_tool = (curves + opt_points + opt_labels + current_points + current_labels + fb_point + gg_point + tt_point).properties(title='Budget Scenario Visualizer').interactive()

budget_tool