from kafka import KafkaProducer
import json


# kafka producer 싱글톤
class kafkaProducer:
    instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.instance:
            cls.instance = KafkaProducer(
                bootstrap_servers=[
                    "ip-10-140-90-42.ap-northeast-2.compute.internal:9092",
                    "ip-10-140-90-43.ap-northeast-2.compute.internal:9092",
                    "ip-10-140-90-44.ap-northeast-2.compute.internal:9092"
                ],
                value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8'),
                acks='all'
            )
        return cls.instance
