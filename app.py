import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import re

# Load preprocessed full dataset (already combined and cleaned outside this app)
combined_df = pd.read_csv("Combined_Document_Review_Data.csv")
combined_df['year_month'] = pd.to_datetime(combined_df['local_date'], errors='coerce').dt.to_period('M').astype(str)

# Extract states from notes
combined_df['states'] = combined_df['notes'].fillna('').apply(lambda x: re.findall(r'\b[A-Z]{2}\b', x))
combined_df = combined_df.explode('states')

# Add is_billable boolean
combined_df['is_billable'] = combined_df['billable'].astype(str).str.lower().isin(['yes', 'true', '1'])

# Create initial aggregations
def aggregate_data(filtered_df):
    hours_by_month = filtered_df.groupby('year_month')['hours'].sum().reset_index()
    docs_by_month = filtered_df.groupby('year_month')['#of_documents_coded'].sum().reset_index()
    review_by_type_month = filtered_df.groupby(['year_month', 'affirmative_or_defensive'])['hours'].sum().reset_index()
    cases_by_month = filtered_df.groupby(['year_month', 'jobcode_3'])['hours'].sum().reset_index()
    states_by_month = filtered_df.groupby(['year_month', 'states'])['hours'].sum().reset_index()
    billable_stats = filtered_df.groupby('year_month').agg(
        total_hours=('hours', 'sum'),
        billable_hours=('is_billable', lambda x: filtered_df.loc[x.index, 'hours'][x].sum())
    ).reset_index()
    billable_stats['billable_pct'] = (billable_stats['billable_hours'] / billable_stats['total_hours']) * 100

    return hours_by_month, docs_by_month, review_by_type_month, cases_by_month, states_by_month, billable_stats

# App setup
app = dash.Dash(__name__)

years = sorted(combined_df['year_month'].str[:4].unique())

app.layout = html.Div([
    html.H1("InSource Document Review Dashboard", style={'textAlign': 'center'}),

    html.Div([
        html.Label("Select Year:"),
        dcc.Dropdown(id='year-dropdown', options=[{'label': y, 'value': y} for y in years], value=years[-1])
    ], style={'width': '25%', 'margin': 'auto'}),

    dcc.Graph(id='hours-month'),
    dcc.Graph(id='docs-month'),
    dcc.Graph(id='review-type'),
    dcc.Graph(id='cases-over-time'),
    dcc.Graph(id='jurisdictions'),
    dcc.Graph(id='billable-pct')
])

@app.callback(
    [Output('hours-month', 'figure'),
     Output('docs-month', 'figure'),
     Output('review-type', 'figure'),
     Output('cases-over-time', 'figure'),
     Output('jurisdictions', 'figure'),
     Output('billable-pct', 'figure')],
    [Input('year-dropdown', 'value')]
)
def update_graphs(selected_year):
    filtered_df = combined_df[combined_df['year_month'].str.startswith(selected_year)]
    hours_by_month, docs_by_month, review_by_type_month, cases_by_month, states_by_month, billable_stats = aggregate_data(filtered_df)

    fig1 = px.bar(hours_by_month, x='year_month', y='hours', title='Total Hours Worked Per Month')
    fig2 = px.line(docs_by_month, x='year_month', y='#of_documents_coded', title='Documents Reviewed Per Month')
    fig3 = px.bar(review_by_type_month, x='year_month', y='hours', color='affirmative_or_defensive', title='Review Type by Volume')
    fig4 = px.bar(cases_by_month, x='year_month', y='hours', color='jobcode_3', title='Cases Worked On')
    fig5 = px.bar(states_by_month, x='year_month', y='hours', color='states', title='Jurisdictions Worked On')
    fig6 = px.line(billable_stats, x='year_month', y='billable_pct', title='Billable Time Percentage')

    return fig1, fig2, fig3, fig4, fig5, fig6

# Note: app.run disabled in restricted environments
#if __name__ == '__main__':
#    app.run(debug=False)
