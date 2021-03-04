#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

from dotenv import load_dotenv
from faunadb import query as q
from faunadb.client import FaunaClient


def info_collection(resp, collection: str):
    if resp:
        print(f"Collection `{collection}` created.")
    else:
        print(f"Error creating `{collection}` collection.")


def info_index(resp, index: str):
    if resp:
        print(f"Index `{index}` created.")
    else:
        print(f"Error creating `{index}` index.")


load_dotenv()
secret = os.getenv("FAUNADB_SECRET_KEY")

if secret is None:
    print("Token not found ...")
    sys.exit(0)

client = FaunaClient(secret=secret)

# Creo la colección de Events
try:
    resp = client.query(
        q.create_collection({
            "name": "Events",
        })
    )
    info_collection(resp, "Events")
except:
    print("The `Events` collection already exists.")

# Creo un indice general para buscar todos los documentos de Events
try:
    resp = client.query(
        q.create_index(
            {
                "name": "all_events",
                "source": q.collection("Events")
            }
        )
    )
    info_index(resp, "all_events")
except:
    print("The `all_events` index already exists.")

# Index para buscar todos los documentos
# que contengan el campo time y devuelve [{time, ref}]
try:
    client.query(
        q.create_index(
            {
                "name": "all_events_by_time",
                "source": q.collection("Events"),
                "values": [
                    {"field": ["data", "time"]},
                    {"field": ["ref"]}
                ]
            }
        )
    )
    info_index(resp, "all_events_by_time")
except:
    print("The `all_events_by_time_range` Index already exists.")

# Index para buscar por author
try:
    client.query(
        q.create_index(
            {
                "name": "events_by_author",
                "source": q.collection("Events"),
                "terms": [
                    {"field": ["data", "author"]}
                ]
            }
        )
    )
    info_index(resp, "events_by_author")
except:
    print("The `events_by_author` index already exists.")

# Index para buscar por id y author
try:
    client.query(
        q.create_index(
            {
                "name": "event_by_id_and_author",
                "source": q.collection("Events"),
                "terms": [
                    {"field": ["ref"]},
                    {"field": ["data", "author"]}
                ]
            }
        )
    )
    info_index(resp, "event_by_id_and_author")
except:
    print("The `event_by_id_and_author` index already exists.")


# Creo la colección de FAQs
try:
    resp = client.query(
        q.create_collection({
            "name": "FAQs",
        })
    )
    info_collection(resp, "FAQs")
except:
    print("The `FAQs` collection already exists.")

# Index general para buscar todos los documentos de FAQs
try:
    resp = client.query(
        q.create_index(
            {
                "name": "all_faqs",
                "source": q.collection("FAQs")
            }
        )
    )
    info_index(resp, "all_faqs")

except:
    print("The `all_faqs` index already exists.")

# Creo la colección de Polls
try:
    resp = client.query(
        q.create_collection({
            "name": "Polls",
        })
    )
    info_collection(resp, "Polls")
except:
    print("The `Polls` collection already exists.")

# Index general para buscar una encuesta por id de comentario de discord
try:
    resp = client.query(
        q.create_index(
            {
                "name": "poll_by_discord_id",
                "source": q.collection("Polls"),
                "terms": [{"field": ["data", "id"]}],
                "values": [
                    {"field": ["data", "type"]},
                    {"field": ["data", "is_active"]},
                    {"field": ["data", "users_voted"]},
                    {"field": ["data", "votes_count"]},
                    {"field": ["data", "question"]},
                    {"field": ["data", "author"]},
                    {"field": ["data", "avatar_url"]},
                ],
            }
        )
    )
    info_index(resp, "poll_by_discord_id")

except:
    print("The `poll_by_discord_id` index already exists.")
