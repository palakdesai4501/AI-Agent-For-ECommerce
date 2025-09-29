// Learn more about clients at https://docs.boundaryml.com/docs/snippets/clients/overview

// Using the new OpenAI Responses API for enhanced formatting

// Example Vertex AI client (uncomment to use)
client<llm> Gemini {
  provider google-ai
  options {
    model "gemini-2.0-flash-lite"
    api_key env.GEMINI_API_KEY
  }
}


