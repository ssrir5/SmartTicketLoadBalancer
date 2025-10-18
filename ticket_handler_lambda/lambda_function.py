import json
import boto3
import os
import re
from boto3.dynamodb.conditions import Attr

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
bedrock = boto3.client('bedrock-runtime', region_name=os.environ.get('AWS_REGION', 'us-east-2'))

# Find DB Table Name 
table_name = os.environ.get('TABLE_NAME', 'Client_Ticket_Information')
ticket_table = dynamodb.Table(table_name)

# Bedrock model ID (adjust if you’re using a different one)
MODEL_ID = os.environ.get('BEDROCK_MODEL', 'us.anthropic.claude-3-5-sonnet-20240620-v1:0')

def lambda_handler(event, context):
    try:
        response = ticket_table.scan(
            FilterExpression=Attr('status').eq('New')
        )

        new_tickets = response.get('Items',[])

        if not new_tickets:
            return {'statusCode': 200, 'body': json.dumps('No new tickets found.')}
                
        processing_tickets = []

        for ticket in new_tickets:
            ticket_id = ticket['ticketId']

            # Send new tickets to LLM
            prompt = f""" You are a support assistant. Analyze the following tickets:
            Title: {ticket.get('title')}
            Description: {ticket.get('description')}
            Category: {ticket.get('category')}
            Suggest possible solutions based on previous ticket data or in general.
            Give a good summary of the ticket and its problem and paths to fix it.
            First return the priority level like this Priority: (number) The priority
            should range from 1-4 where 1 is Low and 4 is critical. nd then Difficulty: (number) 
            The difficulty should be 1-3 where 1 easy and 3 is hard and then give a 
            quick summary of the problem and how to fix it return these both like 
            this Summary: and Suggested Fix: Give me sentence structure not list
            Make sure all sentences are complete"""

            llm_response = bedrock.invoke_model(
                modelId=MODEL_ID,
                # accept='application/json',
                # contentType='application/json',
                body=json.dumps({
                    "messages": [
                        {"role": "user", "content": "You are a helpful support assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 80,
                    "anthropic_version": "" # Still dont know what correct value for this field is but error gone when empty
                })
            )

            response_body = json.loads(llm_response['body'].read())
            llm_output = response_body.get('content', [{}])[0].get('text', 'No response.')

            # Step 3: Extract fields from the LLM output 
            priority_match = re.search(r"Priority:\s*(.*)", llm_output)
            difficulty_match = re.search(r"Difficulty:\s*(.*)", llm_output)
    
            # Summary set to one line will adjust regexp for multiple when needed
            summary_match = re.search(r"Summary:\s*(.*)", llm_output)
            suggested_fix_match = re.search(r"Suggested Fix:\s*((.|\n)*)", llm_output)
            
            # Check to see if matches contain correct data
            priority = priority_match.group(1).strip() if priority_match else "N/A"
            difficulty = difficulty_match.group(1).strip() if difficulty_match else "N/A"
            summary = summary_match.group(1).strip() if summary_match else "N/A"
            suggested_fix = suggested_fix_match.group(1).strip() if suggested_fix_match else "N/A"

            print("Extracted Fields:", {
                "priority": priority,
                "difficulty": difficulty,
                "summary": summary,
                "suggested_fix": suggested_fix
            })
    
            print("LLM Output", llm_output)


            # Step 4: Update ticket with LLM output
            ticket_table.update_item(
                Key={'ticketId': ticket_id},
                UpdateExpression="SET #s = :processed, aiSummary = :llmSummary, priority = :priority, suggestedFix = :suggestedFix, difficulty = :difficulty",
                ConditionExpression=Attr('status').eq('New'),
                ExpressionAttributeNames={'#s': 'status'},
                ExpressionAttributeValues={
                    ':processed': 'New',
                    ':llmSummary': summary,
                    ':priority': priority,
                    ':suggestedFix': suggested_fix,
                    ':difficulty': difficulty
                }
            )

            processing_tickets.append(ticket_id)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Processed {len(processing_tickets)} ticket(s).',
                'ticket_ids': processing_tickets
            })
        }

    except Exception as e:
        print(f"Error: {e}")
        return {'statusCode': 500, 'body': json.dumps(f"Error: {str(e)}")}