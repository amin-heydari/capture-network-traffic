import redis
import threading
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions

redis_client = redis.Redis(host='localhost', port=6379, db=0)
num_threads = 5

options = ChromeOptions()
options.add_argument('--enable-logging')
options.add_argument('--v=1')
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})


def process_browser_log_entry(entry):
    response = json.loads(entry['message'])['message']
    return response


def process_domain(domain):
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(domain)
    except:
        print(f'Request URL: {domain}')
        print(f'statusCode: 502 ')
        print()

    browser_log = driver.get_log('performance')
    events = [process_browser_log_entry(entry) for entry in browser_log]
    events = [event for event in events if 'Network.' in event['method']]

    requests = {}

    for event in events:
        if event['method'] == 'Network.requestWillBeSent':
            request_id = event['params']['requestId']
            request_url = event['params']['request']['url']
            requests[request_id] = {'url': request_url, 'statusCode': None}
        elif event['method'] == 'Network.responseReceivedExtraInfo':
            request_id = event['params']['requestId']
            status_code = event['params']['statusCode']
            requests[request_id]['statusCode'] = status_code

    for request_id, request_info in requests.items():
        print(f'Request ID: {request_id}')
        print(f'Request URL: {request_info["url"]}')
        print(f'statusCode: {request_info["statusCode"]}')
        print()
    # Remove the domain from Redis after processing
    driver.close()
    redis_client.lrem('domain_queue', 0, domain)


def worker(r):
    lock = threading.Lock()

    while True:
        lock.acquire()

        if redis_client.llen('domain_queue') > 0:
            domain = redis_client.lpop('domain_queue').decode('utf-8')
            lock.release()

            process_domain(domain)
        else:
            lock.release()
            break


def add_domains_to_redis():
    with open('domains.txt', 'r') as file:
        domain_names = file.readlines()

    for domain in domain_names:
        domain = domain.strip()
        redis_client.rpush('domain_queue', domain)


def main():
    add_domains_to_redis()
    threads = []

    for _ in range(num_threads):
        thread = threading.Thread(target=worker, args=(redis_client,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

        print("All domains processed.")


if __name__ == "__main__":
    main()
