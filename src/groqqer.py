from langchain_community.vectorstores import PGVector
from langchain.schema import Document
import os
from openai import OpenAI
import instructor
import json
import feedparser
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from models import NewsCategories
import logging
import psycopg2
from langchain_community.embeddings import BedrockEmbeddings


load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

url = os.environ["NDTV_TECH_RSS_URL"]
GROQ_API_KEY = os.environ["GROQ_API_KEY"]

connection_string = PGVector.connection_string_from_db_params(
    host=os.environ["DB_HOST"],
    port=os.environ["DB_PORT"],
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
    driver="psycopg2",
    database=os.environ["DB_NAME"],
)

embedding_function = BedrockEmbeddings(model_id="amazon.titan-embed-image-v1", credentials_profile_name = 'default')


def docs_to_pgvector(documents: list, collection_name: str = "News"):
    try:
        PGVector.from_documents(
            documents=documents,
            embedding=embedding_function,
            connection_string=connection_string,
            collection_name=collection_name,
        )
        logger.info(
            msg=f"Collection - {collection_name} successfully created!"
        )
    except Exception as e:
        logger.error(msg=f"Failed to create collection! {e}")
        raise Exception


def rss_to_vector(url: str, collection_name: str = "News"):
    logger.info("Mapping RSS Feeds")
    mapped = map_rss(url)
    structured = structure_articles(mapped)
    docs = create_documents(structured)
    docs_to_pgvector(documents=docs)


def vector_search(query_vector: list):
    conn = psycopg2.connect(
        host=os.environ["DB_HOST"],
        user=os.environ["DB_USER"],
        dbname=os.environ["DB_NAME"],
        password=os.environ["DB_PASSWORD"],
        port=os.environ["DB_PORT"],
    )
    cur = conn.cursor()

    # Retrieving top 50 best matches
    query = f"""
    select
        *
    from langchain_pg_embedding
    ORDER BY embedding <-> %s::vector
    LIMIT 50
    """

    result = cur.execute(query, (query_vector,))
    retrieved_docs = [i[2] for i in cur.fetchall()]

    conn.close()
    return retrieved_docs


client = instructor.patch(
    OpenAI(
        base_url="https://api.groq.com/openai/v1/",
        api_key=os.environ["GROQ_API_KEY"],
    ),
    mode=instructor.Mode.JSON,
)


def structure_articles(results: list):
    logger.info(msg="Structuring Articles")
    result_dict = {}

    for items in results:
        category = [i.keys() for i in items][0]
        category = "".join(list(category))
        if category not in result_dict.keys():
            result_dict[category] = []
        for i, sub in enumerate(items):
            try:
                summary = list(sub.values())[0]["summary"]
                content = list(sub.values())[0]["content"]
                logger.info(msg=f"Created article {i + 1} category {category}")
            except Exception as e:
                logger.warning(
                    f"Skipping : No entry found for article {i + 1} category {category}"
                )
                continue

            result_dict[category].append((i + 1, summary, content))

    return result_dict


def hash_to_summary(hash_val: int, mapped: dict):
    try:
        obj = {
            "summary": mapped[hash_val]["summary"],
            "content": mapped[hash_val]["content"],
        }
        return obj
    except KeyError:
        return ""


def gen_query_vector(query: str):
    query_vector = embedding_function.embed_query(query)
    return query_vector


def gen_chunked_summaries(summaries: list[str]):
    """
    Agentic Chunking into News Categories.
    """

    prompt = "Here are the news summaries : {}"
    response = None

    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt.format(summaries)}],
            response_model=NewsCategories,
        )
    except Exception as e:
        try:
            response = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt.format(summaries)}],
                response_model=NewsCategories,
            )
        except Exception as e:
            logger.error(msg=e)

    return response


def map_rss(url):
    logger.info(msg="Mapping RSS feeds to Hashes")

    content = feedparser.parse(url)
    entries = content["entries"]

    summaries = [i["summary"] for i in entries]

    contents = [
        BeautifulSoup(i["content"][0]["value"]).get_text() for i in entries
    ]

    hashes = [hash(i) for i in summaries]
    res = gen_chunked_summaries(summaries)
    categories = json.loads(res.json())
    categories_hash = [
        {"hashes": [hash(i) for i in val], "category": key}
        for key, val in categories.items()
    ]
    mapped = {
        hash(i): {"summary": i, "content": j}
        for i, j in zip(summaries, contents)
    }
    results = [
        [
            {i["category"]: hash_to_summary(hash_val=x, mapped=mapped)}
            for x in i["hashes"]
        ]
        for i in categories_hash
    ]

    results = [i for i in results if len(i) and isinstance(i, list)]
    return results


def create_documents(result_dict: dict):
    logger.info(msg="Creating Documents")
    documents = []
    for key, val in result_dict.items():
        for num, summary, content in val:
            doc = Document(
                page_content=content,
                metadata={"id": num, "category": key, "summary": summary},
            )
            documents.append(doc)

    return documents
