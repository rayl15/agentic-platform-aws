from agentic_platform.core.models.prompt_models import BasePrompt
SYSTEM_PROMPT = "You are a RAG bot. You are given a query and context. Your job is to answer the query using ONLY the context provided."

USER_PROMPT = """
For the users query:
<query>
{user_message}
</query>

And context below

<context>
{context}
</context>

Answer the query using ONLY the context provided. Avoid saying "according to the context provided" or anything similar.
Be very direct and straight forward with your answer. It's returning to an agent, not a human.
"""    

class RAGPrompt(BasePrompt):
    model_id: str = "us.amazon.nova-lite-v1:0"
    system_prompt: str = SYSTEM_PROMPT
    user_prompt: str = USER_PROMPT