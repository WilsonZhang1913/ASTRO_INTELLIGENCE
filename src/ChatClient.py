import openai # Import the base library first
from openai import OpenAI, APIError, RateLimitError, APIConnectionError, AuthenticationError, NotFoundError, BadRequestError, PermissionDeniedError # Import specific exceptions
from prompts.SystemPrompt import SYSTEM_PROMPT
from config.config import *
# from openai import OpenAI # Remove duplicate import
import time
import traceback # For unexpected errors


class ChatClient:
    def __init__(self):
        self.client = OpenAI(
            base_url= BASE_URL,
            api_key= API_KEY
        )


    def messageBuilder(self, question: str) -> list:
        """Builds the standard message list for the API call."""
        return [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question}
        ]

    def chat_with_model_stream(self, question):
        """
        Attempts to get a streaming chat completion from configured models.

        This function is a generator. It yields chunks of the response content
        from the first successful model's stream. Status messages about which
        model is being tried or errors encountered are printed to stderr.

        Args:
            question (str): The user's question.

        Yields:
            str: Chunks of the response content from the model.

        Raises:
            RuntimeError: If no configured model successfully returns a stream
                        after trying all of them.
            # Specific OpenAI exceptions might bubble up if not caught or if re-raised
            # (e.g., AuthenticationError, BadRequestError are re-raised by default here).
        """
        messages = self.messageBuilder(question)
        success = False # Flag to track if any model succeeded

        for model in CHATBOT_MODELS:
            try:
                # Print status messages to stderr or use logging
                print(f"\n🔄 Trying model: {model}", flush=True)
                stream = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    stream=True,
                    # Consider adding a timeout
                    # timeout=30.0 # Example: 30 seconds timeout
                )

                content_yielded = False
                # Iterate through the stream and yield content chunks
                for chunk in stream:
                    if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        yield content # <-- YIELD the content chunk
                        content_yielded = True

                # If we successfully processed the stream (even if it was empty), mark success
                if content_yielded:
                    print(f"\n✅ Stream finished for model: {model}", flush=True) # Status print
                    success = True
                    break # Success, stop trying other models
                else:
                    # Handle case where stream completed but yielded no content
                    print(f"⚠️ Model {model} returned an empty stream.", flush=True)
                    # Continue loop to try the next model

            # --- Specific OpenAI Error Handling ---
            except AuthenticationError as e:
                print(f"❌ Authentication Error with model {model}: {e}", flush=True)
                print("   Check API key/permissions. Stopping attempts.", flush=True)
                raise # Re-raise critical errors like auth failure to stop execution
            except PermissionDeniedError as e:
                print(f"❌ Permission Denied for model {model}: {e}", flush=True)
                # Continue to the next model
            except NotFoundError as e:
                print(f"❌ Model Not Found Error: '{model}'. {e}", flush=True)
                # Continue loop to try the next model
            except RateLimitError as e:
                print(f"⏳ Rate Limit Error for model {model}: {e}. Waiting...", flush=True)
                time.sleep(5) # Wait longer for rate limit errors
            except APIConnectionError as e:
                print(f"🌐 API Connection Error with model {model}: {e}. Retrying...", flush=True)
                time.sleep(2)
            except BadRequestError as e:
                print(f"👎 Bad Request Error with model {model}: {e}", flush=True)
                if hasattr(e, 'body') and e.body:
                    print(f"   Error details: {e.body}", flush=True)
                print("   Stopping attempts due to potential data issue.", flush=True)
                raise # Re-raise, likely unrecoverable for this request
            except APIError as e: # Catch other OpenAI API specific errors
                print(f"⚠️ OpenAI API Error with model {model}: {type(e).__name__} - {e}", flush=True)
                time.sleep(1)
            # --- General Error Handling ---
            except Exception as e:
                print(f"💥 Unexpected error with model {model}: {type(e).__name__} - {e}", flush=True)
                print("--- Traceback ---", flush=True)
                traceback.print_exc()
                print("--- End Traceback ---", flush=True)
                time.sleep(1)

        # After the loop, if no model succeeded
        if not success:
            # Raise an exception if all models failed
            raise RuntimeError("Failed to get a response from any configured model.")

# --- Example Usage (Updated) ---

if __name__ == "__main__":
    question = input("Enter your question:")
    print("Bot: ", end="", flush=True) # Initial prompt for the bot response
    chatClient = ChatClient()
    try:
        # chat_with_model_stream returns a generator object
        stream_generator = chatClient.chat_with_model_stream(question)

        full_response = ""
        # Iterate through the generator to get the yielded chunks
        for chunk in stream_generator:
            print(chunk, end="", flush=True) # The caller now prints the chunk
            full_response += chunk # Optionally collect the full response

        print() # Add a newline after the stream is complete

        # You can do something with the full response here if needed
        # print(f"\n--- Full response collected ---\n{full_response}")

    except RuntimeError as e:
        # Handles the case where all models failed (raised from the generator)
        print(f"\n❌ Error: {e}")
    except (AuthenticationError, BadRequestError) as e:
         # Handle critical errors that were re-raised
         print(f"\n❌ Critical API Error: {e}")
    except Exception as e:
        # Catch any other unexpected errors during iteration
        print(f"\n💥 An unexpected error occurred while processing the stream: {e}")
        traceback.print_exc()

