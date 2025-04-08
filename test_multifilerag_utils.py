#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for the MultiFileRAG utilities module.

This module contains tests for the functions in multifilerag_utils.py.
"""

import os
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import json
from pathlib import Path

# Import the module to test
from multifilerag_utils import (
    get_server_url, get_documents, get_document_counts,
    get_documents_by_status, get_failed_documents,
    get_pipeline_status, delete_document, upload_document,
    scan_for_documents, get_graph, query,
    check_ollama_status, check_model_status, check_nvidia_gpu,
    ensure_directories, check_graph_file, restart_server,
    print_document_status, wait_for_processing
)


class TestServerUrlFunctions(unittest.TestCase):
    """Test functions related to server URL handling."""

    def test_get_server_url_default(self):
        """Test get_server_url with default values."""
        with patch.dict(os.environ, {}, clear=True):
            url = get_server_url()
            self.assertEqual(url, "http://localhost:9621")

    def test_get_server_url_custom(self):
        """Test get_server_url with custom values."""
        with patch.dict(os.environ, {"HOST": "example.com", "PORT": "8080"}, clear=True):
            url = get_server_url()
            self.assertEqual(url, "http://example.com:8080")


class TestDocumentFunctions(unittest.TestCase):
    """Test functions related to document handling."""

    @patch('multifilerag_utils.requests.get')
    def test_get_documents_success(self, mock_get):
        """Test get_documents with successful response."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"statuses": {"PROCESSED": [{"id": "1"}]}}
        mock_get.return_value = mock_response

        # Call function
        result = get_documents("http://test-server")

        # Verify
        mock_get.assert_called_once_with("http://test-server/documents", timeout=30)
        self.assertEqual(result, {"statuses": {"PROCESSED": [{"id": "1"}]}})

    @patch('multifilerag_utils.requests.get')
    def test_get_documents_error(self, mock_get):
        """Test get_documents with error response."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Server error"
        mock_get.return_value = mock_response

        # Call function
        result = get_documents("http://test-server")

        # Verify
        self.assertIsNone(result)

    @patch('multifilerag_utils.requests.get')
    def test_get_documents_exception(self, mock_get):
        """Test get_documents with exception."""
        # Mock exception
        mock_get.side_effect = Exception("Connection error")

        # Call function
        result = get_documents("http://test-server")

        # Verify
        self.assertIsNone(result)

    @patch('multifilerag_utils.get_documents')
    def test_get_document_counts_success(self, mock_get_documents):
        """Test get_document_counts with successful response."""
        # Mock response
        mock_get_documents.return_value = {
            "statuses": {
                "PENDING": [{"id": "1"}],
                "PROCESSING": [{"id": "2"}, {"id": "3"}],
                "PROCESSED": [{"id": "4"}, {"id": "5"}, {"id": "6"}],
                "FAILED": [{"id": "7"}]
            }
        }

        # Call function
        result = get_document_counts("http://test-server")

        # Verify
        self.assertEqual(result, {
            "PENDING": 1,
            "PROCESSING": 2,
            "PROCESSED": 3,
            "FAILED": 1,
            "TOTAL": 7
        })

    @patch('multifilerag_utils.get_documents')
    def test_get_document_counts_error(self, mock_get_documents):
        """Test get_document_counts with error."""
        # Mock error
        mock_get_documents.return_value = None

        # Call function
        result = get_document_counts("http://test-server")

        # Verify
        self.assertEqual(result, {"error": "Failed to get documents"})

    @patch('multifilerag_utils.get_documents')
    def test_get_documents_by_status(self, mock_get_documents):
        """Test get_documents_by_status."""
        # Mock response
        mock_get_documents.return_value = {
            "statuses": {
                "PENDING": [{"id": "1"}],
                "PROCESSING": [{"id": "2"}, {"id": "3"}],
                "PROCESSED": [{"id": "4"}, {"id": "5"}, {"id": "6"}],
                "FAILED": [{"id": "7"}]
            }
        }

        # Call function
        result = get_documents_by_status("PROCESSED", "http://test-server")

        # Verify
        self.assertEqual(result, [{"id": "4"}, {"id": "5"}, {"id": "6"}])

    @patch('multifilerag_utils.get_documents')
    def test_get_failed_documents(self, mock_get_documents):
        """Test get_failed_documents."""
        # Mock response
        mock_get_documents.return_value = {
            "statuses": {
                "PENDING": [{"id": "1"}],
                "PROCESSING": [{"id": "2"}, {"id": "3"}],
                "PROCESSED": [{"id": "4"}, {"id": "5"}, {"id": "6"}],
                "FAILED": [{"id": "7"}]
            }
        }

        # Call function
        result = get_failed_documents("http://test-server")

        # Verify
        self.assertEqual(result, [{"id": "7"}])


class TestOllamaFunctions(unittest.TestCase):
    """Test functions related to Ollama."""

    @patch('multifilerag_utils.requests.get')
    def test_check_ollama_status_success(self, mock_get):
        """Test check_ollama_status with successful response."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"version": "0.1.0"}
        mock_get.return_value = mock_response

        # Call function
        is_running, version = check_ollama_status("http://test-ollama")

        # Verify
        mock_get.assert_called_once_with("http://test-ollama/api/version")
        self.assertTrue(is_running)
        self.assertEqual(version, "0.1.0")

    @patch('multifilerag_utils.requests.get')
    def test_check_ollama_status_error(self, mock_get):
        """Test check_ollama_status with error response."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        # Call function
        is_running, version = check_ollama_status("http://test-ollama")

        # Verify
        self.assertFalse(is_running)
        self.assertEqual(version, "Status code: 500")

    @patch('multifilerag_utils.requests.get')
    def test_check_ollama_status_exception(self, mock_get):
        """Test check_ollama_status with exception."""
        # Mock exception
        mock_get.side_effect = Exception("Connection error")

        # Call function
        is_running, version = check_ollama_status("http://test-ollama")

        # Verify
        self.assertFalse(is_running)
        self.assertEqual(version, "Connection error")


class TestDirectoryFunctions(unittest.TestCase):
    """Test functions related to directory management."""

    @patch('multifilerag_utils.Path.mkdir')
    @patch.dict(os.environ, {"INPUT_DIR": "/test/inputs", "WORKING_DIR": "/test/rag_storage"}, clear=True)
    def test_ensure_directories(self, mock_mkdir):
        """Test ensure_directories."""
        # Call function
        ensure_directories()

        # Verify
        self.assertEqual(mock_mkdir.call_count, 2)
        mock_mkdir.assert_any_call(parents=True, exist_ok=True)

    def test_check_graph_file_exists(self):
        """Test check_graph_file when file exists."""
        # Create temporary file
        with tempfile.NamedTemporaryFile() as temp_file:
            # Write some content
            temp_file.write(b"test content")
            temp_file.flush()

            # Mock environment and path
            with patch.dict(os.environ, {"WORKING_DIR": os.path.dirname(temp_file.name)}, clear=True):
                with patch('os.path.join', return_value=temp_file.name):
                    # Call function
                    result = check_graph_file()

                    # Verify
                    self.assertTrue(result)

    def test_check_graph_file_not_exists(self):
        """Test check_graph_file when file does not exist."""
        # Mock environment and path
        with patch.dict(os.environ, {"WORKING_DIR": "/nonexistent"}, clear=True):
            with patch('os.path.exists', return_value=False):
                # Call function
                result = check_graph_file()

                # Verify
                self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
