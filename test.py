import streamlit as st
from transformers import AutoModelForCausalLM, AutoTokenizer

# Load the pretrained model and tokenizer
model_name = "microsoft/DialoGPT-medium"  # You can replace this with other open-source conversational models
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Initialize memory for the chatbot
conversation_memory = []

# Function to generate a response
def generate_response(user_input):
    global conversation_memory
    
    # Tokenize the input and append to the memory
    inputs = tokenizer.encode(" ".join(conversation_memory + [user_input]), return_tensors="pt")
    
    # Generate the response
    outputs = model.generate(inputs, max_length=1000, pad_token_id=tokenizer.eos_token_id, top_p=0.9, temperature=0.7)
    response = tokenizer.decode(outputs[:, inputs.shape[-1]:][0], skip_special_tokens=True)
    
    # Add the user input and response to the memory
    conversation_memory.append(user_input)
    conversation_memory.append(response)
    
    return response

# Streamlit UI
st.title("General Purpose Chatbot")
st.markdown("This chatbot uses an open-source conversational model.")

def main():
    global conversation_memory
    
    user_input = st.text_input("You:", "", key="user_input")
    
    if user_input:
        # Generate response
        response = generate_response(user_input)
        
        # Display response
        st.text_area("Chatbot:", response, height=200)

if __name__ == "__main__":
    main()
