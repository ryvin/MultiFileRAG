#!/usr/bin/env python3
"""
Script to improve query processing for resume information.
This script will:
1. Test different query modes to find the best one for resume information
2. Create a custom prompt template for resume-related queries
3. Provide recommendations for improving resume information retrieval
"""

import os
import sys
import json
import requests
import time
from pathlib import Path

def test_query_modes(query, server_url="http://localhost:9621"):
    """Test different query modes for a specific query."""
    modes = ["naive", "local", "global", "hybrid", "mix"]
    results = {}
    
    print(f"Testing query modes for: '{query}'")
    
    for mode in modes:
        try:
            print(f"\nTesting mode: {mode}")
            response = requests.post(
                f"{server_url}/query", 
                json={"query": query, "mode": mode},
                timeout=60
            )
            
            if response.status_code != 200:
                print(f"Error: Failed to query with mode {mode}. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                results[mode] = {"error": response.text}
                continue
            
            result = response.json()
            response_text = result.get("response", "")
            
            # Save the response
            results[mode] = {"response": response_text}
            
            # Print a summary
            print(f"Response length: {len(response_text)} characters")
            print(f"First 100 characters: {response_text[:100]}...")
            
            # Analyze the response quality
            quality_score = analyze_response_quality(response_text, query)
            results[mode]["quality_score"] = quality_score
            print(f"Quality score: {quality_score}/10")
        
        except Exception as e:
            print(f"Error testing mode {mode}: {str(e)}")
            results[mode] = {"error": str(e)}
    
    # Determine the best mode
    best_mode = None
    best_score = -1
    
    for mode, result in results.items():
        if "quality_score" in result and result["quality_score"] > best_score:
            best_score = result["quality_score"]
            best_mode = mode
    
    if best_mode:
        print(f"\nBest query mode for resume information: {best_mode} (Score: {best_score}/10)")
    else:
        print("\nCould not determine the best query mode.")
    
    return results, best_mode

def analyze_response_quality(response, query):
    """Analyze the quality of a response for a resume-related query."""
    # Initialize score
    score = 5
    
    # Check for relevant keywords based on the query
    query_keywords = {
        "education": ["education", "university", "degree", "bachelor", "master", "phd", "school"],
        "experience": ["experience", "work", "job", "position", "role", "company", "employer"],
        "skills": ["skills", "abilities", "competencies", "proficiencies", "expertise", "knowledge"],
        "certifications": ["certification", "certificate", "certified", "license", "accreditation"],
        "projects": ["project", "initiative", "development", "implementation", "deployment"],
    }
    
    # Determine which keyword sets to check based on the query
    keywords_to_check = []
    for category, keywords in query_keywords.items():
        if any(word in query.lower() for word in [category] + keywords):
            keywords_to_check.extend(keywords)
    
    # If no specific categories were found in the query, check all keywords
    if not keywords_to_check:
        for keywords in query_keywords.values():
            keywords_to_check.extend(keywords)
    
    # Check for presence of relevant keywords
    keyword_count = sum(1 for keyword in keywords_to_check if keyword.lower() in response.lower())
    keyword_score = min(3, keyword_count / 3)
    score += keyword_score
    
    # Check for structure (sections, bullet points)
    if "###" in response or "##" in response:
        score += 1
    if "-" in response or "*" in response:
        score += 0.5
    
    # Check for comprehensiveness
    if len(response) > 500:
        score += 1
    elif len(response) < 100:
        score -= 2
    
    # Check for references
    if "reference" in response.lower() or "[kg]" in response.lower():
        score += 0.5
    
    # Cap the score at 10
    return min(10, score)

def create_custom_prompt(server_url="http://localhost:9621"):
    """Create a custom prompt template for resume-related queries."""
    try:
        # Define the custom prompt
        custom_prompt = """
You are an AI assistant with access to a knowledge graph containing information about Raul Pineda's resume, work experience, education, and skills. When answering questions about Raul Pineda's professional background, please:

1. Include specific details about his education, work experience, skills, and certifications
2. Organize the information into clear sections with headings
3. Mention the companies he has worked for and his roles
4. Include dates when available
5. List his skills and areas of expertise
6. Cite the sources of information using [KG] references

Always provide comprehensive information from all available sources in the knowledge graph.
"""
        
        # TODO: In a real implementation, we would save this custom prompt to be used by the system
        # For now, we'll just print it as a recommendation
        
        print("Custom prompt template for resume-related queries:")
        print(custom_prompt)
        
        return True
    
    except Exception as e:
        print(f"Error creating custom prompt: {str(e)}")
        return False

def test_specific_queries(server_url="http://localhost:9621"):
    """Test specific resume-related queries."""
    queries = [
        "Tell me about Raul Pineda's education and qualifications",
        "What is Raul Pineda's work experience?",
        "What skills does Raul Pineda have?",
        "What companies has Raul Pineda worked for?",
        "Tell me about Raul Pineda's role at Leadingbit Solutions",
        "What certifications does Raul Pineda have?",
        "What is Raul Pineda's background in cloud computing?",
        "Tell me about Raul Pineda's experience with AI and machine learning",
        "What is Raul Pineda's experience with security compliance?",
        "Tell me about Raul Pineda's open source contributions"
    ]
    
    # Find the best query mode first
    _, best_mode = test_query_modes(
        "What information is available about Raul Pineda's resume?", 
        server_url
    )
    
    if not best_mode:
        best_mode = "hybrid"  # Default to hybrid if we couldn't determine the best mode
    
    print(f"\nTesting specific resume-related queries using {best_mode} mode:")
    
    for i, query in enumerate(queries):
        try:
            print(f"\n{i+1}. Query: '{query}'")
            response = requests.post(
                f"{server_url}/query", 
                json={"query": query, "mode": best_mode},
                timeout=60
            )
            
            if response.status_code != 200:
                print(f"Error: Failed to query. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                continue
            
            result = response.json()
            response_text = result.get("response", "")
            
            # Print a summary
            print(f"Response length: {len(response_text)} characters")
            print(f"First 100 characters: {response_text[:100]}...")
            
            # Analyze the response quality
            quality_score = analyze_response_quality(response_text, query)
            print(f"Quality score: {quality_score}/10")
        
        except Exception as e:
            print(f"Error testing query: {str(e)}")
    
    return True

def improve_resume_queries():
    """Improve query processing for resume information."""
    server_url = "http://localhost:9621"
    
    print("=== Resume Query Improvement ===\n")
    
    # Step 1: Test different query modes
    print("Step 1: Testing different query modes...")
    test_query_modes(
        "What information is available about Raul Pineda's resume, including his education, experience, and skills?",
        server_url
    )
    
    # Step 2: Create a custom prompt template
    print("\nStep 2: Creating a custom prompt template...")
    create_custom_prompt(server_url)
    
    # Step 3: Test specific resume-related queries
    print("\nStep 3: Testing specific resume-related queries...")
    test_specific_queries(server_url)
    
    # Step 4: Provide recommendations
    print("\n=== Recommendations for Improving Resume Queries ===")
    print("1. Use the best query mode identified above for resume-related queries")
    print("2. Include specific keywords in your queries (education, experience, skills, etc.)")
    print("3. Be specific about what aspect of the resume you're interested in")
    print("4. Consider using the custom prompt template for resume-related queries")
    print("5. If information is still missing, try reprocessing the resume documents with a different LLM model")

if __name__ == "__main__":
    improve_resume_queries()
