# Scheduling logic based of metric
# Overall Performance, Relatability, avg Completion Time
# Assign if Available, currentStatus active, load < max cap

"""
Checks technician database to find all available techs 
"""

def findAvailableTechnicians(technician_table):
    res = technician_table.scan()
    technicians = res['Items']

    valid_techs = []
    
    if technicians:
        for technician in technicians:
            if technician['availability'] and technician['currentStatus'] == 'active' and technician['ticketLoad'] < technician['maxTicketCapacity']:
                valid_techs.append(technician)

    return valid_techs

"""
Uses performance metric to calculate a score for each tech 
Score currently based on tech performance, skills, and completion time
"""

def calculate_ticket_match_rating(technician, ticket):
    DIVISION_BY_ZERO_PAD = 1e-5
    # Weight for each attribute for a tech (will change based on what matters the most later)
    PERFORMANCE_WEIGHT = 0.5
    SKILLS_WEIGHT = 0.3
    COMPLETION_TIME_WEIGHT = 0.2

    # Match the overlapping skills
    matching_skillset_count = len(set(technician['skills']) & set(ticket['category']))
    completion_score = 1 / (float(technician["avgCompletionTime"]) + DIVISION_BY_ZERO_PAD)
    
    total_score = (
        PERFORMANCE_WEIGHT * float(technician["performanceScore"]) +
        SKILLS_WEIGHT * matching_skillset_count +
        COMPLETION_TIME_WEIGHT * completion_score
    )

    return total_score

"""
Takes all available techs and ranks their score to find the top number of techs
"""

def findHighestMatchingTechnicians(technician_table, ticket, numberOfTechs):
    available_technicians = findAvailableTechnicians(technician_table)
    
    ranked_techs = []

    for tech in available_technicians:
        score = calculate_ticket_match_rating(tech,ticket)
        ranked_techs.append((tech, score))

    ranked_techs.sort(key=lambda x: x[1], reverse=True)

    top_technicians = [tech for tech, _ in ranked_techs[:numberOfTechs]]
    return top_technicians

    

    







