#!/usr/bin/env python3
"""
Script to check if specific documents were properly processed and their content is available.
This script uses the multifilerag_utils module for API interaction.
"""

from multifilerag_utils import get_documents, get_server_url, query

def check_document_content(doc_name, server_url=None):
    """Check if a specific document was processed and its content is available."""
    # Use default server URL if not provided
    if server_url is None:
        server_url = get_server_url()

    # Get all document statuses
    data = get_documents(server_url)
    if not data:
        return False

    # Collect all documents from all statuses
    all_docs = []
    for docs in data.get("statuses", {}).values():
        all_docs.extend(docs)

    # Find documents matching the name
    matching_docs = [
        doc for doc in all_docs
        if doc_name.lower() in doc.get("file_path", "").lower()
    ]

    if not matching_docs:
        print(f"Document '{doc_name}' not found in the system.")
        return False

    # Print details of matching documents
    print(f"Found {len(matching_docs)} documents matching '{doc_name}':")
    _print_document_details(matching_docs)

    # Check if any of the documents were processed successfully
    processed_docs = [doc for doc in matching_docs if doc.get("status") == "PROCESSED"]
    if processed_docs:
        processed_count = len(processed_docs)
        total_count = len(matching_docs)
        print(f"\n✅ {processed_count} out of {total_count} documents were processed successfully.")
        return True

    print("\n❌ None of the matching documents were processed successfully.")
    return False


def _print_document_details(docs):
    """Helper function to print document details."""
    for i, doc in enumerate(docs):
        # Extract document properties
        doc_id = doc.get("id", "Unknown")
        file_path = doc.get("file_path", "Unknown")
        status = doc.get("status", "Unknown")
        created_at = doc.get("created_at", "Unknown")
        updated_at = doc.get("updated_at", "Unknown")
        chunks_count = doc.get("chunks_count", 0)
        error = doc.get("error", "")

        # Print document details
        print(f"\n{i+1}. Document: {file_path}")
        print(f"   ID: {doc_id}")
        print(f"   Status: {status}")
        print(f"   Created: {created_at}")
        print(f"   Updated: {updated_at}")
        print(f"   Chunks: {chunks_count}")
        if error:
            print(f"   Error: {error}")

def check_text_chunks(server_url=None):
    """Check the text chunks in the system to see if they contain resume information."""
    # Use default server URL if not provided
    if server_url is None:
        server_url = get_server_url()

    # Query for resume-related information
    query_terms = ["resume", "Raul Pineda", "experience", "education", "skills"]

    for term in query_terms:
        print(f"\nSearching for chunks containing '{term}'...")
        try:
            # Use the query function from multifilerag_utils
            response_text = query(term, mode="naive", server_url=server_url)

            # Check if the response contains meaningful information
            if len(response_text) > 100:
                print(f"Found information related to '{term}':")
                print(f"Response length: {len(response_text)} characters")
                print(f"First 200 characters: {response_text[:200]}...")
            else:
                print(f"No significant information found for '{term}'")
        except ConnectionError as e:
            print(f"Connection error querying for '{term}': {str(e)}")
        except TimeoutError as e:
            print(f"Timeout error querying for '{term}': {str(e)}")
        except ValueError as e:
            print(f"Value error querying for '{term}': {str(e)}")
        except KeyError as e:
            print(f"Key error querying for '{term}': {str(e)}")
        except Exception as e:
            print(f"Unexpected error querying for '{term}': {str(e)}")

def main():
    """Main entry point for document content checking."""
    # Get server URL from environment or use default
    server_url = get_server_url()

    print("=== Document Content Check ===\n")

    # Check for resume documents
    print("Checking for resume documents...")
    resume_found = check_document_content("resume", server_url)

    # Check for Raul Pineda documents
    print("\nChecking for documents related to Raul Pineda...")
    raul_found = check_document_content("raul", server_url)

    # Check text chunks for resume content
    print("\nChecking text chunks for resume content...")
    check_text_chunks(server_url)

    # Print recommendations
    print("\n=== Recommendations ===")
    if not resume_found and not raul_found:
        print("1. Upload the resume documents again")
        print("2. Make sure the documents are in a supported format (PDF, DOCX)")
        print("3. Check if the LLM model is properly processing the documents")
    elif not resume_found or not raul_found:
        print("1. Some documents were found but not all")
        print("2. Try reprocessing the missing documents")
    else:
        print("1. Documents were found and processed")
        print("2. If information is still missing, try improving entity extraction")

if __name__ == "__main__":
    main()
