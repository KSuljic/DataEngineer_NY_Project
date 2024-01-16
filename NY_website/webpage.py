import pymongo
from pymongo import MongoClient
from dash import dash, dcc, html, callback, Input, Output, State
from datetime import datetime

import plotly.express as px

# Connect to MongoDB using the service name from Docker Compose
client = MongoClient("mongodb://mongodb:27017/")
# client = pymongo.MongoClient("mongodb://localhost:27017/") # for running locally 

# Specify the MongoDB collection
db = client.NY_Project  # Replace 'ny_times' with your actual collection name
collection = db.ny_articles  # Replace 'your_collection_name' with your actual collection name



pipeline = [
    {
        '$group': {
            '_id': '$news_desk',
            # 'section_word_count': {'$sum': '$word_count'},
            'section_word_count': {'$avg': '$word_count'},
            'section_article_count': {'$sum': 1},
            'newest_articles': {
                '$push': {
                    'headline': '$headline',
                    'web_url': '$web_url',
                    'pub_date': '$pub_date'
                }
            }
        }
    },
    {
        '$group': {
            '_id': None,
            'average_word_count': {'$avg': '$section_word_count'},
            'total_article_count': {'$sum': '$section_article_count'},  
            'sections': {
                '$push': {
                    'section': '$_id',
                    'average_word_count': {'$avg': '$section_word_count'},
                    'article_count': '$section_article_count'
                }
            },
            'all_articles': {'$push': '$newest_articles'}
        }
    },
    {
        '$project': {
            'average_word_count': 1,
            'total_article_count': 1,
            'sections': 1,
            # Flatten the array of arrays
            'flattened_articles': {'$reduce': {
                'input': '$all_articles',
                'initialValue': [],
                'in': {'$concatArrays': ['$$value', '$$this']}
            }}
        }
    },
    {
        '$unwind': '$flattened_articles'
    },
    {
        '$sort': {'flattened_articles.pub_date': -1}
    },
    {
        '$limit': 5
    },
    {
        '$group': {
            '_id': '$_id',
            'average_word_count': {'$first': '$average_word_count'},
            'total_article_count': {'$first': '$total_article_count'},
            'sections': {'$first': '$sections'},
            'newest_articles': {'$push': '$flattened_articles'}
        }
    }
]


result = list(collection.aggregate(pipeline))


if result:
   # Extracting data from the 'result' for 'sections'
    sections_data = [    {'section': section['section'], 'count': section['article_count']} 
        for section in result[0]['sections']
    ]

    # # Save aggregated data into a new collection
    # aggregated_data_collection = db.ny_articles_aggregated_data
    # aggregated_data_collection.insert_one({
    #     'total_articles': sum(section['count'] for section in sections_data),
    #     'average_word_count': result[0]['average_word_count'],
    #     'sections': sections_data,
    #     'newest_articles': result[0]['newest_articles'],
    #     'timestamp': datetime.now()
    # })

    # # Extract total number of articles, average word count, sections with counts, and newest articles
    total_articles = result[0]["total_article_count"]
    average_word_count = result[0]["average_word_count"]
    sections = [section['section'] for section in result[0]['sections']]
    article_counts = [section['article_count'] for section in result[0]['sections']]
    newest_articles = result[0]['newest_articles']


    ## Figure
    # Extract the data for the scatter plot
    scatter_data = result[0]['sections']


# Create a scatter plot using Plotly Express
fig = px.scatter(
    scatter_data,
    x='article_count',
    y='average_word_count',
    text='section',
    labels={'article_count': 'Number of Articles', 'average_word_count': 'Average Word Count'},
    color='section',
    title='Number of Articles vs Average Word Count per Section',
    template='plotly_dark'
)

# Scatter plot showing number of articles vs average word count per section
scatter_plot = dcc.Graph(
    id='section-scatter-plot',
    figure=fig,
    config={'displayModeBar': False}  # Hide the interactive mode bar
)



# Initialize Dash app
app = dash.Dash(__name__)


# Define the layout
app.layout = html.Div(children=[
    html.H1(children='NY Times Article Statistics'),

    html.Div(children=f'Total articles: {total_articles}', style={'marginBottom': 20}),

    html.Div(children=f'The average word count is: {average_word_count:.2f}', style={'marginBottom': 20}),

    html.H2("5 Latest Articles:"),
    # Create a list of links to the 5 newest articles
    html.Ul([
        html.Li(html.A(article['headline']['main'], href=article['web_url']), style={'list-style-type': 'none'}) for article in newest_articles
    ]),

    # Search bar
    html.H2("Article Search"),
    dcc.Input(id='search-input', type='text', placeholder='Enter keywords...'),

    # Create a list of links to the articles based on the search results
    html.Ul(id='search-results'),

    
    html.H2("Scatter Plot: Number of Articles vs Average Word Count per Section"),
    scatter_plot,  # Add the scatter plot here

    html.H2("Articles per Section:"),

    # Create a list of sections and counts
    html.Ul([
        html.Li(f"{section}: {count} articles") for section, count in zip(sections, article_counts)
    ])

])

# Define callback to update search results
@app.callback(
    Output('search-results', 'children'),
    [Input('search-input', 'value')],
    prevent_initial_call=True
)
def update_search_results(search_query):
    # MongoDB query to find articles containing the search query in keywords
    search_pipeline = [
        {'$match': {'keywords.value': {'$regex': f'{search_query}', '$options': 'i'}}},
        {'$project': {'headline': '$headline.main', 'web_url': '$web_url', '_id': 0}},
        {'$limit': 5}
    ]

    search_results = list(collection.aggregate(search_pipeline))

    # Display search results as links
    result_links = [
        html.Li(html.A(result['headline'], href=result['web_url'])) for result in search_results
    ]

    return result_links

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
