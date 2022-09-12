from sharkfin.utilities import *
from sharkfin.markets import AbstractMarket
import numpy as np
import json
#import pika
import uuid
import os
import time
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from azure.servicebus.management import ServiceBusAdministrationClient

class AzureRabbitMQMarket(AbstractMarket):

    dividend_growth_rate = None

    dividend_std = None

    dividends = None

    prices = None


    def __init__(self,
        session_id,
        host='localhost',
        dividend_growth_rate = 1.000628,
        dividend_std = 0.011988,
        price_to_dividend_ratio = 60 / 0.05,
        ):

		self.simulation_price_scale = 1
		self.default_sim_price = 100
		self.sample = 0
		self.seeds = []
		self.latest_price = None
		self.prices = [self.default_sim_price]
        self.price_to_dividend_ratio = price_to_dividend_ratio
        self.dividends = [self.default_sim_price / self.price_to_dividend_ratio]
        self.dividend_growth_rate = dividend_growth_rate
        self.dividend_std = dividend_std
		self.rpc_session_id = session_id
		self.rpc_send_queue_name = session_id +'sq'
		self.rpc_response_queue_name = session_id +'rq'
		self.rpc_host_name = host
		self.connection_str = host
		self.init_az_rpc()
		self.create_queues()

    def run_market(self, buy_sell=(0, 0)):

        self.last_buy_sell = buy_sell

        new_dividend = self.next_dividend()
        self.dividends.append(new_dividend)

        data = {
            'bl': buy_sell[0],
            'sl': buy_sell[1],
            'dividend' : new_dividend,
            'end_simulation': False
            }

        self.response = None

        # find out how to send a data message properly and wait and receive a message ???
        self.new_rpc_message(data)

        print('waiting for response...')


        print('response received')

        self.latest_price = float(self.response)
        self.prices.append(float(self.response))

        return self.latest_price, new_dividend

    def get_simulation_price(self, buy_sell=(0, 0)):
        return self.latest_price

    def daily_rate_of_return(self, buy_sell=None):
        # same as PNL class. Should this be put in the abstract base class?
        # need different scaling for AMMPS vs PNL, this needs to be changed.

        if buy_sell is None:
            buy_sell = self.last_buy_sell

        last_sim_price = self.get_simulation_price(buy_sell=buy_sell)

        if last_sim_price is None:
            last_sim_price = self.default_sim_price

        # ror = (last_sim_price * self.simulation_price_scale - 100) / 100
        ror = (self.latest_price - self.prices[-2])/self.prices[-2]

        # adjust to calibrated NetLogo to S&P500
        # do we need to calibrate AMMPS to S&P as well?

        # modularize calibration
        # ror = self.sp500_std * (ror - self.netlogo_ror) / self.netlogo_std + self.sp500_ror

        return ror

	#method to initialize Azure Service Bus Clients for messageing and managment
	def init_az_rpc(self):
		self.service_bus_mgmt_client = ServiceBusAdministrationClient.from_connection_string(self.connection_str)
		self.service_bus_message_client = ServiceBusClient.from_connection_string(conn_str=self.connection_str, logging_enable=True)

	#method to create the required sending and response queues for RPC pattern
	def create_queues(self):
		#create queue for sharkfin to send daily values
		self.service_bus_mgmt_client.create_queue(self.rpc_send_queue_name, max_delivery_count=10, dead_lettering_on_message_expiration=True)
		#create queue for amps response -
		self.service_bus_mgmt_client.create_queue(self.rpc_response_queue_name, max_delivery_count=10, dead_lettering_on_message_expiration=True)

	#method to instanciate a well-formed service bus message. requires passing json object as msg_body parameter
	def new_rpc_message(self,msg_body):
		msgdata = json.dumps(msg_body)
		self.service_bus_message = ServiceBusMessage(
		msgdata,
		session_id = self.rpc_session_id,
		reply_to = self.rpc_response_queue_name,
		reply_to_session_id = self.rpc_session_id,
		application_properties = {'placeholdermetadata': 'custom_data_example_if_needed'})

	#method to send a service bus message
	def send_rpc_message(self):
		sender = self.service_bus_message_client.get_queue_sender(queue_name=self.rpc_send_queue_name)
		result = sender.send_messages(self.service_bus_message)
		print (f"Sent RPC message to consumer queue {self.rpc_send_queue_name} await reply into response queue: {self.rpc_response_queue_name}...")
		return result

	def get_rpc_response(self):
		receiver = self.service_bus_message_client.get_queue_receiver(queue_name=self.rpc_response_queue_name, max_wait_time=5)
		for msg in receiver:
			self.response = body
		print("Received: " + str(body))
		receiver.complete_message(msg)
