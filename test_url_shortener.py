import pytest
import pymongo
import random
import time
from unittest.mock import patch, MagicMock
from url_shortener import generate_shortcode, minify_url, expand_url, is_valid_url, output_minified_url


@pytest.fixture
def mock_mongo_collection():
    with patch('url_shortener.connect_to_mongodb') as mock_connect:
        mock_collection = MagicMock()
        mock_connect.return_value = mock_collection
        yield mock_collection


def test_generate_shortcode():
    length = 6
    shortcode = generate_shortcode(length)
    assert len(shortcode) == length


def test_is_valid_url():
    assert is_valid_url("http://example.com")
    assert is_valid_url("https://example.com/11212?param=true")
    assert not is_valid_url("JUST_A_STRING")
    assert not is_valid_url("http://")


def test_minify_url_existing(mock_mongo_collection):
    url = "http://example.com"
    expiry_time = 3600
    shortcode = "abc123"
    mock_mongo_collection.find_one.return_value = {
        "shortcode": shortcode,
        "url": url,
        "expiration_timestamp": time.time() + 3600
    }
    minified_url = minify_url(url, expiry_time)
    assert minified_url == output_minified_url(shortcode)
    mock_mongo_collection.find_one.assert_called_once()


def test_expand_url_not_found(mock_mongo_collection):
    shortcode = "abc123"
    mock_mongo_collection.find_one.return_value = None
    expanded_url = expand_url(shortcode)
    assert expanded_url == "Shortened URL not found."
    mock_mongo_collection.find_one.assert_called_once_with({"shortcode": shortcode})


def test_expand_url_expired(mock_mongo_collection):
    shortcode = "abc123"
    mock_mongo_collection.find_one.return_value = {
        "shortcode": shortcode,
        "url": "http://example.com",
        "expiration_timestamp": time.time() - 60
    }
    expanded_url = expand_url(shortcode)
    assert expanded_url == "Shortened URL has expired."
    mock_mongo_collection.find_one.assert_called_once_with({"shortcode": shortcode})


def test_expand_url_found(mock_mongo_collection):
    shortcode = "abc123"
    url = "http://example.com"
    mock_mongo_collection.find_one.return_value = {
        "shortcode": shortcode,
        "url": url,
        "expiration_timestamp": time.time() + 3600
    }
    expanded_url = expand_url(shortcode)
    assert expanded_url == url
    mock_mongo_collection.find_one.assert_called_once_with({"shortcode": shortcode})