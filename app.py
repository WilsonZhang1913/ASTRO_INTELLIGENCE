# app.py
import sys
import os
from flask import Flask, render_template, request, Response, stream_with_context
import json # To potentially send structured error messages

# Add the src directory to the Python path to find ChatClient
# Adjust the path if your directory structure is different
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

try:
    from ChatClient import ChatClient, AuthenticationError, BadRequestError, RuntimeError # Import necessary items
except ImportError as e:
    print(f"Error importing ChatClient: {e}")
    print("Ensure ChatClient.py is in the 'src' directory and src is in PYTHONPATH.")
    sys.exit(1)

app = Flask(__name__)

# Instantiate your ChatClient once
try:
    chat_client = ChatClient()
except Exception as e:
    print(f"Error initializing ChatClient: {e}")
    # Handle initialization error appropriately, maybe exit or provide a dummy client
    chat_client = None # Or raise an error

@app.route('/')
def index():
    """Renders the main HTML page."""
    # Ensure the templates folder is correctly located relative to app.py
    # Flask looks for templates in a 'templates' subfolder by default.
    return render_template('chat.html')

@app.route('/author')
def author():
    """Renders the author page (if you have one)."""
    # Replace with your actual author page rendering logic
    return render_template('author.html')


@app.route('/chat_stream')
def chat_stream():
    """
    Handles the streaming chat request using Server-Sent Events (SSE).
    Takes the question as a query parameter.
    """
    if not chat_client:
         # Function to send an SSE error message
        def error_stream():
            error_message = "Chat client failed to initialize on the server."
            yield f"event: error\ndata: {json.dumps({'error': error_message})}\n\n"
        return Response(stream_with_context(error_stream()), mimetype='text/event-stream')

    question = request.args.get('question', '') # Get question from query param
    if not question:
        def error_stream():
            error_message = "No question provided."
            yield f"event: error\ndata: {json.dumps({'error': error_message})}\n\n"
        return Response(stream_with_context(error_stream()), mimetype='text/event-stream')

    def generate_sse():
        """Generates SSE formatted stream data."""
        try:
            # Use the generator from ChatClient
            stream_generator = chat_client.chat_with_model_stream(question)
            for chunk in stream_generator:
                # Format as SSE: data: <chunk>\n\n
                yield f"data: {json.dumps(chunk)}\n\n" # Send data as JSON string
            # Signal the end of the stream (optional, but good practice)
            yield "event: end\ndata: {}\n\n"

        # --- Handle specific errors from ChatClient that stop the process ---
        except (AuthenticationError, BadRequestError) as e:
            print(f"SSE Stream Error (Critical): {e}") # Log server-side
            # Send a specific error event to the client
            error_data = {'error': f"API Error: {type(e).__name__}", 'message': str(e)}
            yield f"event: error\ndata: {json.dumps(error_data)}\n\n"
        except RuntimeError as e: # Catch the "all models failed" error
            print(f"SSE Stream Error (Runtime): {e}") # Log server-side
            error_data = {'error': "Runtime Error", 'message': str(e)}
            yield f"event: error\ndata: {json.dumps(error_data)}\n\n"
        except Exception as e:
            # Catch any other unexpected errors during generation
            print(f"SSE Stream Error (Unexpected): {e}") # Log server-side
            import traceback
            traceback.print_exc() # Log full traceback
            error_data = {'error': "Unexpected Server Error", 'message': "An error occurred while generating the response."}
            yield f"event: error\ndata: {json.dumps(error_data)}\n\n"

    # Return a streaming response with the correct mimetype for SSE
    # stream_with_context is important for using generators within requests
    return Response(stream_with_context(generate_sse()), mimetype='text/event-stream')


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8083))
    app.run(host="0.0.0.0", port=port)
