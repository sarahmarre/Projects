import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

colorscales = px.colors.named_colorscales()

# Load the dataset
df = pd.read_csv('data\sarahs_books.csv')

# Preprocess data
df['month read'] = pd.to_datetime(df['month read'], format='%m/%y')
irrelevant_columns = ['title', 'author_last', 'month read', 'month added']
relevant_columns = [col for col in df.columns if col not in irrelevant_columns]
genres_dummies = df['genre'].str.get_dummies(sep=',')
df = pd.concat([df, genres_dummies], axis=1)
df.drop(['genre', 'Audiobook'], axis=1, inplace=True)

# Initialize the Dash app
app = dash.Dash(__name__)
app.title = 'Book Analysis Dashboard'

# Define the app layout
app.layout = html.Div([
    html.H1('Book Analysis Dashboard'),
    dcc.Tabs([
        dcc.Tab(label='View Data', children=[
            html.Div([
                html.H2('Dataset'),
                dash.dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'name': i, 'id': i} for i in df.columns],
                    page_size=10
                )
            ])
        ]),
        dcc.Tab(label='Most Frequent Genres', children=[
            dcc.Graph(id='genre-bar-plot')
        ]),
        dcc.Tab(label='Book Length Distribution', children=[
            dcc.Graph(id='length-dist-plot')
        ]),
        dcc.Tab(label='Books Read Over Time', children=[
            dcc.Graph(id='books-over-time-line-plot')
        ])
    ])
])

@app.callback(
    Output('genre-bar-plot', 'figure'),
    Input('genre-bar-plot', 'id')
)
def update_genre_bar_plot(_):
    genre_columns = df.columns[10:-1]
    genre_counts = df[genre_columns].sum().sort_values(ascending=False)
    top_10_genres = genre_counts.head(10).sort_values(ascending=True)
    fig = px.bar(
        x=top_10_genres.values,
        y=top_10_genres.head(10).index,
        orientation='h',
        labels={'x': 'Count', 'y': 'Genre'},
        title='Top 10 Most Frequent Genres',
        color=top_10_genres.head(10).values,
        color_continuous_scale='ylgnbu'
    )
    
    fig.update_layout(xaxis_title='Count', yaxis_title='Genre')
    return fig

@app.callback(
    Output('length-dist-plot', 'figure'),
    Input('length-dist-plot', 'id')
)
def update_length_dist_plot(_):
    fig = px.histogram(
        df,
        x='length (pages)',
        nbins=30,
        title='Distribution of Book Lengths',
    )
    fig.update_traces(marker_color='olivedrab')

    fig.update_layout(xaxis_title='Length (pages)', yaxis_title='Count')
    return fig.to_dict()  # Convert the figure to a dictionary

@app.callback(
    Output('books-over-time-line-plot', 'figure'),
    Input('books-over-time-line-plot', 'id')
)
def update_books_over_time_line_plot(_):
    # Group data by month read and count the number of books per month
    books_per_month = df.groupby(df['month read'].dt.to_period('M')).size().reset_index(name='count')
    books_per_month['month read'] = books_per_month['month read'].dt.strftime('%Y-%m')

    # Create the line plot using Plotly Express
    fig = px.line(
        books_per_month,
        x='month read',
        y='count',
        title='Number of Books Read Over Time'
    )
    fig.update_traces(marker_color='orangered')

    # Update layout of the plot
    fig.update_layout(
        xaxis_title='Month',
        yaxis_title='Number of Books Read',
        xaxis=dict(tickformat='%Y-%m')
    )

    return fig.to_dict()  # Ensure the figure is JSON serializable

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
