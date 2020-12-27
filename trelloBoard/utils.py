import requests
import json
from .models import Board


class TrelloUtils:

    def __init__(self):
        self.list_board = list()

