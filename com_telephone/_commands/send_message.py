#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import sys
import urllib.request
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def send_message(text, project="roberto"):
    """Envoyer un message via l'API /send avec encodage UTF-8 correct"""
    data = {
        "text": text,
        "project": project
    }

    json_data = json.dumps(data, ensure_ascii=False).encode('utf-8')

    req = urllib.request.Request(
        'http://127.0.0.1:5000/send',
        data=json_data,
        headers={'Content-Type': 'application/json; charset=utf-8'},
        method='POST'
    )

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            print(f"✅ Message envoyé: {result}")
            return result
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python send_message.py '<message>' [projet]")
        sys.exit(1)

    text = sys.argv[1]
    project = sys.argv[2] if len(sys.argv) > 2 else "roberto"

    send_message(text, project)
