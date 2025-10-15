import boto3
import os
import random
from faker import Faker
from datetime import datetime

CREATE_TICKETS = False

def findNextTicket(ticket_table):
    res = ticket_table.scan()
    tickets = res['Items']

    ticket_ids = []

    for ticket in tickets:
        try:
            ticket_ids.append(int(ticket['ticketId']))
        except ValueError:
            continue

    if ticket_ids:
        lastTicketId = max(ticket_ids)
        print(f"Foudn ticket ${lastTicketId} to start at")
        return lastTicketId
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
        
def print_table_data(table):
    res = table.scan()
    tickets = res['Items']

    for ticket in tickets:
        if(ticket['ticketId'] == '15'):
            for key, value in ticket.items():
                print(f"${key}, ${value}")



# Initialize the DynamoDB client with credentials
session = boto3.Session(
    aws_access_key_id= os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name='us-east-2'  
)

# Sesh for database 
dynamodb = session.resource('dynamodb')

#Ticket Table Access
ticket_table = dynamodb.Table("Client_Ticket_Information")

if CREATE_TICKETS:
    lastTicketId = findNextTicket(ticket_table)

    if lastTicketId != -1:
        create_custom_tickets(lastTicketId+1,10,ticket_table)

print_table_data(ticket_table)





