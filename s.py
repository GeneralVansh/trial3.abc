from gensim.models import KeyedVectors

# apna file path yahan daal
model_path = r"C:\Users\<your_username>\Downloads\GoogleNews-vectors-negative300.bin"

model = KeyedVectors.load_word2vec_format(model_path, binary=True)

print("Model loaded successfully!")
print(model.most_similar("king"))
