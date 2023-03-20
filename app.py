import requests
from flask import Flask, jsonify, request
# from flask_cors import CORS
from libgen_api import LibgenSearch

app = Flask(__name__)
# CORS(app, resources={r"/api/*": {"origins": "*"}})


@app.route('/')
def index():
    return "Welcome To API"


@app.route('/api/_v1/search')
def search():
    global results
    title = request.args.get('title', type=str)
    author = request.args.get('author', type=str)
    if not title and not author:
        return jsonify(
            {
                "status": 0,
                "message": "Not found"
            }
        ), 404
    s = LibgenSearch()
    if title:
        results = s.search_title(title)
    if author:
        results = s.search_author(author)

    # for result in results:
    #     item = getAdditionInfo(result['Title'])
    #     result['Images'] = item['images']
    #     result['Description'] = item['description']
        # url = result['Mirror_1']
        # # url1 = result['Mirror_2']
        # imgUrl = getImageUrl(url, result['ID'])
        # result['cover'] = imgUrl
        # description = getDescription(result['Title'])
        # result['description'] = description

    return jsonify(
        {
            "status": 1,
            "message": "Success",
            "data": results
        }
    ), 200


@app.route('/api/_v1/filter')
def filter_book_addition():
    global results
    title = request.args.get('title', type=str)
    author = request.args.get('author', type=str)
    language = request.args.get('language', type=str)
    extension = request.args.get('extension', type=str)
    year = request.args.get('extension', type=str)
    filter_book = {}
    if not title or not author:
        return jsonify(
            {
                "status": 0,
                "message": "Not found"
            }
        ), 404
    s = LibgenSearch()
    if not language and not extension and not year:
        return jsonify(
            {
                "status": 0,
                "message": "Not found"
            }
        ), 404
    if language:
        filter_book["Language"] = language
    if extension:
        filter_book["Extension"] = extension
    if year:
        filter_book["Year"] = year
    if title:
        results = s.search_title_filtered(title, filter_book, exact_match=True)
    if author:
        results = s.search_author_filtered(author, filter_book, exact_match=True)
    return jsonify(
        {
            "status": 1,
            "message": "Success",
            "data": results
        }
    ), 200


@app.route('/api/_v1/bookinfo')
def bookInfo():
    global results
    title = request.args.get('title', type=str)
    author = request.args.get('author', type=str)
    if not title and not author:
        return jsonify(
            {
                "status": 0,
                "message": "Not found"
            }
        ), 404
    s = LibgenSearch()
    if title:
        results = s.search_title(title)
    if author:
        results = s.search_author(author)
    item_to_download = results[0]
    # url = item_to_download['Mirror_1']
    # # url1 = result['Mirror_2']
    # imgUrl = getImageUrl(url, item_to_download['ID'])
    # item_to_download['cover'] = imgUrl
    # description = getDescription(item_to_download['Title'])
    # item_to_download['description'] = description
    item = getAdditionInfo(item_to_download['Title'])
    item_to_download['images'] = item['images']
    item_to_download['description'] = item['description']
    download_links = s.resolve_download_links(item_to_download)
    item_to_download['download_link'] = download_links
    return jsonify(
        {
            "status": 1,
            "message": "Success",
            "data": item_to_download
        }
    ), 200


def getAdditionInfo(name):
    item = {}
    query_link = 'https://www.googleapis.com/books/v1/volumes?q=' + name
    res_json = requests.get(query_link).json()
    for i in res_json['items']:
        if 'description' not in i['volumeInfo']:
            continue
        item['description'] = i['volumeInfo']['description']
        if 'imageLinks' not in i['volumeInfo']:
            continue
        item['images'] = i['volumeInfo']['imageLinks']
        break
    return item


# def getImageUrl(url, id):
#     imageUrl = ''
#     domain = url.split('/main/')[0]
#     count = countDigit(int(id))
#     if count == 3:
#         imageUrl = domain + '/covers/0/' + url.split('/main/')[1].lower() + '-d.jpg'
#     else:
#         imageUrl = domain + '/covers/' + (str(id)[:(count - 3)] + '000') + '/' + url.split('/main/')[
#             1].lower() + '-d.jpg'
#     # f = requests.get(url).text
#     # soup = BeautifulSoup(f, 'html.parser')
#     # for imgtag in soup.find_all('img'):
#     #     imageUrl = domain + imgtag['src']
#     return imageUrl
#
#
# # def getDescription(url):
# #     description = ''
# #     f = requests.get(url).text
# #     soup = BeautifulSoup(f, 'html.parser')
# #     last_td = soup.findAll('td')[-1]
# #     return last_td.get_text()
#
# def getDescription(name):
#     description = ''
#     query_link = 'https://www.googleapis.com/books/v1/volumes?q=' + name
#     res_json = requests.get(query_link).json()
#     for i in res_json['items']:
#         if 'description' not in i['volumeInfo']:
#             continue
#         description = i['volumeInfo']['description']
#         break
#     return description


# def countDigit(n):
#     count = 0
#     while n != 0:
#         n //= 10
#         count += 1
#     return count


if __name__ == '__main__':
    app.run(debug=True)
