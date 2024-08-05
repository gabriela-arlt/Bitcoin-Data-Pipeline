import json
import os
import psycopg2

# Database connection parameters
DATABASE_URL = os.getenv('railway_url')

def save_bitcoin_news(event, context):
    try:
        # Connect to the database
        conn = psycopg2.connect(DATABASE_URL)
        print("Connected to the database successfully.")
        
        # Parse the incoming event
        try:
            # If `body` is a JSON string, parse it
            #data = json.loads(event['body'])
            data = json.loads(event['responsePayload']['body'])
            print("Data parsed successfully:", data)
        except Exception as e:
            print(f'Error parsing JSON data: {e}')
            return {
                'statusCode': 400,
                'body': json.dumps(f'Error parsing JSON data: {e}')
            }
        
        # Insert the Bitcoin news into the database
        try:
            cursor = conn.cursor()
            for item in data:
                # Debug print each item
                print("Processing item:", item)
                
                # Check if 'date' and 'title' exist in the item
                if 'date' in item and 'title' in item:
                    cursor.execute('''
                        INSERT INTO gabi_news (date, title)
                        VALUES (%s, %s)
                        ON CONFLICT (date, title) DO NOTHING
                    ''', (item['date'], item['title']))
                else:
                    print(f"Missing 'date' or 'title' in item: {item}")
            
            conn.commit()
            cursor.close()
            print("Data inserted successfully into the database.")
        except Exception as e:
            print(f'Error inserting Bitcoin data: {e}')
            conn.rollback()
            return {
                'statusCode': 500,
                'body': json.dumps(f'Error inserting Bitcoin data: {e}')
            }
        
        # Close the connection
        conn.close()
        print("Database connection closed successfully.")
        
        return {
            'statusCode': 200,
            'body': json.dumps('Data inserted successfully')
        }
    except Exception as e:
        print(f'Error in save_bitcoin_news: {e}')
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {e}')
        }
