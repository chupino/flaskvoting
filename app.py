from flask import Flask, render_template, request, make_response, g
from redis import Redis
from kafka import KafkaProducer
import os
import socket
import random
import json
import logging

option_a = os.getenv('OPTION_A', "Cats")
option_b = os.getenv('OPTION_B', "Dogs")
hostname = socket.gethostname()

app = Flask(__name__)

gunicorn_error_logger = logging.getLogger('gunicorn.error')
app.logger.handlers.extend(gunicorn_error_logger.handlers)
app.logger.setLevel(logging.INFO)

# Configurar Kafka Producer
def get_kafka_producer():
    if not hasattr(g, 'kafka_producer'):
        g.kafka_producer = KafkaProducer(
            bootstrap_servers='35.170.192.17',
            value_serializer=lambda v: json.dumps(v).encode('utf-8')  # Serializar los datos como JSON
        )
    return g.kafka_producer

@app.route("/", methods=['POST','GET'])
def hello():
    voter_id = request.cookies.get('voter_id')
    if not voter_id:
        voter_id = hex(random.getrandbits(64))[2:-1]

    vote = None

    if request.method == 'POST':
        producer = get_kafka_producer()
        vote = request.form['vote']
        app.logger.info('Received vote for %s', vote)
        
        # Crear los datos del voto
        data = {'voter_id': voter_id, 'vote': vote}
        
        # Enviar los datos a Kafka
        producer.send('testtopic', value=data)
        #producer.flush()

    resp = make_response(render_template(
        'index.html',
        option_a=option_a,
        option_b=option_b,
        hostname=hostname,
        vote=vote,
    ))
    resp.set_cookie('voter_id', voter_id)
    return resp


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True, threaded=True)