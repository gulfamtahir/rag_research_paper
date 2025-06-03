




# import streamlit as st
# from streamlit_chat import message
# import requests
# import json
# from agno.utils.log import logger
# from dotenv import load_dotenv
# import os
# load_dotenv()

# API_URL = os.getenv("API_URL")
# def init():
#     st.set_page_config(page_title="Chat App", layout="centered")
#     load_dotenv()
    


# def process_query(query):
#     try:
#         response = requests.post(
#             API_URL,
#             headers={"Content-Type": "application/json"},
#             data=json.dumps({"text": query})
#         )
        
#         if response.status_code == 200:
#             logger.info(response)
#             # data = response.json()
#             # # Update shopping list in session state
#             # st.session_state.shopping_list = data["shopping_list"]
#             # # Add to chat history
#             # st.session_state.chat_history.append({"user": query, "assistant": data["response"]})
#             # return data["response"]
#         else:
#             return f"Error: Received status code {response.status_code}"
    
#     except requests.exceptions.ConnectionError:
#         return "Error: Could not connect to the backend server. Make sure it's running on http://127.0.0.1:8000"
#     except Exception as e:
#         return f"Error: {str(e)}"

# def main():
#     init()
#     st.title("ChatGPT-like Chat Interface")
#     st.markdown("---")
    
    
    

#     # -- Initialize session state for chat history --
#     if 'past' not in st.session_state:
#         st.session_state.past = []
#     if 'generated' not in st.session_state:
#         st.session_state.generated = []

#     # -- Callback when user submits a message --
#     def on_input():
#         user_msg = st.session_state.user_input
#         if user_msg:
#             # Append user message and a placeholder response to session state
#             st.session_state.past.append(user_msg)
#             # TODO: Replace the following line with actual model response if needed
#             output = process_query(user_msg)
#             st.session_state.generated.append(output)
#             # Clear input box after sending
#             st.session_state.user_input = ""

#     # -- Render chat messages inside a scrollable container --
#     # Fixed height (500px) enables scrolling for overflow:contentReference[oaicite:5]{index=5}.
#     chat_container = st.container(height=500, key="chat")
#     with chat_container:
#         for i in range(len(st.session_state.generated)):
#             # Display the user message
#             message(st.session_state.past[i], is_user=True, key=f"user_{i}")
#             # Display the bot response
#             message(st.session_state.generated[i], is_user=False, key=f"bot_{i}")

#         # Auto-scroll to bottom: inject JS to set scrollTop = scrollHeight:contentReference[oaicite:6]{index=6}.
#         # We select the container by its Streamlit-generated CSS class (st-key-chat).
#         scroll_js = """
#         <script>
#         setTimeout(function() {
#             const container = window.parent.document.querySelector('.st-key-chat');
#             if (container) {
#                 container.scrollTop = container.scrollHeight;
#             }
#         }, 100);
#         </script>
#         """
#         st.components.v1.html(scroll_js, height=0, width=0)

#     # -- User input area --
#     st.text_input("You:", key="user_input", on_change=on_input)


# if __name__ == "__main__":
#     main()