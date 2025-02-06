import logging
import random
import time
from typing import Dict, Literal, TypedDict
from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_core.messages import HumanMessage
import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

from flask import Flask, session
from flask_socketio import SocketIO as SocketIO, emit, join_room, leave_room
from flask_session import Session
import sqlite3

from flask import after_this_request

from sql import add_to_conversation, create_sql_tables, get_all_messages_sql, get_sequence, get_user_id, set_sequence

load_dotenv()

app = Flask(__name__)

app.secret_key = os.urandom(24)

#  Update CORS configuration to be more permissive for development
CORS(app)

# Session configuration
app.config.update(
    SESSION_TYPE='filesystem',
    SESSION_PERMANENT=True,
    SESSION_USE_SIGNER=True,
    SESSION_FILE_DIR='/tmp/flask_sessions',
    SESSION_COOKIE_SAMESITE='None',
    SESSION_COOKIE_SECURE=False  # Set to True in production with HTTPS
)

Session(app)

# Initialize SocketIO with updated CORS settings
socketio = SocketIO(app, cors_allowed_origins="*", engineio_logger=True, logger=True)

# Retrieve OpenAI API key
openai_api_key = os.getenv('OPENAI_API_KEY')
if not openai_api_key:
    raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)


# initiate sql
create_sql_tables()

print("Ready")

class State(TypedDict):
    username: str
    messages: list[str]
    sequence: list[str]
    context: str
    has_enough_info: bool
    next_question: str
    user_input: str
    
@socketio.on('join_room')
def handle_join_room(data):
    print("user joining room")
    username = data["username"]
    if not username: return
    join_room(username)
    print(f"User {username} connected and joined room")

# Socket connection handling
@socketio.on('connect')
def handle_connect():
    print('user connexted')

@socketio.on('get_all_messages')
def get_all_messages(data):
    username = data["username"]
    messages = get_all_messages_sql(username)
    print(f"Sending messages to user {username}")
    
    if messages:
        emit('all-messages', messages, room=username)
    

@socketio.on('get_sequence')
def handle_get_sequence(data):
    try:
        username = data.get("username")
        if not username:
            print("Error: No username provided")
            return
            
        print(f"Fetching sequence for user: {username}")
        sequence = get_sequence(username)
        print(f"Got sequence: {sequence}")
        
        if sequence:
            print(f"Emitting sequence to room {username}")
            # First, check if client is in the room
            rooms = socketio.server.rooms(request.sid)
            print(f"Client {request.sid} is in rooms: {rooms}")
            
            emit('sequence', sequence, room=username)
            
            # Double check emission
            print(f"Sequence emitted to {username}")
        else:
            print(f"No sequence found for {username}")
            emit('sequence', [], room=username)  # Send empty array if no sequence
            
    except Exception as e:
        print(f"Error in handle_get_sequence: {str(e)}")
        emit('error', {'message': f'Error getting sequence: {str(e)}'}, room=username)


@app.route('/')
def home():
    return "home"


