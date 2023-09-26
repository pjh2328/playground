from confluent_kafka import Producer
import time
import random
from faker import Faker
from datetime import datetime

fake = Faker()

# 카프카 브로커 정보 설정
bootstrap_servers = 'localhost:9092'  # 카프카 브로커의 호스트와 포트를 설정해야 합니다.

# 첫 번째 프로듀서 설정 (fakelog1 토픽으로 데이터 보내기)
producer_config1 = {
    'bootstrap.servers': bootstrap_servers,
    'queue.buffering.max.messages': 10000000,  # 배치 크기 설정 (메시지 버퍼링)
    'queue.buffering.max.ms': 10,  # 배치를 보내는 최대 대기 시간 (밀리초)
}

producer1 = Producer(producer_config1)

# 두 번째 프로듀서 설정 (fakelog2 토픽으로 데이터 보내기)
# producer_config2 = {
#     'bootstrap.servers': bootstrap_servers,
#     'queue.buffering.max.messages': 10000000,  # 배치 크기 설정 (메시지 버퍼링)
#     'queue.buffering.max.ms': 10,  # 배치를 보내는 최대 대기 시간 (밀리초)
# }

# producer2 = Producer(producer_config2)

# 첫 번째 토픽 이름 설정
topic_name1 = 'fakelog1'

# 두 번째 토픽 이름 설정
# topic_name2 = 'fakelog2'

# TPS 측정을 위한 변수 초기화
start_time = time.time()
message_count1 = 0
# message_count2 = 0

def generate_log_data():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_level = random.choice(["INFO", "WARNING", "ERROR"])
    log_source = random.choice(["Administrator", "Client", "Host"])
    random_integer = random.randint(10, 99)
    log_message = fake.sentence() 
    return f"[{current_time}][{log_level}][{log_source}][{random_integer}] {log_message}"


def produce_data1():
    global message_count1
    for _ in range(1):  # 120초 동안
        for i in range(3600000):  
            log_data = generate_log_data()
            producer1.produce(topic_name1, key=str(i), value=log_data)
            message_count1 += 1

for _ in range(10):
    log_data = generate_log_data()
    print(log_data)
# def produce_data2():
#     global message_count2
#     for _ in range(1):  # 120초 동안
#         for i in range(1800, 3600):  # 첫 번째 프로듀서와 중복되지 않는 범위
#             log_data = generate_log_data()
#             producer2.produce(topic_name2, key=str(i), value=log_data)
#             message_count2 += 1

# 두 프로듀서 함수 호출
produce_data1()
# produce_data2()

# 모든 메시지를 보내고 대기
producer1.flush()
# producer2.flush()

# TPS 측정
end_time = time.time()
elapsed_time = end_time - start_time
tps1 = message_count1 / elapsed_time
# tps2 = message_count2 / elapsed_time

print(f"Total Messages Produced (Producer 1): {message_count1}")
# print(f"Total Messages Produced (Producer 2): {message_count2}")
print(f"Total Time Taken: {elapsed_time} seconds")
print(f"TPS (Producer 1): {tps1} messages/second")
# print(f"TPS (Producer 2): {tps2} messages/second")