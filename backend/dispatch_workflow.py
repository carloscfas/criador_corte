#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.workers.tasks.video_tasks import process_video_workflow

video_id = "05cc83e6-4e08-44ad-b0ee-4e7e7f011b6f"
print(f"Disparando workflow para vídeo {video_id}")
result = process_video_workflow.delay(video_id)
print(f"Task ID: {result.id}")
print("Workflow disparado com sucesso!")
