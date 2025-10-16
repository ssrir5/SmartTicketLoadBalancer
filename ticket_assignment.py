def assignAndUpdateTicket(ticket_table, technician_table, ticket, technician):
    # Update the current Tech with the new ticket
    technician_table.update_item(
        Key={'technicianId': technician['technicianId']},
        UpdateExpression="SET ticketLoad = ticketLoad + :inc, currentTickets = list_append(currentTickets, :newTicket)",
        ExpressionAttributeValues={':inc': 1, ':newTicket': [ticket['ticketId']]} 
    )

    # Update the ticket info with new assignment
    ticket_table.update_item(
        Key={'ticketId': ticket['ticketId']},
        UpdateExpression="SET assignedTechnician = :techId, status = :status",
        ExpressionAttributeValues={":techId": technician['technicianId'], ':status': 'In Progress'}
    )

