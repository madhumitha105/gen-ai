from vector_tools import search_local_knowledge
result = search_local_knowledge.invoke({"query": "from sydney to tokyo give me travel itenary"})

print("--- Test Result ---")
print(result)