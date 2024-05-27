from groqqer import rss_to_vector, logger
from webhook import send_nfn
import os
from dotenv import load_dotenv


def main():
    load_dotenv()
    rss_to_vector(os.environ["NDTV_TECH_RSS_URL"])
    logger.info(msg="News exported to Vector Database!")
    send_nfn()


if __name__ == '__main__':
    main()
