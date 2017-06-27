# This Python file uses the following encoding: utf-8

"""
The MIT License (MIT)

Copyright 2017, Jaime Soto and Simverge Software LLC

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

wikiquote-tweet-awslambda
A library to find and tweet random inspirational quotes from wikiquote.org.

"""

import json
import os
import logging
import random
import re
import requests
import tweepy

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# TODO Use Unicode escape sequences for non-ASCII characters
FORBIDDEN_SECTIONS = frozenset([
	'references',
	'see also',
	'external links',
	'referencias',
	'enlaces externos',
	'véase también',
	'temas relacionados',
	'veja também'
])

MAX_TWEET_LENGTH = 140
MAX_TCO_URL_LENGTH = 20

def build_tweetable_quote(message, author, theme):
	"""
	Builds a quote suitable for tweeting.

	A quote is considered tweetable if its length does not exceed MAX_TWEET_LENGTH.
	The message and author strings are stripped of unnecessary whitespace
	and wikitext markup. The theme is added as a hashtag if its inclusion
	does not cause the quote length to exceed MAX_TWEET_LENGTH. The theme
	hashtag is inlined if present in the message body or appended as a suffix if not.

	Parameters
	----------
	message : str
		The quote message as parsed from wikitext
	author : str
		The quote author as parsed from wikitext
	theme: str
		The theme of the quote, typically the title of the source page

	Returns
	-------
	str
		A quote formatted for tweeting or None if it could not be built

	"""

	# Strip special characters from message and author
	# TODO Consolidate and pre-compile these regex patterns
	# TODO Use Unicode escape sequences for non-ASCII characters
	message = re.sub(r'(<.*?>)','', message) # Remove all characters between < and >
	message = re.sub('\[.\:', '', message) # Remove all characters between [ and :
	message = re.sub('\|.\]', '', message) # Remove all characters between | and ]
	message = re.sub('[\[\]\"«»“”#=]', '', message) # Remove []"«»“”#
	message = re.sub('[\']{2,}', '', message) # Remove two or more consecutive '
	message = message.strip()

	if message and message[len(message) - 1] not in ['.', '?', '!']:
		message += '.'

	author = re.sub(r'(<.*?>)','', author) # Remove all characters between < and >
	author = re.sub('\[.\:', '', author) # Remove all characters between [ and :
	author = re.sub('\|.\]', '', author) # Remove all characters between | and ]
	author = re.sub('[\[\]#=]', '', author) # Remove []"«»“”#
	author = re.sub('[\']{2,}', '', author)
	author = author.strip()

	quote = None

	if len(message) + len(author) < MAX_TWEET_LENGTH:
		quote = message + ' ' + author

		hashtag = theme.lower();
		i = quote.lower().find(hashtag)

		# Embed the theme as a hashtag if present in the quote
		if i >= 0 and len(quote) < MAX_TWEET_LENGTH:
			quote = quote[:i] + '#' + quote[i:]
		# Add the hashtag as a suffix if it cannot be inlined
		else:
			hashtag = re.sub('[\(\)]', '', hashtag)
			hashtag = re.sub('\s', '-', hashtag)

			if len(quote) + len(hashtag) < MAX_TWEET_LENGTH - 1:
				quote += ' #' + hashtag

	return quote if quote and len(quote) <= MAX_TWEET_LENGTH else None

def find_quote_from_wikitext(wikitext, theme):
	"""
	Randomly finds a tweetable quote from the provided wikitext.

	Parameters
	----------
	wikitext : str
		The wikitext to search for a quote
	theme : str
		The theme of the wikitext quotes, typically the title of the source page

	Returns
	-------
	str
		A random tweetable quote from the wikitext or None if none could be found
	"""

	quote = None
	quotes = wikitext.split('*')

	# Search for a random line until we find an empty one
	# Merge the previous and next lines to form the quote
	# Add the title page as the hashtag

	indices = [i for i in range(len(quotes))]

	while indices and not quote:
		r = random.randint(0, len(indices) - 1)
		i = indices[r]

		if quotes[i].strip() == '' and i > 0 and i < len(quotes) - 2:
			quote = build_tweetable_quote(quotes[i - 1], quotes[i + 1], theme)

		# Delete the processed index to avoid finding it again
		del(indices[r])

	return quote

