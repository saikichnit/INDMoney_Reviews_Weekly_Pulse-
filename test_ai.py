import sys
import os
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

from services.discovery_service.service import DiscoveryService
from services.classification_service.service import ClassificationService
from services.note_service.service import NoteService

reviews = [{"review_text": "The app is great but taking too long to withdraw."}]
ds = DiscoveryService()
cs = ClassificationService()
ns = NoteService()

print("Discovering...")
try:
    signals = ds.discover_signals(reviews)
    print(signals)
except Exception as e:
    print(f"Error: {e}")

print("Classifying...")
try:
    themes = cs.classify_themes(signals)
    print(themes)
except Exception as e:
    print(f"Error: {e}")

print("Generating note...")
try:
    note = ns.generate_note(themes.get("themes", []), reviews)
    print(note)
except Exception as e:
    print(f"Error: {e}")
