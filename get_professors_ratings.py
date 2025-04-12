from bs4 import BeautifulSoup
import requests
from flask import Flask, request, jsonify
from urllib.parse import quote_plus

app = Flask(__name__)

@app.route('/professor', methods=['GET'])
def get_professor_info():
    name = request.args.get('name')
    if not name:
        return jsonify({'error': 'Missing professor name'}), 400


    base_search_url = "https://www.ratemyprofessors.com/search/professors/1967?q="
    search_url = base_search_url + quote_plus(name)


    data = get_professor_info(search_url)
    
    if not data:
        return jsonify({'error': 'Professor not found or could not fetch data'}), 404

    return jsonify(data)

professor_ratings = {
    "overall_rating": "",
    "difficulty": "",
    "would_take_again": "",
    "ratings_quantity": "",
}

def get_professor_info(url):
    rmp_soup = parse_url(url)
    if rmp_soup:
        professor_data = rmp_soup.find_all("a")[1]
        get_overall_rating(professor_data)
        get_difficulty_and_would_take_again(professor_data)
        return professor_ratings

def get_difficulty_and_would_take_again(card):
    
    difficulty_data = card.find("div")
    difficulty_data = difficulty_data.select("div[class*='TeacherCard__CardInfo']")
    feedback = difficulty_data[0].find_all("div", class_="CardFeedback__CardFeedbackNumber-lq6nix-2")
    
    if len(feedback) >= 2:
        would_take_again = feedback[0].get_text(strip=True)
        difficulty = feedback[1].get_text(strip=True)
        professor_ratings["would_take_again"] = would_take_again
        professor_ratings["difficulty"] = difficulty

def get_overall_rating(rmp_soup):
    overall_rating_data = rmp_soup.find("div").find_all("div")[3:5]
    professor_ratings["overall_rating"] = overall_rating_data[0].text
    professor_ratings["ratings_quantity"] = overall_rating_data[1].text

def parse_url(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        return soup
    else:
        print("Failed to fetch:", response.status_code)
        return None

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)

