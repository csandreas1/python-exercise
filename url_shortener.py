import pymongo, random, time, argparse
from urllib.parse import urlparse

MONGODB_URL = "mongodb://root:example@mongodb:27017/"
DATABASE_NAME = "url_shortener"
COLLECTION_NAME = "urls"


def connect_to_mongodb():
    client = pymongo.MongoClient(MONGODB_URL)
    return client[DATABASE_NAME][COLLECTION_NAME]


def generate_shortcode(length):
    # Generate MD5 hash of the URL
    characters = "abcdefghijklmnopqrstuv-+wxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string


def expand_url(shortcode):
    collection = connect_to_mongodb()
    url_data = collection.find_one({"shortcode": shortcode})
    if url_data:
        if url_data['expiration_timestamp'] > time.time():
            return url_data['url']
        else:
            return "Shortened URL has expired."
    else:
        return "Shortened URL not found."


def output_minified_url(shortcode):
    return f"https://py.sh/" + shortcode


def minify_url(url, expiry_time):
    collection = connect_to_mongodb()
    shortcode = generate_shortcode(6)

    query = {"url": url, "expiration_timestamp": {"$gt": time.time()}}
    existing_url = collection.find_one(query)

    if existing_url:
        return output_minified_url(existing_url["shortcode"])
    else:
        collection.insert_one({
            "shortcode": shortcode,
            "url": url,
            "expiration_timestamp": time.time() + expiry_time
        })
    return output_minified_url(shortcode)


def is_valid_url(url):
    try:
        result = urlparse(url)
        # Check if the URL has a valid scheme and netloc (domain)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def main():
    parser = argparse.ArgumentParser(description="URL Shortener Tool")
    parser.add_argument("--minify", help="Minify (shorten) a URL")
    parser.add_argument("--expand", help="Expand (retrieve original) a shortened URL")
    args = parser.parse_args()

    if not args.minify and not args.expand:
        print('Please provide required arguments. make help for more info')
        return

    if args.minify and is_valid_url(args.minify):
        minified_url = minify_url(args.minify, 3600)  # Expiry time set to 1 hour
        print(minified_url)
    elif args.expand and is_valid_url(args.expand):
        original_url = expand_url(args.expand.split('/')[-1])
        print(original_url)


if __name__ == "__main__":
    main()
