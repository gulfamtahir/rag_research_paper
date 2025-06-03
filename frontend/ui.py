import streamlit as st
import requests

st.title("Research Paper Q&A Chatbot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# File upload section
st.sidebar.title("Upload Research Paper")
uploaded_file = st.sidebar.file_uploader("Upload a research paper", type="pdf")
if uploaded_file:
    # Prepare the file for upload
    files = {
        "file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")
    }
    with st.spinner("Uploading and processing the file..."):
        response = requests.post("http://0.0.0.0:8000/upload/", files=files)
    if response.status_code == 200:
        st.sidebar.success("File uploaded and processed successfully!")
    else:
        st.sidebar.error(f"Upload failed: {response.json().get('detail', 'Unknown error')}")

# Chat section
if prompt := st.chat_input("Ask a question about the research paper:"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Send the question to the FastAPI backend
    with st.spinner("Processing your question..."):
        response = requests.post("http://0.0.0.0:8000/query/", json={"question": prompt})
    if response.status_code == 200:
        answer = response.json().get("answer", "No answer found.")
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(answer)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": answer})
    else:
        st.error(f"Query failed: {response.json().get('detail', 'Unknown error')}")


# import streamlit as st
# import requests

# st.title("Research Paper Q&A")

# # Upload PDF
# uploaded_file = st.file_uploader("Upload a research paper", type="pdf")
# if uploaded_file:
#     # Prepare the file for upload
#     files = {
#         "file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")
#     }
#     response = requests.post("http://0.0.0.0:8000/upload/", files=files)
        
#     if response.status_code == 200:
#         st.success(f"Document uploaded and processed")
#     else:
#         st.error(f"Upload failed: {response.json().get('detail', 'Unknown error')}")

# # Ask a question
# question = st.text_input("Ask a question about the paper:")
# if st.button("Submit") and question:
#     # Show a spinner while waiting for the response
#     with st.spinner("Processing your question..."):
#         # Send the question as JSON to the /query/ endpoint
#         response = requests.post("http://0.0.0.0:8000/query/", json={"question": question})
#         if response.status_code == 200:
#             answer = response.json().get("answer", "No answer found.")
#             st.write(f"**Answer:** {answer}")
#         else:
#             st.error(f"Query failed: {response.json().get('detail', 'Unknown error')}")