@socketio.on('user-query')
def handle_user_query(data):
    def process_input(state: State) -> Dict:
        """Process new user input and add to messages"""
        state["messages"].append(state["user_input"])
        
        user_id = get_user_id(username)
        content = state["user_input"]
        
        add_to_conversation(user_id, 1, content)
        messages = get_all_messages_sql(username)
        
        emit('all-messages', messages, room=username)
        return {"messages": state["messages"]}

    def get_intent(state: State) -> Dict:
        
        print("getting intent") 
        
        if len(state["sequence"]) == 0:
            return "check_info_node"
        
        messages = [
            f"""
            Based on this conversation history and context, 
            
            Context: {state['context']}
            Message History: {state['messages']}
            Sequence: {state['sequence']}
            User Input: {state['user_input']}
            
            Determine the intent of the user's input. These are the options: Clarifying questions are nice, so if you need more info to create a sequence respond 'Info'. If they are modifying an existing sequence or steps respond 'Modify Sequence'.i 
            Remeber to respond with only one thing, 'Info' or 'Modify Sequence'
            """
        ]
        
        response = llm.invoke(messages).content.strip()
        print(response)
        
        if response == 'Info':
            return "check_info_node"
        elif response == 'Modify Sequence':
            return "modify_sequence"
        else: return END
    
    def check_info_node(state: State) -> Dict:
        print("Checking info at node")
        return {"user_input": state['user_input']}


    def check_info_route(state: State) -> str:
        """Check if we have enough information to generate a sequence"""
        print("Checking info route")
        messages = [
            f"""
            Based on this conversation history and context, do we have enough information 
            to generate a recruiting outreach sequence? If you have there has already been 2 clarifying questions, respond with 'True'. Reply with 'True' if you have enough info or 'False' if you would like more info.
            
            Context: {state['context']}
            Message History: {state['messages']}
            """
        ]
        
        print(state["messages"])
        
        response = llm.invoke(messages).content.strip()
        print(response)
        if response == "True":
            return "generate_sequence"
        elif response == "False":
            return "get_next_question"
        else:
            return END

    def get_next_question(state: State) -> Dict:
        """Generate the next question to ask the user"""
        prompt = [
            f"""
            Based on this conversation history and context, what's the next most important
            question we should ask to gather information for the recruiting sequence?
            Ask only ONE clear, specific question.
            
            Context: {state['context']}
            Message History: {state['messages']}
            """
        ]
        response = llm.invoke(prompt)
        
        state["messages"].append(response.content)
        print(state["messages"])

        user_id = get_user_id(username)
        add_to_conversation(1, user_id, response.content)
        messages = get_all_messages_sql(username)

        emit('all-messages', messages, room=username)
        
        return {"messages": state["messages"]} 

    def generate_sequence(state: State) -> Dict:
        """Generate the final recruiting sequence"""
        messages = [
            f"""
            Based on all the information gathered, generate a recruiting outreach sequence.
            Respond with a list of steps in a Json format structured like this:
            {{
            "data": [
                {{
                "step_number": 1,
                "step_info": "step1 details"
                }},
                {{
                    "step_number": 2,
                    "step_info": "step2 deails"
                }}
                ]
            }}
            
            Context: {state['context']}
            Message History: {state['messages']}
            """
        ]
        response = llm.invoke(messages)
        state["messages"].append(response.content)
        print(state["messages"])

        user_id = get_user_id(username)
        set_sequence(user_id, response.content)
        
        sequence = get_sequence(username)

        emit('sequence', sequence, room=username)
        return {"sequence": [response.content]}

    def modify_sequence(state: State) -> Dict:
        """Generate the final recruiting sequence"""
        print("modifying sequence")
        print(state['sequence'])
        print(state['user_input'])
        
        messages = [
            f"""
            Context: {state['context']}
            User Input: {state['user_input']}
            Current Sequence of steps: {state['sequence']}
            The user wants to modify the sequence. Based on the current sequence of steps and all the information gathered, generate a new recruiting outreach sequence with these modifications.
            Respond with a list of steps in a Json format structured like this:
            {{
            "data": [
                {{
                "step_number": 1,
                "step_info": "step1 details"
                }},
                {{
                    "step_number": 2,
                    "step_info": "step2 deails"
                }}
                ]
            }}
            
            """
        ]
        response = llm.invoke(messages)
        print(response.content)
        
        user_id = get_user_id(username)
        set_sequence(user_id, response.content)
        
        sequence = get_sequence(username)

        emit('sequence', sequence, room=username)
        return {"sequence": [response.content]}
    
    
    username = data["username"]
    query = data["query"]
    
    if not username or not query:
        emit('error', {'message': 'Username and query are required'}, room=request.sid)
        return

    messages = get_all_messages_sql(username)
    print(f"Emitting messages to user {username}")
    emit('all-messages', messages, room=username)
    
    # Initialize the graph
    workflow = StateGraph(State)
    
    # Add nodes
    workflow.add_node("process_input", process_input)
    workflow.add_node("get_intent", get_intent)
    workflow.add_node("check_info_route", check_info_route)
    workflow.add_node("check_info_node", check_info_node)
    workflow.add_node("get_next_question", get_next_question)
    workflow.add_node("generate_sequence", generate_sequence)
    workflow.add_node("modify_sequence", modify_sequence)
    
    # Add edges
    workflow.add_edge(START, "process_input")
    # Add conditional edges 
    workflow.add_conditional_edges(
        "process_input",
        get_intent,
    )
    workflow.add_conditional_edges(
        "check_info_node",
        check_info_route,
    )
    workflow.add_edge("get_next_question", END)
    workflow.add_edge("generate_sequence", END)
    workflow.add_edge("modify_sequence", END)
    
    print("Compiling graph")
    chain = workflow.compile()
    
    # get previous message context
    messages = get_all_messages_sql(username)
    sequence = get_sequence(username)
    print(f"Got messages: {messages}")
    print(f"Got sequence: {sequence}")

    # Initialize state
    initial_state = {
        "username": username,
        "user_input": query,
        "messages": messages,
        "context": "You are an HR assistant who will help the user create a sequence of recruiting outreach steps",
        "sequence": sequence,
        "has_enough_info": False,
        "next_question": ""
    }

    # Run the workflow
    steps = []
    for step in chain.stream(initial_state):
        steps.append(step)
    
    print("END")
    messages = get_all_messages_sql(username)
    emit('all-messages', messages)
    print(jsonify({"steps": steps}))

if __name__ == '__main__':
    socketio.run(app)
    # app.run(debug=True)