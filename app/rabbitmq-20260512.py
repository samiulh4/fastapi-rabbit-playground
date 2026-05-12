import aio_pika
import asyncio

async def send_direct_message_to_queue():
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
    channel = await connection.channel()
    queue = await channel.declare_queue("rabbitmq_playground_queue", durable=True)
    await channel.default_exchange.publish(
        aio_pika.Message(body=b"Hello RabbitMQ"),
        routing_key=queue.name
    )
    print("Message sent!")

async def send_message_using_exchange():
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
    channel = await connection.channel()
    exchange = await channel.declare_exchange(
    "rabbitmq_playground_exchange",
    aio_pika.ExchangeType.DIRECT
    )
    queue = await channel.declare_queue("rabbitmq_playground_queue", durable=True)
    await queue.bind(exchange, routing_key="message.create")
    await exchange.publish(
    aio_pika.Message(body=b"Task Created"),
    routing_key="message.create"
   )   

async def consume():
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
    channel = await connection.channel()

    queue = await channel.declare_queue("rabbitmq_playground_queue", durable=True)

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                print("Received:", message.body)