import streamlit as st
import openai

# Set your OpenAI API key
openai.api_key = "your-openai-api-key"

# Initialize memory for the chatbot
conversation_memory = []

# Function to interact with GPT (OpenAI)
def generate_response(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150,
        temperature=0.7
    )
    return response['choices'][0]['text'].strip()

# Streamlit UI
st.title("General Purpose Chatbot")
st.markdown("This chatbot has interactivity and memory capabilities.")

# User input
def main():
    global conversation_memory

    user_input = st.text_input("You:", "", key="user_input")

    if user_input:
        # Add user query to memory
        conversation_memory.append({"role": "user", "content": user_input})

        # Prepare the prompt
        prompt = "The following is a conversation with a chatbot.\n"
        for message in conversation_memory:
            prompt += f"{message['role']}: {message['content']}\n"
        prompt += "assistant:"

        # Generate the response
        response = generate_response(prompt)

        # Display the response
        st.text_area("Chatbot:", response, height=200)

        # Add response to memory
        conversation_memory.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
