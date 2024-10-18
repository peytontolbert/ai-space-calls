def prepare_system_prompt(space_name, description, participants):
    prompt = f"Space Name: {space_name}\nDescription: {description}\nParticipants:\n"
    for participant in participants:
        prompt += f"- {participant['name']}: {participant['persona']}\n"
    prompt += "\nConversation starts here.\n"
    return prompt
