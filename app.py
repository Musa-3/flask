from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, send

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Replace with a secure secret key in production
socketio = SocketIO(app)

# Dictionary to store chat messages room-wise
chat_history = {}

@app.route("/")
def home():
    return render_template("base.html")

@app.route("/chat")
def chat():
    return render_template("chat.html")

@socketio.on("join")
def handle_join(data):
    username = data["username"]
    room = data["room"]

    # Add room to chat history if it doesn't exist
    if room not in chat_history:
        chat_history[room] = []

    # Add user to the room
    join_room(room)

    # Send join notification to the room
    send(f"{username} has joined the room.", to=room)

    # Load chat history for the user
    socketio.emit("load_history", chat_history[room], to=request.sid)

@socketio.on("leave")
def handle_leave(data):
    username = data["username"]
    room = data["room"]

    # Remove user from the room
    leave_room(room)

    # Send leave notification to the room
    send(f"{username} has left the room.", to=room)

@socketio.on("message")
def handle_message(data):
    username = data["username"]
    room = data["room"]
    message = data["message"]

    # Format the full message
    full_message = f"{username}: {message}"

    # Append the message to the room's chat history
    chat_history[room].append(full_message)

    # Broadcast the message to the room
    send(full_message, to=room)

if __name__ == "__main__":
    import eventlet
    eventlet.monkey_patch()
    socketio.run(app, host="0.0.0.0", port=5000)
