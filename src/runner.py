import os

from dotenv import load_dotenv

from groqqer import logger, rss_to_vector
from webhook import send_nfn


def main():
    load_dotenv()
    rss_to_vector(os.environ["NDTV_TECH_RSS_URL"])
    logger.info(msg="News exported to Vector Database!")
    send_nfn()


if __name__ == '__main__':
    main()
