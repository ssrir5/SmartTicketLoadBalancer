import boto3
import os
import sys
from database_code_generator import create_custom_tickets, create_custom_technician, findNextIdRange, print_table_data
from scheduling_logic import findHighestMatchingTechnicians

# Params to set for creating new tech/ticks
CREATE_TICKET = False
CREATE_TECHNICIAN = False
NUMBER_OF_TICKETS_TO_CREATE = 1
NUMBER_OF_TECHNICIAN_TO_CREATE = 1

# Initialize the DynamoDB client with credentials
# Validate credentials and region early with clear errors
AWS_AK = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SK = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION")

if not AWS_AK or not AWS_SK:
    print("ERROR: AWS_ACCESS_KEY_ID or AWS_SECRET_ACCESS_KEY not set. Activate your venv or set these environment variables.")
    sys.exit(1)

if not AWS_REGION:
    print("WARNING: AWS_DEFAULT_REGION not set. Falling back to 'us-east-2'.")
    AWS_REGION = 'us-east-2'

#-------------------- Load session to use Table -------------------
session = boto3.Session(
    aws_access_key_id=AWS_AK,
    aws_secret_access_key=AWS_SK,
    region_name=AWS_REGION
)

# Connect to DB 
dynamodb = session.resource('dynamodb')

# Ticket and Technician Access 
ticket_table = dynamodb.Table("Client_Ticket_Information")
technician_table = dynamodb.Table("Technician_Information")

# To Generate More Techs/Tickets
if CREATE_TICKET:
    primaryKey = 'ticketId'
    lastId = findNextIdRange(ticket_table,primaryKey)

    if lastId != -1:
        create_custom_tickets(lastId+1,NUMBER_OF_TICKETS_TO_CREATE,ticket_table)

if CREATE_TECHNICIAN:
    primaryKey = 'technicianId'
    lastId = findNextIdRange(technician_table,primaryKey)

    if lastId != -1:
        create_custom_technician(lastId+1,NUMBER_OF_TECHNICIAN_TO_CREATE,technician_table)

# Custom Ticket to check 
custom_ticket =  {
    "ticketId": "11",
    "accessedTime": "14:37",
    "aiSummary": "System frequently restarts without warning after OS update.",
    "assignedTeam": "Team 2",
    "assignedTech": "05",
    "category": ["OS", "Hardware"],
    "clientId": "217",
    "description": "After the recent operating system update, the workstation reboots randomly every few hours, disrupting workflow. Event logs show kernel power errors.",
    "difficulty": 7,
    "priority": "high",
    "referenceTicketIds": ["04", "09"],
    "requiredSkills": ["OS", "Hardware", "Diagnostics"],
    "solution": "Pending diagnostic and hardware stress test.",
    "status": "New",
    "suggestedFix": "Check for faulty power supply or driver conflicts from previous tickets.",
    "technicainSkillMatch": 0,
    "timestamp": "10/15/25",
    "title": "Random System Reboots After Update"
}

# Number of Techs To broadcast to 
BROADCAST_TECH_COUNT = 7

# Find the closest tech that match ticket preference and broadcast
techList = findHighestMatchingTechnicians(technician_table, custom_ticket, BROADCAST_TECH_COUNT)

print(f"Custom Ticket ${custom_ticket['requiredSkills']}")

for tech in techList:
    print(f"---------Available Tech-------- List")
    print(f"${tech['name']}, ${tech['skills']}")


