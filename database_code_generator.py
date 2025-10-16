import boto3
import os
import sys
import random
from faker import Faker
from datetime import datetime
from scheduling_logic import findHighestMatchingTechnicians

CREATE_TICKET = False
CREATE_TECHNICIAN = False
NUMBER_OF_TICKETS_TO_CREATE = 1
NUMBER_OF_TECHNICIAN_TO_CREATE = 10


def findNextIdRange(table,primaryKey):
    # Reads in all table data
    res = table.scan()
    tableKeyIds = res['Items']

    # Iterate through table items and add pKey to find max 
    keyIds = []

    for item in tableKeyIds:
        try:
            keyIds.append(int(item[primaryKey]))
        except ValueError:
            continue

    if keyIds:
        lastId = max(keyIds)
        print(f"Found Id ${lastId} as last item")
        return lastId
    else:
        print("No tickets Found")
        return -1

def create_custom_tickets(startRange,numberOfTickets,ticket_table):

    fake = Faker()

    teams = ["Team 1", "Team 2", "Team 3", "Team 4"]
    categories = ["OS", "IT", "Network", "Security", "Hardware", "Software"]
    priorities = ["low", "medium", "high"]
    statuses = ["New", "In Progress", "Resolved", "Closed"]

    ticket_problems = [
        "Blue screen shows on every startup",
        "Cannot connect to Wi-Fi network",
        "Forgotten password for Windows login",
        "Email client not syncing",
        "Printer is offline and not responding",
        "Application crashes when opening file",
        "Laptop battery drains too quickly",
        "User cannot access shared folder",
        "Computer running very slowly",
        "Antivirus detects false positives"
    ]

    ticket_solutions = [
        "Restart the computer and check for updates",
        "Reset network settings and reconnect Wi-Fi",
        "Reset the user's password and test login",
        "Reconfigure email account and sync settings",
        "Restart printer and reinstall drivers",
        "Update the application to the latest version",
        "Replace battery or adjust power settings",
        "Check folder permissions and network access",
        "Run disk cleanup and defragment the drive",
        "Update antivirus definitions and whitelist app"
    ]

    ai_summaries = [
        "System crashes frequently on startup",
        "User cannot access network resources",
        "Application issues reported by client",
        "Hardware malfunction suspected",
        "Performance degradation observed",
        "Security alert triggered"
    ]


    for i in range(startRange,startRange+numberOfTickets):

        ticketId = f"{i:02d}"

        ticket = {
            "ticketId": ticketId,
            "accessedTime": fake.time(pattern="%H:%M"),
            "aiSummary": random.choice(ai_summaries),
            "assignedTeam": random.choice(teams),
            "assignedTech": f"{random.randint(1, 10):02d}",
            "category": random.sample(categories, k=random.randint(1,3)),
            "clientId": f"{random.randint(100, 999)}",
            "description": random.choice(ticket_problems),
            "difficulty": random.randint(1, 10),
            "priority": random.choice(priorities),
            "referenceTicketIds": [f"{random.randint(1,10):02d}" for _ in range(random.randint(0,2))],
            "solution": random.choice(ticket_solutions),
            "status": random.choice(statuses),
            "suggestedFix": random.choice(ticket_solutions),
            "technicainSkillMatch": random.randint(1,10),
            "timestamp": datetime.now().strftime("%m/%d/%y"),
            "title": fake.sentence(nb_words=3)
        }

        ticket_table.put_item(Item=ticket)
        print(f"Inserted ticket ${ticketId} into table")

def create_custom_technician(startRange,numberOfTickets,technician_table):
    fake = Faker()
    teams = ["Team 1", "Team 2", "Team 3", "Team 4"]
    skills_pool = ["OS", "IT", "Network", "Security", "Hardware", "Software"]
    statuses = ["active", "idle", "offline"]

    for i in range(startRange,startRange+numberOfTickets):

        tech_id = f"{i:02d}"
        tech = {
            "technicianId": tech_id,
            "availability": random.choice([True, False]),
            "avgCompletionTime": random.randint(30, 500),  # minutes
            "currentStatus": random.choice(statuses),
            "currentTickets": [f"{random.randint(1,10):02d}" for _ in range(random.randint(0,3))],
            "lastActive": fake.date_between(start_date='-1y', end_date='today').strftime("%m/%d/%y"),
            "maxTicketCapacity": random.randint(5, 20),
            "name": fake.first_name(),
            "performanceScore": random.randint(1,10),
            "skills": random.sample(skills_pool, k=random.randint(1,3)),
            "teamId": random.choice(teams),
            "ticketLoad": random.randint(0,10)
        }

        technician_table.put_item(Item=tech)
        print(f"Added tech number ${tech_id}")

def print_table_data(table):
    res = table.scan()
    items = res.get('Items', [])

    for item in items:
        print(f"--- Item ---")
        for key, value in item.items():
            print(f"{key}: {value}")
 

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

# Load session to use Table -------------

session = boto3.Session(
    aws_access_key_id=AWS_AK,
    aws_secret_access_key=AWS_SK,
    region_name=AWS_REGION
)

# Sesh for database 
dynamodb = session.resource('dynamodb')

# Ticket and Technician Access 
ticket_table = dynamodb.Table("Client_Ticket_Information")
technician_table = dynamodb.Table("Technician_Information")

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

# print_table_data(ticket_table)
# print_table_data(technician_table)


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


techList = findHighestMatchingTechnicians(technician_table,custom_ticket,5)

for tech in techList:
    print(f"---------Available Tech--------")
    print(tech)







