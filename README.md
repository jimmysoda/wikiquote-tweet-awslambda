# wikiquote-tweet-awslambda
 An AWS Lambda to tweet a random quote from wikiquote.org.

Summary
-------

An AWS Lambda application written in Python 3.x to tweet a randomly-selected
inspirational quote from wikiquote.org with a matching image from pixabay.com.

Learn more about the AWS IoT button, i.e., the programmable Amazon Dash button,
at https://aws.amazon.com/iotbutton/.

Follow [@asTheQuoteSays](https://twitter.com/asTheQuoteSays) on Twitter for
a demo!

This code is released using the MIT license. See [LICENSE] for more details.

Requirements
------------
This lambda function retrieves Pixabay and Twitter API keys from environment
variables:

- `PIXABAY_KEY`: The Pixabay API key
- `TWITTER_CONSUMER_KEY`: The Twitter API consumer key
- `TWITTER_CONSUMER_SECRET`: The Twitter API consumer secret
- `TWITTER_ACCESS_TOKEN`: The Twitter API access token
- `TWITTER_ACCESS_SECRET`: The Twitter API access token secret

Visit https://pixabay.com/api/docs/ and https://apps.twitter.com/ for
instructions on how to obtain these keys.

Dependencies
------------
- Python 3.x: tested on v3.6.1
- [_requests_ HTTP library](http://docs.python-requests.org/en/master/): tested
  with v2.18.1
  or later
- [_tweepy_ Twitter API wrapper](http://www.tweepy.org/): tested with v3.5.0

Usage
-----
The AWS Lambda function (`lambda_handler`) calls the
`tweet_inspirational_quote` function with a different language depending
on the click type received in the `event` argument:

 Click Type | Language | Function Call
----------- |----------|--------------
`SINGLE` | English | `tweet_inspirational_quote('en')`
`DOUBLE` | Spanish | `tweet_inspirational_quote('es')`
`LONG` | Portuguese | `tweet_inspirational_quote('pt')`

Currently only English (`en`) and Spanish (`es`) are well tested and supported.
Any language other than these two and Portuguese (`pt`) is automatically mapped
to English.

Acknowledgements
----------------
- Thanks to @onema for his [lambda-tweet](https://github.com/onema/lambda-tweet)
AWS Lambda application that I used as a reference on how to use tweepy
- Thanks to @natetyles for his [wikiquotes-api](https://github.com/natetyler/wikiquotes-api)
that I used as a reference on how to call the wikiquote.org API and parse
its response


