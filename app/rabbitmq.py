import aio_pika
import json
from typing import Awaitable, Callable

RABBITMQ_URL = "amqp://guest:guest@localhost/"
QUEUE_NAME = "rabbitmq_playground_queue"


async def send_direct_message_to_queue():
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    channel = await connection.channel()
    queue = await channel.declare_queue(QUEUE_NAME, durable=True)
    await channel.default_exchange.publish(
        aio_pika.Message(body=b"Hello RabbitMQ"),
        routing_key=queue.name
    )
    print("Message sent!")


async def publish_message(payload: dict):
    """Publish a full message payload as JSON to the shared queue."""
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue(QUEUE_NAME, durable=True)
        body = json.dumps(payload).encode()
        await channel.default_exchange.publish(
            aio_pika.Message(body=body),
            routing_key=queue.name,
        )


async def consume(broadcast_callback: Callable[[dict], Awaitable[None]]):
    """Consume messages from the queue and forward them via broadcast_callback."""
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    channel = await connection.channel()
    queue = await channel.declare_queue(QUEUE_NAME, durable=True)

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                try:
                    payload = json.loads(message.body)
                    await broadcast_callback(payload)
                except Exception as e:
                    print(f"Consumer error: {e}")