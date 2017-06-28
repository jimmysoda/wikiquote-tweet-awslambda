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

This code is released using the MIT license. See [LICENSE](LICENSE) for more details.

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

Setting the `PHONE_NUMBER` environment variable and allowing `sns:Publish`
via [AWS IAM](https://console.aws.amazon.com/iam) for the lambda function
enables sending a notification SMS with the payload sent by the button
and the URL to the resulting tweet.

The following function policy copied from the IoT example lambda functions
allows limits [AWS SNS](https://console.aws.amazon.com/sns) publish to SMS but not topics or endpoints.

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "sns:Publish"
            ],
            "Resource": [
                "*"
            ]
        },
        {
            "Effect": "Deny",
            "Action": [
                "sns:Publish"
            ],
            "Resource": [
                "arn:aws:sns:*:*:*"
            ]
        }
    ]
}
```

Dependencies
------------
- Python 3.x: tested on v3.6.1
- [_requests_ HTTP library](http://docs.python-requests.org/en/master/): tested
  with v2.18.1
  or later
- [_tweepy_ Twitter API wrapper](http://www.tweepy.org/): tested with v3.5.0

The _requests_ and _tweepy_ libraries need to be uploaded to AWS Lambda in a
[deployment package](http://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html). Remember to install these dependencies
via pip [at the root of the package](https://stackoverflow.com/a/40741925) and
to set the value of the [*Handler* field in AWS Lambda](https://stackoverflow.com/a/35355800)
to *wikiquote_tweet_awslambda.lambda_handler*.

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
- Thanks to @onema for the [lambda-tweet](https://github.com/onema/lambda-tweet)
AWS Lambda application that I used as a reference on how to use tweepy
- Thanks to @natetyles for the [wikiquotes-api](https://github.com/natetyler/wikiquotes-api)
repository that I used as a reference on how to call the wikiquote.org API and parse
its response
- Thanks to @dev-techmoe for the [tweepy status structure gist](https://gist.github.com/dev-techmoe/ef676cdd03ac47ac503e856282077bf2)
that I used as a reference to parse the results from tweepy
