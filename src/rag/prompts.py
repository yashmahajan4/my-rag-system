def build_prompt(question, context):

    return f"""
Answer ONLY using the supplied context.

If the answer is not available in the context,
say:

I could not find that information in the document.

Context:

{context}

Question:

{question}

Answer:
"""