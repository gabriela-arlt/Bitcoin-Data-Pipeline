import os
import psycopg2
import json

def save_bitcoin_data(event, context):
    Database_URL = os.getenv('railway_url')
    conn = None  # Initialize conn to None
    
    try:
        if not Database_URL:
            raise ValueError("Database_URL environment variable not set")
        
        print(f"Connecting to database using URL: {Database_URL}")
        
        # Connect to the database
        conn = psycopg2.connect(Database_URL)
        cursor = conn.cursor()
        
        # Print the incoming event body for debugging
        #print(f"Incoming event body: {event['body']}")
        
        # Parse the incoming event
        #data = json.loads(event['body'])

        data = json.loads(event['responsePayload']['body'])
        
        for date, values in data.items():
            cursor.execute('''
                INSERT INTO gabi_api (Date, Open, High, Low, Close, Volume)
                Values(%s, %s, %s, %s, %s, %s)
                ON CONFLICT (Date) DO NOTHING
                ''', (date, values['1. open'], values['2. high'], values['3. low'], values['4. close'], values['5. volume']))
        
        conn.commit()
        cursor.close()
        return {
            'statusCode': 200,
            'body': json.dumps('Successssssssss')
        }
    except json.JSONDecodeError as e:
        print(f'JSON decode error: {e}')
        return {
            'statusCode': 400,
            'body': json.dumps(f'JSON decode error: {e}')
        }
    except Exception as e:
        print(f'Error inserting Bitcoin data: {e}')
        if conn:
            conn.rollback()
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error inserting Bitcoin data: {e}')
        }
    finally:
        if conn:
            conn.close()