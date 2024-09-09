import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from pce.google_drive import GoogleDrive
from datetime import timedelta
import pytest

@pytest.fixture
def google_drive():
    return GoogleDrive(os.path.join(os.path.dirname(__file__), "useful-cathode-435107-r6-c6ea48c620cb.json"))

def test_list_all(google_drive):
    print(google_drive.list_all_files())

def test_upload(google_drive):
    local_file = os.path.join(os.path.dirname(__file__), "Aligned.pdf")
    file_path = google_drive.upload_for_someone_read(local_file, expirationTime=timedelta(days=7))
    print(file_path)
"""
def test_download(google_drive):
    local_path = os.path.join(os.path.dirname(__file__), "test.pdf")
    google_drive.download_file("1dzOPhThuA0guvjWhcTpUbeHIfuGF-CwR", local_path)

def test_delete(google_drive):
    google_drive.delete_file('1VmwEfXtTQMA9qirUl3WjhZoQ36SuHxYG')
"""