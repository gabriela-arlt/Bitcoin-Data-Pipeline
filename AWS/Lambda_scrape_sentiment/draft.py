# Example event and context for local testing
if __name__ == "__main__":
    event = {
        "responsePayload": {
            "body": '[{"date": "2024-06-07", "title": "Trying to get the best government you can", "neutral_score": 0.9997968077659607, "negative_score": 0.00010265030869049951, "positive_score": 0.00010059310443466529}]'
        }
    }
    context = {}
    result = save_bitcoin_news(event, context)
    print(result)