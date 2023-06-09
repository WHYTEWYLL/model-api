import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin

from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import DeepLake

app = Flask(__name__)
app.config["TIMEOUT"] = 300
cors = CORS(app, allow_headers=["Origin", "X-Requested-With", "Content-Type", "Accept"])


app.config["CORS_HEADERS"] = "Content-Type"


load_dotenv()

os.environ.get("ACTIVELOOP_TOKEN")
username = "rihp"  # replace with your username from app.activeloop.ai
projectname = "polywrap10"  # replace with your project name from app.activeloop.ai

embeddings = OpenAIEmbeddings(disallowed_special=())

db = DeepLake(
    dataset_path=f"hub://{username}/{projectname}",
    read_only=True,
    embedding_function=embeddings,
)

retriever = db.as_retriever()
retriever.search_kwargs["distance_metric"] = "cos"
retriever.search_kwargs["fetch_k"] = 100
retriever.search_kwargs["maximal_marginal_relevance"] = True
retriever.search_kwargs["k"] = 10

model = ChatOpenAI(model_name="gpt-4", temperature=0)  # switch to 'gpt-4'
qa = ConversationalRetrievalChain.from_llm(model, retriever=retriever)


@app.route("/ask", methods=["POST"])
@cross_origin()
def ask_question():
    print(request)
    print(request.get_json())
    print("------------------")

    data = request.get_json()

    prompt = data["question"]

    questions = [prompt]
    chat_history = []

    for question in questions:
        prefix = ""
        sufix = ". I just want the code structure . Dont give me any additional text or comments. Remember to use double quotes"

        result = qa(
            {"question": f"{prefix} {question} {sufix}", "chat_history": chat_history}
        )
        # chat_history.append((f'{prefix} {question} {sufix}', result['answer']))
        print(f"-> **Question**: {question} \n")
        print(f"**Answer**: {result['answer']} \n")

    answer = result["answer"]

    return jsonify({"answer": answer})


@app.route("/")
def index():
    # A welcome message to test our server
    return "<h1>Welcome to unblock-model-api</h1>"


if __name__ == "__main__":
    app.run()
    app.com
