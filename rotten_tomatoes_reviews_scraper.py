import pandas as pd
import requests
import pickle
from bs4 import BeautifulSoup
from time import time


# Get the movie details
movies = pd.read_excel('./movies_list.xlsx').to_dict('records')


# Start a requests session
s = requests.Session()


# Iterate over the movies
t0 = time()
#final_result = []
for m in movies[51:]:
    # Get the movie url from the rotten tomatoes api
    r = s.get('https://www.rottentomatoes.com/api/private/v2.0/search', params={'q': m['movie_name']})
    search_result = r.json()['movies']
    url = [i['url'] for i in search_result if i['name'] == m['movie_name'] and i['year'] == m['year']][0]

    # Get the number of pages of reviews
    url_reviews = 'https://www.rottentomatoes.com' + url + '/reviews'
    r = s.get(url_reviews, params={'type': 'user', 'page': 1})
    r.encoding = 'utf-8'
    soup = BeautifulSoup(r.text, 'lxml')
    pages = int(soup.select_one('.pageInfo').text[10:])

    # Iterate through the reviews pages
    reviews = []
    for p in range(min(20, pages)):
        r = s.get(url_reviews, params={'type': 'user', 'page': p})
        r.encoding = 'utf-8'
        tags = BeautifulSoup(r.text, 'lxml').select('.col-xs-16')
        for t in tags:
            rating = t.find('div', attrs={'class': 'scoreWrapper'}).span['class']
            review = t.find('div', attrs={'class': 'user_review'}).text
            reviews.append({'rating': rating, 'review': review})

    # Storing the results
    movie_result = {'reviews': reviews}
    movie_result.update(m)
    final_result.append(movie_result)
    print('{0} is done. Time taken so far is {1} mins.'.format(m['movie_name'], round((time() - t0) / 60, 1)))


# Deleting all reviews which don't have a rating and converting to a 5 point scale
for m in final_result:
    m['reviews'] = [{'review': r['review'], 'rating': int(r['rating'][0]) / 10}
                    for r in m['reviews'] if r['rating'][0].isnumeric()]


# Exporting the results
with open('movie_reviews.pickle', 'wb') as f:
    pickle.dump(final_result, f)
