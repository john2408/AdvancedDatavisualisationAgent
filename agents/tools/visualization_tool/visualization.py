import pandas as pd
import altair as alt

# Data
data = [
  { "year_month": "2023-01", "total_registrations": 1450 },
  { "year_month": "2023-02", "total_registrations": 1620 },
  { "year_month": "2023-03", "total_registrations": 2150 },
  { "year_month": "2023-04", "total_registrations": 1890 },
  { "year_month": "2023-05", "total_registrations": 2300 },
  { "year_month": "2023-06", "total_registrations": 1950 },
  { "year_month": "2023-07", "total_registrations": 2100 },
  { "year_month": "2023-08", "total_registrations": 2200 },
  { "year_month": "2023-09", "total_registrations": 2400 },
  { "year_month": "2023-10", "total_registrations": 2500 },
  { "year_month": "2023-11", "total_registrations": 2600 },
  { "year_month": "2023-12", "total_registrations": 2700 }
]

df = pd.DataFrame(data)
df['year_month'] = pd.to_datetime(df['year_month'])
df['quarter'] = df['year_month'].dt.to_period('Q').astype(str)

# Create a chart with line segments colored by quarter
chart = alt.Chart(df).mark_line().encode(
    x=alt.X('year_month', title='Month', axis=alt.Axis(format='%b')),
    y=alt.Y('total_registrations', title='Total Registrations'),
    color=alt.Color('quarter', title='Quarter'),
    tooltip=[alt.Tooltip('year_month', title='Month', format='%Y-%m'), 'total_registrations']
).properties(
    title='Registrations by Quarter'
)

chart.save('two_toned_line_chart_09.json')
