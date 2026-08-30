# AI Patient Education Assistant

A Python-based healthcare patient-education application that combines
local large language models (LLMs) with reliable medical information
from MedlinePlus, a service of the U.S. National Library of Medicine.

## Overview

The AI Patient Education Assistant is designed to provide general,
easy-to-understand healthcare education while incorporating basic
safety controls.

The application does not diagnose medical conditions or provide
personalized treatment recommendations.

## Key Features

- Healthcare topic input through a command-line interface
- Emergency symptom detection
- Personal medical question detection
- Medical information retrieval from MedlinePlus
- Local AI-generated patient education using Ollama
- Source-aware prompting
- Prevention of unsupported AI responses when a reliable medical
  source cannot be found
- Plain-language healthcare explanations
- Error handling for unavailable AI services

## Safety Features

The application performs safety checks before sending a topic to
the AI model.

### Emergency Detection

Potential emergency topics such as:

- Chest pain
- Difficulty breathing
- Heart attack
- Stroke
- Severe bleeding
- Unconsciousness
- Overdose

are intercepted before AI-generated information is provided.

The application directs users to seek immediate medical attention
instead.

### Personal Medical Questions

Questions such as:

- "Do I have diabetes?"
- "What medication should I take?"
- "What should I do about my symptoms?"

are intercepted because the application cannot safely diagnose
conditions or provide personalized medical treatment.

### Source Validation

The application queries MedlinePlus before generating educational
content.

If no relevant MedlinePlus information is found, the application
does not ask the AI model to generate an answer from unsupported
knowledge.

Instead, it displays:

"NO RELIABLE MEDICAL SOURCE FOUND"

This reduces the risk of presenting unsupported information as
authoritative medical guidance.

## Technology

- Python
- Requests
- XML parsing
- Regular expressions
- MedlinePlus API
- Ollama
- Llama 3.2
- Local LLM inference

## Architecture

User Input
    ↓
Safety Screening
    ↓
Emergency Check
    ↓
Personal Medical Question Check
    ↓
MedlinePlus Search
    ↓
Reliable Medical Information
    ↓
Source-Aware AI Prompt
    ↓
Local Llama 3.2 Model
    ↓
Patient-Friendly Educational Response

## Example

### General Healthcare Question

Input:

"What is asthma?"

The application retrieves information about asthma from MedlinePlus
and provides a simplified educational explanation.

### Emergency Question

Input:

"I have chest pain"

The application detects the potential emergency and does not send
the request to the language model.

### Personal Medical Question

Input:

"Do I have diabetes?"

The application explains that it cannot determine whether the user
has a medical condition.

### Unsupported Topic

Input:

"xyzabc123"

The application reports that no reliable medical source was found.

## Running the Application

Install the required Python package:

```bash
pip3 install -r requirements.txt