def find_quote_from_section(api, page_id, section_id):
	""" 
	Randomly finds a tweetable quote from a Wikiquote's page section.

	Parameters
	----------
	api : str
		The wikiquote.org API's URL
	page_id : int
		The Wikiquote page ID
	section_id : int
		The index of the section to search

	Returns
	-------
	str
		A random tweetable quote from the section or None if none could be found
	"""
	
	payload = {
		'format' : 'json',
		'action' : 'parse',
		'prop' : 'wikitext',
		'section' : section_id,
		'pageid' : page_id
	}

	json = requests.post(api, data = payload).json()
	return find_quote_from_wikitext(json['parse']['wikitext']['*'], json['parse']['title'])

def find_quote_from_page(api, page_id):
	""" 
	Randomly finds a tweetable quote from the sections Wikiquote's page.

	Searches for a quote from a random section that is not in FORBIDDEN_SECTIONS.

	This function currently does not check the page itself for quotes.
	This behavior yields very few results in less-structured Wikiquote
	pages with few or no sections such as those found in the Portuguese
	site (pt.wikiquotes.org).

	Parameters
	----------
	api : str
		The wikiquote.org API's URL
	page_id : int
		The Wikiquote page ID

	Returns
	-------
	str
		A random tweetable quote from the page sections or None if none could be found

	"""

	payload = {
		'format' : 'json',
		'action' : 'parse',
		'prop' : 'sections',
		'pageid' : page_id
	}

	json = requests.post(api, data = payload).json()
	sections = json['parse']['sections']
	quote = None

	while sections and quote is None:
		r = random.randint(0, len(sections) - 1)

		if sections[r]['line'].lower() not in FORBIDDEN_SECTIONS and sections[r]['index']:
			quote = find_quote_from_section(api, page_id, sections[r]['index'])

		# Delete the processed section to avoid finding it again
		del(sections[r])

	# TODO Search page contents if no sections are found
	# The pt.wikiquote.org is notorious for lacking sections 
	"""
	if not quote:
		payload = {
			'format' : 'json',
			'action' : 'parse',
			'prop' : 'wikitext',
			'pageid' : page_id
		}
		
		json = requests.post(api, data = payload).json()
		logger.info(json['parse']['wikitext']['*'])
		quote = find_quote_from_wikitext(json['parse']['wikitext']['*'], json['parse']['title'])
	"""

	return quote

def find_quote_from_category(category, language='en'):
	""" 
	Randomly finds a tweetable quote from a Wikiquote's category.

	Searches for a quote from a random page belonging to the provided category
	in the provided language. The category and language are not validated
	by this function, so incorrect values may yield errors relayed from
	the wikiquotes.org API.

	Parameters
	----------
	category : str
		The Wikiquote category to search
	language : str
		The Wikiquote language site to search, as lowercase ISO-639-1

	Returns
	-------
	str
		A random tweetable quote from a page in the category or None if none could be found

	"""

	# TODO Validate language
	api = 'https://' + language + '.wikiquote.org/w/api.php'

	payload = {
		'format' : 'json',
		'action' : 'query',
		'list' : 'categorymembers',
		'cmtitle' : 'Category:' + category,
		'cmprop' : 'ids|title',
		'cmnamespace' : '0',
		'cmtype' : 'file',
		'cmlimit' : '100',
		'cmsort' : 'timestamp',
		'cmdir' : 'newer'
	}

	json = requests.post(api, data = payload).json()
	pages = json['query']['categorymembers']

	quote = None
	theme = None
	
	while pages and quote is None:
		r = random.randint(0, len(pages) - 1)
		quote = find_quote_from_page(api, pages[r]['pageid'])

		if quote:
			theme = pages[r]['title']

		# Delete the processed page to avoid finding it again
		del(pages[r])

	return [quote, theme]

def find_image(keyword, language='en'):
	""" 
	Randomly finds an image related to a keyword in the specified language.

	Searches pixabay.com for an image based on the provided keyword and language.
	The keyword and language are not validated not sanitized so make sure they
	conform to the pixabay.com requirements for the 'q' and 'lang' parameters,
	respectively.
	
	An environment variable with the name PIXABAY_KEY must be set
	with a valid pixabay.com API key before calling this function.

	Environment
	-----------
	PIXABAY_KEY : str
		A pixabay.com API key

	Parameters
	----------
	keyword : str
		The keyword to search
	language : str
		The keyword's language

	Returns
	-------
	str
		The URL to a pixabay.com image that matches the keyword or None if none could be found

	"""

	api = 'https://pixabay.com/api'

	payload = {
		'q' : keyword,
		'lang' : language,
		'image_type' : 'photo',
		'safesearch' : 'true',
		'editors_choice' : 'true',
		'key' : os.environ['PIXABAY_KEY']
	}

	json = requests.get(api, params = payload).json()
	images = json["hits"]

	return random.choice(images)['webformatURL'] if images else None

