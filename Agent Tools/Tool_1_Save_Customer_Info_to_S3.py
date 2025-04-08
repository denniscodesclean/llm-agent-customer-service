import json
import boto3

# Note here I used OpenAPI Schema to define the action group
# Here's guidance on output requirement: https://docs.aws.amazon.com/bedrock/latest/userguide/agents-lambda.html

def lambda_handler(event, context):
    # Print Log
    print("Received event:", json.dumps(event, indent=4))

    parameters = event.get('parameters', [])

    # Convert parameters to a dictionary
    param_dict = {param['name']: param['value'] for param in parameters}

    full_name = param_dict.get('full_name')
    gender = param_dict.get('gender')
    age = int(param_dict.get('age', 0)) if param_dict.get('age') is not None else 0
    activities = param_dict.get('activities', [])
    if isinstance(activities, str):
        activities = [activities]  # Convert it to a list with one element
    
    #activities = json.loads(param_dict.get('activities', '[]')) if isinstance(param_dict.get('activities'), str) else param_dict.get('activities', [])


    new_entry = {
        "full_name": full_name,
        "gender": gender,
        "age": age,
        "activities": activities
    }

    def store_info_to_s3(full_name='', gender='', age='', activities=''):

        s3_client = boto3.client('s3')
        bucket_name = 'customer-service-llm'
        object_key = 'customer_info/customer_info.json'

        try:
            # Check if file exists and read existing data
            response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
            existing_data = json.loads(response['Body'].read().decode('utf-8'))
            #print("Existing data:", existing_data)  # Debug log
        except s3_client.exceptions.NoSuchKey:
            # If file doesn't exist, initialize with empty customer list
            existing_data = {"customers": []}
        except Exception as e:
            print(f"Error reading from S3: {str(e)}")
            raise

        # Append new entry
        existing_data["customers"].append(new_entry)

        # Save updated data back to S3
        try:
            s3_client.put_object(
                Bucket=bucket_name,
                Key=object_key,
                Body=json.dumps(existing_data, indent=4),
                ContentType='application/json'
            )
        except Exception as e:
            print(f"Error writing to S3: {str(e)}")
            raise

    # Store to S3
    store_info_to_s3(full_name, gender, age, activities)

    response_body = {
        'application/json': {
            'body': "Lambda Function Successfully Invoked :)"
        }
    }

    action_response = {
        'actionGroup': event['actionGroup'],
        'apiPath': event['apiPath'],
        'httpMethod': event['httpMethod'],
        'httpStatusCode': 200,
        'responseBody': response_body
    }
    
    session_attributes = event['sessionAttributes']
    prompt_session_attributes = event['promptSessionAttributes']
    
    api_response = {
        'messageVersion': '1.0', 
        'response': action_response,
        'sessionAttributes': session_attributes,
        'promptSessionAttributes': prompt_session_attributes
    }
        
    return api_response