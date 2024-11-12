import requests
import threading
import time
import statistics
from urllib.parse import urlparse
import matplotlib.pyplot as plt
from tqdm import tqdm


cybernated_gurkha_ascii = """
   ____        _                                _             _    ____               _     _            
  / ___|_   _ | |__    ___  _ __  _ __    __ _ | |_  ___   __| |  / ___| _   _  _ __ | | __| |__    __ _ 
 | |   | | | || '_ \  / _ \| '__|| '_ \  / _` || __|/ _ \ / _` | | |  _ | | | || '__|| |/ /| '_ \  / _` |
 | |___| |_| || |_) ||  __/| |   | | | || (_| || |_|  __/| (_| | | |_| || |_| || |   |   < | | | || (_| |
  \____|\__, ||_.__/  \___||_|   |_| |_| \__,_| \__|\___| \__,_|  \____| \__,_||_|   |_|\_\|_| |_| \__,_|
        |___/                                                                                                                                                                    
                                                                                                          KhajumSanjog                                                     
"""

# Print ASCII art with formatting, size, and position
def get_user_input():
    print(cybernated_gurkha_ascii)
    target_url = input("Enter the target URL: ")
    num_threads = int(input("Enter the number of threads (concurrent users): "))
    requests_per_thread = int(input("Enter the number of requests per thread: "))
    http_method = input("Enter the HTTP method (GET, POST, etc.): ").upper()
    headers = input("Enter any custom headers (key1:value1,key2:value2,...): ")
    headers_dict = {}
    if headers:
        headers_list = headers.split(',')
        for header in headers_list:
            key, value = header.split(':')
            headers_dict[key.strip()] = value.strip()
    return target_url, num_threads, requests_per_thread, http_method, headers_dict

# Function to validate and correct the URL if needed
def validate_url(url):
    parsed_url = urlparse(url)
    if not parsed_url.scheme:
        url = "http://" + url
    return url

# Get user input
TARGET_URL, NUM_THREADS, REQUESTS_PER_THREAD, HTTP_METHOD, HEADERS = get_user_input()
TARGET_URL = validate_url(TARGET_URL)
    
print("Headers to be sent in the request:")
for key, value in HEADERS.items():
    print(f"{key}: {value}")
# Store the response times and status codes
response_times = []
status_codes = []
lock = threading.Lock()

# Define a function for each thread to run
def perform_requests(thread_bar):
    for _ in thread_bar:
        start_time = time.time()
        try:
            if HTTP_METHOD == 'GET':
                response = requests.get(TARGET_URL, headers=HEADERS)
            elif HTTP_METHOD == 'POST':
                response = requests.post(TARGET_URL, headers=HEADERS)
            # Add more methods as needed
            else:
                print(f"Unsupported HTTP method: {HTTP_METHOD}")
                return
            response_time = time.time() - start_time
            with lock:
                response_times.append(response_time)
                status_codes.append(response.status_code)
        except requests.RequestException as e:
            print(f"Request failed: {e}")

threads = []
thread_bars = []

# Create a tqdm progress bar for each thread
for i in range(NUM_THREADS):
    thread_bar = tqdm(range(REQUESTS_PER_THREAD), desc=f'Thread {i+1}', position=i+1)
    thread = threading.Thread(target=perform_requests, args=(thread_bar,))
    print(thread)
    threads.append(thread)
    thread_bars.append(thread_bar)
    thread.start()

# Wait for all threads to finish
for thread in threads:
    thread.join()

# Close all progress bars
for thread_bar in thread_bars:
    thread_bar.close()

# Wait for 3 seconds before printing the summary
time.sleep(3)

# Calculate statistics
if response_times:
    min_time = min(response_times)
    max_time = max(response_times)
    avg_time = statistics.mean(response_times)
    median_time = statistics.median(response_times)
    stdev_time = statistics.stdev(response_times)
    success_count = status_codes.count(200)
    failure_count = len(status_codes) - success_count

    # Prepare summary
    summary_lines = [
        f"Load Testing Summary for {TARGET_URL}",
        f"HTTP Method: {HTTP_METHOD}",
        f"Total Requests: {len(response_times)}",
        f"Success Requests: {success_count}",
        f"Failed Requests: {failure_count}",
        f"Min Response Time: {min_time:.2f} seconds",
        f"Max Response Time: {max_time:.2f} seconds",
        f"Average Response Time: {avg_time:.2f} seconds",
        f"Median Response Time: {median_time:.2f} seconds",
        f"Standard Deviation: {stdev_time:.2f} seconds"
    ]

    # Calculate box width
    max_length = max(len(line) for line in summary_lines)
    box_width = max_length + 4  # Add padding

    # Print summary in a box
    print("╔" + "═" * box_width + "╗")
    for line in summary_lines:
        print(f"║ {line.ljust(max_length)} ║")
    print("╚" + "═" * box_width + "╝")

    # Plotting the response times
    plt.figure(figsize=(10, 5))
    plt.plot(response_times, label='Response Time (s)')
    plt.axhline(y=avg_time, color='r', linestyle='--', label=f'Average Response Time: {avg_time:.2f}s')
    plt.axhline(y=median_time, color='g', linestyle='-.', label=f'Median Response Time: {median_time:.2f}s')
    plt.xlabel('Request Number')
    plt.ylabel('Response Time (s)')
    plt.title('Response Times for Load Testing')
    plt.legend()
    plt.grid(True)
    plt.show()
else:
    print("No requests were successfully completed.")