def tweet_inspirational_quote(language='en'):
	""" 
	Tweets an inspirational quote in the specified language.

	Currently only English (en) and Spanish (es) are well tested and supported.
	Any language other than these two and Portuguese (pt) is automatically mapped
	to English.

	Randomly searches a category from wikiquotes.org in the provided language for
	a tweetable quote. In addition, this function searches for an image in pixabay.com
	that matches the theme of the quote.

	Environment variables with a valid temp directory and valid keys Twitter
	must be set before calling this function. See the Environment section
	for more details. See also environment requirements imposed by find_image.

	Environment
	-----------
	TEMP_DIRECTORY:
		The path to a temporary directory to download pixabay.com images. Assumed to be /tmp if omitted.
	TWITTER_CONSUMER_KEY
		The Twitter consumer key
	TWITTER_CONSUMER_SECRET
		The Twitter consumer secret
	TWITTER_ACCESS_TOKEN
		The Twitter access token
	TWITTER_ACCESS_SECRET
		The Twitter access secret

	Parameters
	----------
	language : str
		The tweet's language

	Returns
	-------
	Status
		The Status object returned by tweepy or None if no tweet was posted
	"""

	categories = {
		'en' : 'Virtues',
		'es' : 'Virtudes',
		'pt' : 'Sentimentos'
	}

	if language not in categories.keys():
		language = 'en'

	[message, theme] = find_quote_from_category(categories[language], language)

	if message and theme:
		quote_url = 'https://' + language + '.wikiquote.org/' + theme

		if len(message) < MAX_TWEET_LENGTH - MAX_TCO_URL_LENGTH:
			message += ' ' + quote_url

		logger.info('Tweeting message (' + str(len(message)) + 'chars): ' + message)
		
		oauth = tweepy.OAuthHandler(os.environ['TWITTER_CONSUMER_KEY'], os.environ['TWITTER_CONSUMER_SECRET'])
		oauth.set_access_token(os.environ['TWITTER_ACCESS_TOKEN'], os.environ['TWITTER_ACCESS_SECRET'])
		twitter = tweepy.API(oauth)

		# TODO Gracefully handle tweepy.error.TweepError: [{'code': 187, 'message': 'Status is a duplicate.'}]
		if twitter:
			image_url = find_image(theme, language)

			if image_url:
				logger.info('Found image for theme ' + theme + ' in language ' + language)

				temp = os.environ['TEMP_DIRECTORY'] if os.getenv('TEMP_DIRECTORY') else '/tmp'
				image_path = temp + '/' + image_url.split('/')[-1]
				response = requests.get(image_url, stream = True)

				with open(image_path, 'wb') as image:
					for chunk in response.iter_content(chunk_size = 1024):
						if chunk:
							image.write(chunk)

				with open(image_path, 'rb') as image:
					logger.info('Found image file at ' + image_path)
					status = twitter.update_with_media(filename = image_path, status = message, file = image)

				os.remove(image_path)

			else:
				logger.warn('Could not find image for theme ' + theme + ' in language ' + language)
				status = twitter.update_status(status = message)

		else:
			logger.error('Could not authorize Twitter account but retrieved this quote for you')
			logger.info(message)

	return status

def lambda_handler(event, context):
	""" 
	Handles an AWS IoT button event by tweeting an inspirational quote.

	Currently tweets a quote in English on a SINGLE pulse, in Spanish on a DOUBLE pulse,
	and in Portuguese on a LONG pulse.

	Refer to tweet_inspirational_quote and find_image for environment requirements.

	Refer to AWS Lambda and AWS IoT button documentation for more information
	about the event and context parameters.

	Returns
	-------
	str
		The URL to the tweet or None if post was unsuccessful
	"""

	logging.info('Received event: ' + json.dumps(event))
	languages = { 'SINGLE' : 'en', 'DOUBLE' : 'es', 'LONG' : 'pt' }
	logging.info('Language: ' + languages[event['clickType']])
	status = tweet_inspirational_quote(languages[event['clickType']])
	tweet = None

	if status:
		tweet = 'https://twitter.com/' + status.user.id_str + '/status/' + status.id_str

	return tweet