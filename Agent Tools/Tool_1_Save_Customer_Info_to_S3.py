import json
import boto3

def lambda_handler(event, context):
    agent = event['agent']
    actionGroup = event['actionGroup']
    function = event['function']
    parameters = event.get('parameters', [])

    # Print Log
    #print("Received event:", json.dumps(event, indent=4))

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

    def store_info_to_s3(full_name, gender, age, activities):

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


    if function == 'store_customer_info':
        store_info_to_s3(full_name, gender, age, activities)

    responseBody = {
        "TEXT": {
            "body": f"The function {function} was called successfully!"
        }
    }

    action_response = {
        'actionGroup': actionGroup,
        'function': function,
        'functionResponse': {
            'responseBody': responseBody
        }
    }

    dummy_function_response = {
        'response': action_response,
        'messageVersion': event['messageVersion']
    }
    
    print("Response:", dummy_function_response)
    
    return dummy_function_response
