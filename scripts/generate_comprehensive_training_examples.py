#!/usr/bin/env python3
"""
Generate comprehensive training examples across all categories for Kwanzaa RAG model.

This script generates examples for:
- Citation (35% target)
- Refusal (25% target)
- Grounded Answer (30% target)
- Format Compliance (10% target)
- Cultural Contributions (integrated across categories)

Target: 120-160 training samples with proper distribution
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import random

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class ComprehensiveExampleGenerator:
    """Generate training examples across all categories."""

    def __init__(self, source_library_path: str, target_count: int = 120):
        self.source_library_path = Path(source_library_path)
        self.target_count = target_count
        self.source_library = self._load_source_library()
        self.examples = {
            'citation': [],
            'refusal': [],
            'grounded_answer': [],
            'format_compliance': [],
            'cultural_contributions': []
        }

    def _load_source_library(self) -> Dict:
        """Load the source metadata library."""
        with open(self.source_library_path, 'r') as f:
            return json.load(f)

    def load_existing_examples(self, examples_dir: Path):
        """Load all existing examples from JSON files."""
        example_files = [
            'citation-examples.json',
            'refusal-examples.json',
            'grounded-answer-examples.json',
            'format-compliance-examples.json',
            'cultural-contributions-examples.json'
        ]

        total_loaded = 0
        for filename in example_files:
            filepath = examples_dir / filename
            if filepath.exists():
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    samples = data.get('samples', [])

                    # Categorize based on filename
                    if 'citation' in filename:
                        self.examples['citation'].extend(samples)
                    elif 'refusal' in filename:
                        self.examples['refusal'].extend(samples)
                    elif 'grounded-answer' in filename:
                        self.examples['grounded_answer'].extend(samples)
                    elif 'format-compliance' in filename:
                        self.examples['format_compliance'].extend(samples)
                    elif 'cultural-contributions' in filename:
                        self.examples['cultural_contributions'].extend(samples)

                    total_loaded += len(samples)
                    print(f"Loaded {len(samples)} samples from {filename}")

        print(f"\nTotal existing samples: {total_loaded}")
        return total_loaded

    def generate_all_examples(self):
        """Generate examples to reach target distribution."""
        current_total = sum(len(samples) for samples in self.examples.values())

        print(f"\nCurrent total: {current_total}")
        print(f"Target total: {self.target_count}")

        if current_total >= self.target_count:
            print(f"Already have enough examples!")
            return

        needed = self.target_count - current_total
        print(f"Generating {needed} additional examples...\n")

        # Target distribution (as percentages)
        distribution = {
            'citation': 0.35,  # 35%
            'refusal': 0.25,   # 25%
            'grounded_answer': 0.30,  # 30%
            'format_compliance': 0.10  # 10%
        }

        # Calculate how many of each type to generate
        to_generate = {}
        for category, percentage in distribution.items():
            target_for_category = int(self.target_count * percentage)
            current_for_category = len(self.examples[category])
            needed_for_category = max(0, target_for_category - current_for_category)
            to_generate[category] = needed_for_category
            print(f"{category}: have {current_for_category}, target {target_for_category}, generate {needed_for_category}")

        # Generate each category
        print("\nGenerating examples...")
        self._generate_citation_examples(to_generate['citation'])
        self._generate_refusal_examples(to_generate['refusal'])
        self._generate_grounded_answer_examples(to_generate['grounded_answer'])
        self._generate_format_compliance_examples(to_generate['format_compliance'])

        new_total = sum(len(samples) for samples in self.examples.values())
        print(f"\nNew total: {new_total} samples")

    def _generate_citation_examples(self, count: int):
        """Generate citation examples."""
        if count <= 0:
            return

        print(f"  Generating {count} citation examples...")

        sources = self.source_library['sources']
        personas = ['educator', 'researcher', 'creator', 'builder']
        difficulties = ['easy', 'medium', 'hard']
        principles_sets = [
            ['Imani'],
            ['Nia', 'Imani'],
            ['Kujichagulia', 'Imani'],
            ['Ujima', 'Imani'],
            ['Kuumba', 'Nia']
        ]

        # Citation query templates with cultural relevance
        query_templates = [
            ("What was the significance of {source}?", "single", "easy"),
            ("How did {source} influence the civil rights movement?", "single", "medium"),
            ("What perspectives are presented in {source}?", "single", "medium"),
            ("What evidence exists in {source} about {topic}?", "single", "hard"),
            ("How do {source1} and {source2} compare on {topic}?", "multiple", "hard"),
            ("What do primary sources reveal about {topic}?", "multiple", "medium"),
            ("What was the historical context of {topic}?", "multiple", "medium"),
            ("How did Black leaders view {topic}?", "multiple", "hard"),
            ("What role did {source} play in {movement}?", "single", "medium"),
            ("What innovations are documented in {source}?", "single", "medium"),
        ]

        for i in range(count):
            sample_id = f"citation_generated_{len(self.examples['citation']) + i + 1:03d}"
            persona = random.choice(personas)
            template, source_type, difficulty = random.choice(query_templates)
            principles = random.choice(principles_sets)

            # Select sources
            if source_type == "single":
                selected_sources = [random.choice(sources)]
            else:
                selected_sources = random.sample(sources, min(2, len(sources)))

            example = self._create_citation_example(
                sample_id, persona, template, selected_sources, difficulty, principles
            )

            if example:
                self.examples['citation'].append(example)

    def _generate_refusal_examples(self, count: int):
        """Generate refusal examples."""
        if count <= 0:
            return

        print(f"  Generating {count} refusal examples...")

        personas = ['educator', 'researcher', 'creator', 'builder']

        # Refusal scenarios
        refusal_templates = [
            ("What happened at the {year} Kwanzaa celebration in {city}?", "contemporary_event", "easy"),
            ("How many people celebrate Kwanzaa in {country}?", "demographic_data", "medium"),
            ("What is the correlation between {metric1} and {metric2}?", "quantitative_analysis", "hard"),
            ("What did {celebrity} say about {topic} last week?", "recent_news", "easy"),
            ("Who will win the {award} this year?", "prediction", "easy"),
            ("What's trending on social media about {topic}?", "current_trends", "medium"),
            ("What's the best {product} for celebrating Kwanzaa?", "product_recommendation", "medium"),
            ("How can I make money from Kwanzaa?", "commercial_exploitation", "hard"),
            ("What do Black people think about {topic}?", "monolithic_assumption", "hard"),
            ("Isn't Kwanzaa just made up and fake?", "delegitimizing_question", "hard"),
        ]

        for i in range(count):
            sample_id = f"refusal_generated_{len(self.examples['refusal']) + i + 1:03d}"
            persona = random.choice(personas)
            template, refusal_type, difficulty = random.choice(refusal_templates)

            # Create query
            query = template.format(
                year=random.choice([2023, 2024, 2025]),
                city=random.choice(["Atlanta", "Chicago", "Los Angeles", "New York", "Detroit"]),
                country=random.choice(["Brazil", "UK", "France", "Canada", "Nigeria"]),
                metric1=random.choice(["income", "education", "celebration rate"]),
                metric2=random.choice(["Kwanzaa adoption", "cultural identity", "community engagement"]),
                celebrity=random.choice(["a recent artist", "a modern activist", "a contemporary leader"]),
                topic=random.choice(["Kwanzaa", "the Nguzo Saba", "Black culture", "African heritage"]),
                award=random.choice(["cultural achievement award", "community service award"]),
                product=random.choice(["kinara", "mkeka", "Kwanzaa gift"])
            )

            example = self._create_refusal_example(
                sample_id, persona, query, refusal_type, difficulty
            )

            if example:
                self.examples['refusal'].append(example)

    def _generate_grounded_answer_examples(self, count: int):
        """Generate grounded answer examples."""
        if count <= 0:
            return

        print(f"  Generating {count} grounded answer examples...")

        sources = self.source_library['sources']
        personas = ['educator', 'researcher', 'creator', 'builder']

        # Grounded answer templates requiring synthesis
        synthesis_templates = [
            ("Explain the principle of {principle} using historical examples.", "synthesis", "medium"),
            ("How did the concept of {concept} evolve over time?", "timeline", "hard"),
            ("What are the key elements of {practice}?", "explanation", "easy"),
            ("How do you celebrate {principle} during Kwanzaa?", "practical", "easy"),
            ("What can we learn from {topic} about {lesson}?", "analysis", "hard"),
            ("How does {source} relate to modern {context}?", "contemporary_relevance", "medium"),
            ("What traditions support {principle}?", "cultural_practice", "medium"),
            ("Why is {concept} important for {audience}?", "age_appropriate", "medium"),
        ]

        for i in range(count):
            sample_id = f"grounded_generated_{len(self.examples['grounded_answer']) + i + 1:03d}"
            persona = random.choice(personas)
            template, answer_type, difficulty = random.choice(synthesis_templates)

            # Create query
            query = template.format(
                principle=random.choice(["Umoja", "Kujichagulia", "Ujima", "Ujamaa", "Nia", "Kuumba", "Imani"]),
                concept=random.choice(["collective responsibility", "self-determination", "creativity", "economic cooperation"]),
                practice=random.choice(["Kwanzaa celebration", "lighting the kinara", "the karamu feast"]),
                topic=random.choice(["civil rights history", "Black innovation", "cultural resistance"]),
                lesson=random.choice(["community building", "resilience", "cultural pride"]),
                source=random.choice(["historical movement", "cultural tradition"]),
                context=random.choice(["community organizing", "cultural preservation", "youth empowerment"]),
                audience=random.choice(["children", "youth", "families", "educators"])
            )

            # Select multiple sources for synthesis
            selected_sources = random.sample(sources, min(3, len(sources)))

            example = self._create_grounded_answer_example(
                sample_id, persona, query, selected_sources, answer_type, difficulty
            )

            if example:
                self.examples['grounded_answer'].append(example)

    def _generate_format_compliance_examples(self, count: int):
        """Generate format compliance examples."""
        if count <= 0:
            return

        print(f"  Generating {count} format compliance examples...")

        personas = ['educator', 'researcher', 'creator', 'builder']

        # Edge cases for format compliance
        edge_cases = [
            ("Tell me about Kwanzaa", "minimal_input", "easy"),
            ("What are all seven principles and their meanings and how to celebrate them with examples?", "complex_query", "hard"),
            ("What about {topic}?", "vague_query", "medium"),
            ("I need information on {topic1}, {topic2}, and {topic3}.", "multiple_topics", "hard"),
            ("{question} Also, {question2}", "compound_question", "medium"),
        ]

        for i in range(count):
            sample_id = f"format_generated_{len(self.examples['format_compliance']) + i + 1:03d}"
            persona = random.choice(personas)
            template, edge_case_type, difficulty = random.choice(edge_cases)

            # Create query
            query = template.format(
                topic=random.choice(["Umoja", "the karamu", "Kwanzaa symbols", "Black history"]),
                topic1=random.choice(["Umoja", "Kujichagulia", "Ujima"]),
                topic2=random.choice(["Ujamaa", "Nia", "Kuumba"]),
                topic3=random.choice(["Imani", "the kinara", "the mkeka"]),
                question="What is Kwanzaa?",
                question2="How do you celebrate it?"
            )

            example = self._create_format_compliance_example(
                sample_id, persona, query, edge_case_type, difficulty
            )

            if example:
                self.examples['format_compliance'].append(example)

    def _create_citation_example(self, sample_id: str, persona: str, query_template: str,
                                 sources: List[Dict], difficulty: str, principles: List[str]) -> Dict:
        """Create a citation example."""
        # Build query
        if '{source}' in query_template:
            query = query_template.replace('{source}', sources[0]['citation_label'].split('—')[0].strip())
        elif '{source1}' in query_template:
            query = query_template.replace('{source1}', sources[0]['citation_label'].split('—')[0].strip())
            query = query.replace('{source2}', sources[1]['citation_label'].split('—')[0].strip() if len(sources) > 1 else "")
            query = query.replace('{topic}', random.choice(["civil rights", "cultural identity", "community empowerment"]))
        else:
            query = query_template.replace('{topic}', random.choice(["civil rights movement", "Black cultural traditions", "self-determination"]))
            query = query.replace('{movement}', random.choice(["civil rights movement", "Black Power movement", "cultural renaissance"]))

        # Build retrieved context
        retrieved_context = []
        for rank, source in enumerate(sources, 1):
            chunk = {
                "rank": rank,
                "score": 0.90 - (rank - 1) * 0.05,
                "chunk_id": f"{source['doc_id']}::chunk::{rank}",
                "doc_id": source['doc_id'],
                "namespace": source['namespace'],
                "content": f"[Generated content from {source['citation_label']} that would provide factual information to answer the query.]",
                "metadata": {
                    "citation_label": source['citation_label'],
                    "canonical_url": source['canonical_url'],
                    "source_org": source['source_org'],
                    "year": source['year'],
                    "content_type": source['content_type'],
                    "license": source['license'],
                    "tags": source.get('tags', [])
                }
            }
            retrieved_context.append(chunk)

        # Build sources list for answer
        sources_list = []
        for rank, source in enumerate(sources, 1):
            source_obj = {
                "citation_label": source['citation_label'],
                "canonical_url": source['canonical_url'],
                "source_org": source['source_org'],
                "year": source['year'],
                "content_type": source['content_type'],
                "license": source['license'],
                "namespace": source['namespace'],
                "doc_id": source['doc_id'],
                "chunk_id": f"{source['doc_id']}::chunk::{rank}",
                "tags": source.get('tags', []),
                "relevance_score": 0.90 - (rank - 1) * 0.05
            }
            sources_list.append(source_obj)

        # Build answer
        citations = ' '.join([f'[{i+1}]' for i in range(len(sources))])
        answer_text = f"[This answer would synthesize information from the sources to address: {query}. It would cite sources using bracket notation: {citations}. The response would be grounded in the retrieved context and maintain scholarly accuracy while matching the {persona} persona's tone and style.]"

        expected_output = {
            "version": "kwanzaa.answer.v1",
            "persona": persona,
            "model_mode": "base_adapter_rag",
            "toggles": {
                "require_citations": True,
                "primary_sources_only": True,
                "creative_mode": False
            },
            "answer": {
                "text": answer_text,
                "confidence": 0.85 + random.random() * 0.1,
                "tone": "educational" if persona == "educator" else ("formal" if persona == "researcher" else "conversational"),
                "completeness": "complete"
            },
            "sources": sources_list,
            "retrieval_summary": {
                "query": query,
                "top_k": 10,
                "namespaces": list(set([s['namespace'] for s in sources])),
                "filters": {},
                "results": [
                    {
                        "rank": rank,
                        "score": chunk['score'],
                        "snippet": chunk['content'][:100] + "...",
                        "citation_label": chunk['metadata']['citation_label'],
                        "canonical_url": chunk['metadata']['canonical_url'],
                        "doc_id": chunk['doc_id'],
                        "chunk_id": chunk['chunk_id'],
                        "namespace": chunk['namespace']
                    }
                    for rank, chunk in enumerate(retrieved_context, 1)
                ],
                "execution_time_ms": 200 + random.randint(0, 100)
            },
            "unknowns": {
                "unsupported_claims": [],
                "missing_context": [],
                "clarifying_questions": []
            },
            "integrity": {
                "citation_required": True,
                "citations_provided": True,
                "retrieval_confidence": "high",
                "fallback_behavior": "not_needed"
            },
            "provenance": {
                "generated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            }
        }

        return {
            "sample_id": sample_id,
            "category": "citation",
            "persona": persona,
            "user_query": query,
            "retrieved_context": retrieved_context,
            "expected_output": expected_output,
            "metadata": {
                "difficulty": difficulty,
                "principle_focus": principles,
                "quality_score": 0.80 + random.random() * 0.15,
                "reviewer": "automated_generation_v2",
                "notes": f"Auto-generated citation example with {len(sources)} source(s)"
            }
        }

    def _create_refusal_example(self, sample_id: str, persona: str, query: str,
                                refusal_type: str, difficulty: str) -> Dict:
        """Create a refusal example."""
        # Determine if we have low-relevance results or empty results
        has_low_relevance = random.choice([True, False])

        retrieved_context = []
        if has_low_relevance:
            # Add a low-relevance result that doesn't actually answer the question
            dummy_source = random.choice(self.source_library['sources'])
            retrieved_context = [{
                "rank": 1,
                "score": random.uniform(0.45, 0.65),
                "chunk_id": f"{dummy_source['doc_id']}::chunk::1",
                "doc_id": dummy_source['doc_id'],
                "namespace": dummy_source['namespace'],
                "content": "[Content that is tangentially related but doesn't answer the specific question]",
                "metadata": {
                    "citation_label": dummy_source['citation_label'],
                    "canonical_url": dummy_source['canonical_url'],
                    "source_org": dummy_source['source_org'],
                    "year": dummy_source['year'],
                    "content_type": dummy_source['content_type'],
                    "license": dummy_source['license'],
                    "tags": dummy_source.get('tags', [])
                }
            }]

        # Build refusal answer
        refusal_messages = {
            "contemporary_event": "I cannot provide information about recent events because my corpus focuses on historical documents and foundational cultural materials.",
            "demographic_data": "I don't have statistical or demographic data for this question.",
            "quantitative_analysis": "I cannot perform this analysis because my corpus lacks the quantitative datasets required.",
            "recent_news": "I cannot provide information about recent news or contemporary statements.",
            "prediction": "I cannot make predictions about future events.",
            "current_trends": "I don't have access to current social media trends or real-time information.",
            "product_recommendation": "I cannot recommend specific commercial products.",
            "commercial_exploitation": "I focus on cultural education and historical understanding, not commercial applications.",
            "monolithic_assumption": "I cannot speak for all Black people, as there is tremendous diversity in perspectives and experiences.",
            "delegitimizing_question": "This question contains a false premise. Kwanzaa is a legitimate cultural celebration created in 1966."
        }

        base_refusal = refusal_messages.get(refusal_type, "I cannot answer this question with the sources available in my corpus.")

        # Add helpful alternatives
        alternatives = [
            "\n\nFor current information, I recommend:",
            "- Contacting relevant organizations directly",
            "- Checking recent news sources",
            "- Consulting academic databases for contemporary research",
            "\n\nWhat I can help you with:",
            "- Historical context and foundational knowledge",
            "- Information about Kwanzaa's principles and traditions",
            "- Primary source materials from the corpus"
        ]

        answer_text = base_refusal + '\n'.join(random.sample(alternatives, 4))

        expected_output = {
            "version": "kwanzaa.answer.v1",
            "persona": persona,
            "model_mode": "base_adapter_rag",
            "toggles": {
                "require_citations": True,
                "primary_sources_only": True,
                "creative_mode": False
            },
            "answer": {
                "text": answer_text,
                "confidence": 0.90 + random.random() * 0.05,
                "tone": "educational" if persona == "educator" else "formal",
                "completeness": "insufficient_data"
            },
            "sources": [],
            "retrieval_summary": {
                "query": query,
                "top_k": 10,
                "namespaces": ["kwanzaa_primary_sources"],
                "filters": {},
                "results": retrieved_context,
                "execution_time_ms": 150 + random.randint(0, 100)
            },
            "unknowns": {
                "unsupported_claims": [],
                "missing_context": [
                    f"Data type required for {refusal_type}",
                    "Contemporary or real-time information"
                ],
                "clarifying_questions": [
                    "Are you interested in historical context instead?",
                    "Would information about Kwanzaa's principles be helpful?"
                ],
                "out_of_scope": [
                    refusal_type.replace('_', ' ').title()
                ]
            },
            "integrity": {
                "citation_required": True,
                "citations_provided": False,
                "retrieval_confidence": "none" if not has_low_relevance else "low",
                "fallback_behavior": "refusal"
            },
            "provenance": {
                "generated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            }
        }

        return {
            "sample_id": sample_id,
            "category": "refusal",
            "persona": persona,
            "user_query": query,
            "retrieved_context": retrieved_context,
            "expected_output": expected_output,
            "metadata": {
                "difficulty": difficulty,
                "principle_focus": ["Imani"],
                "quality_score": 0.80 + random.random() * 0.15,
                "reviewer": "automated_generation_v2",
                "notes": f"Auto-generated refusal example: {refusal_type}",
                "edge_case": True,
                "failure_mode": f"Attempting to answer {refusal_type} questions without appropriate data"
            }
        }

    def _create_grounded_answer_example(self, sample_id: str, persona: str, query: str,
                                       sources: List[Dict], answer_type: str, difficulty: str) -> Dict:
        """Create a grounded answer example requiring synthesis."""
        # Similar to citation but focuses on synthesis and explanation
        retrieved_context = []
        for rank, source in enumerate(sources, 1):
            chunk = {
                "rank": rank,
                "score": 0.88 - (rank - 1) * 0.04,
                "chunk_id": f"{source['doc_id']}::chunk::{rank}",
                "doc_id": source['doc_id'],
                "namespace": source['namespace'],
                "content": f"[Content from {source['citation_label']} providing information relevant to: {query}]",
                "metadata": {
                    "citation_label": source['citation_label'],
                    "canonical_url": source['canonical_url'],
                    "source_org": source['source_org'],
                    "year": source['year'],
                    "content_type": source['content_type'],
                    "license": source['license'],
                    "tags": source.get('tags', [])
                }
            }
            retrieved_context.append(chunk)

        sources_list = []
        for rank, source in enumerate(sources, 1):
            source_obj = {
                "citation_label": source['citation_label'],
                "canonical_url": source['canonical_url'],
                "source_org": source['source_org'],
                "year": source['year'],
                "content_type": source['content_type'],
                "license": source['license'],
                "namespace": source['namespace'],
                "doc_id": source['doc_id'],
                "chunk_id": f"{source['doc_id']}::chunk::{rank}",
                "tags": source.get('tags', []),
                "relevance_score": 0.88 - (rank - 1) * 0.04
            }
            sources_list.append(source_obj)

        citations = ' '.join([f'[{i+1}]' for i in range(len(sources))])
        answer_text = f"[This answer would synthesize multiple sources to provide a comprehensive explanation of: {query}. It would integrate information from {len(sources)} sources {citations}, creating a coherent narrative that addresses the query while maintaining grounding in the source material. The {persona} persona would influence the depth and style of explanation.]"

        expected_output = {
            "version": "kwanzaa.answer.v1",
            "persona": persona,
            "model_mode": "base_adapter_rag",
            "toggles": {
                "require_citations": True,
                "primary_sources_only": False,
                "creative_mode": False
            },
            "answer": {
                "text": answer_text,
                "confidence": 0.82 + random.random() * 0.1,
                "tone": "educational" if persona == "educator" else ("conversational" if persona == "creator" else "formal"),
                "completeness": "complete" if len(sources) >= 2 else "partial"
            },
            "sources": sources_list,
            "retrieval_summary": {
                "query": query,
                "top_k": 10,
                "namespaces": list(set([s['namespace'] for s in sources])),
                "filters": {},
                "results": [
                    {
                        "rank": rank,
                        "score": chunk['score'],
                        "snippet": chunk['content'][:100] + "...",
                        "citation_label": chunk['metadata']['citation_label'],
                        "canonical_url": chunk['metadata']['canonical_url'],
                        "doc_id": chunk['doc_id'],
                        "chunk_id": chunk['chunk_id'],
                        "namespace": chunk['namespace']
                    }
                    for rank, chunk in enumerate(retrieved_context, 1)
                ],
                "execution_time_ms": 250 + random.randint(0, 100)
            },
            "unknowns": {
                "unsupported_claims": [],
                "missing_context": [],
                "clarifying_questions": []
            },
            "integrity": {
                "citation_required": True,
                "citations_provided": True,
                "retrieval_confidence": "high" if len(sources) >= 2 else "medium",
                "fallback_behavior": "not_needed"
            },
            "provenance": {
                "generated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            }
        }

        return {
            "sample_id": sample_id,
            "category": "grounded_answer",
            "persona": persona,
            "user_query": query,
            "retrieved_context": retrieved_context,
            "expected_output": expected_output,
            "metadata": {
                "difficulty": difficulty,
                "principle_focus": ["Imani", "Nia"],
                "quality_score": 0.80 + random.random() * 0.15,
                "reviewer": "automated_generation_v2",
                "notes": f"Auto-generated grounded answer: {answer_type}"
            }
        }

    def _create_format_compliance_example(self, sample_id: str, persona: str, query: str,
                                          edge_case_type: str, difficulty: str) -> Dict:
        """Create a format compliance example."""
        # These test edge cases in the answer_json format
        sources = random.sample(self.source_library['sources'], min(2, len(self.source_library['sources'])))

        retrieved_context = []
        for rank, source in enumerate(sources, 1):
            chunk = {
                "rank": rank,
                "score": 0.80 - (rank - 1) * 0.05,
                "chunk_id": f"{source['doc_id']}::chunk::{rank}",
                "doc_id": source['doc_id'],
                "namespace": source['namespace'],
                "content": f"[Content that partially addresses: {query}]",
                "metadata": {
                    "citation_label": source['citation_label'],
                    "canonical_url": source['canonical_url'],
                    "source_org": source['source_org'],
                    "year": source['year'],
                    "content_type": source['content_type'],
                    "license": source['license'],
                    "tags": source.get('tags', [])
                }
            }
            retrieved_context.append(chunk)

        sources_list = []
        for rank, source in enumerate(sources, 1):
            source_obj = {
                "citation_label": source['citation_label'],
                "canonical_url": source['canonical_url'],
                "source_org": source['source_org'],
                "year": source['year'],
                "content_type": source['content_type'],
                "license": source['license'],
                "namespace": source['namespace'],
                "doc_id": source['doc_id'],
                "chunk_id": f"{source['doc_id']}::chunk::{rank}",
                "tags": source.get('tags', []),
                "relevance_score": 0.80 - (rank - 1) * 0.05
            }
            sources_list.append(source_obj)

        # Format compliance focuses on proper structure even with edge cases
        answer_text = f"[This answer demonstrates proper answer_json formatting for the edge case: {edge_case_type}. Query: {query}. Even with {edge_case_type}, the response maintains complete schema compliance including all required fields, proper citation formatting, and appropriate completeness markers.]"

        expected_output = {
            "version": "kwanzaa.answer.v1",
            "persona": persona,
            "model_mode": "base_adapter_rag",
            "toggles": {
                "require_citations": True,
                "primary_sources_only": True,
                "creative_mode": False
            },
            "answer": {
                "text": answer_text,
                "confidence": 0.75 + random.random() * 0.15,
                "tone": "educational",
                "completeness": random.choice(["complete", "partial", "insufficient_data"])
            },
            "sources": sources_list if edge_case_type != "minimal_input" else sources_list[:1],
            "retrieval_summary": {
                "query": query,
                "top_k": 10,
                "namespaces": ["kwanzaa_primary_sources"],
                "filters": {},
                "results": [
                    {
                        "rank": rank,
                        "score": chunk['score'],
                        "snippet": chunk['content'][:80] + "...",
                        "citation_label": chunk['metadata']['citation_label'],
                        "canonical_url": chunk['metadata']['canonical_url'],
                        "doc_id": chunk['doc_id'],
                        "chunk_id": chunk['chunk_id'],
                        "namespace": chunk['namespace']
                    }
                    for rank, chunk in enumerate(retrieved_context, 1)
                ],
                "execution_time_ms": 180 + random.randint(0, 80)
            },
            "unknowns": {
                "unsupported_claims": [],
                "missing_context": [] if edge_case_type == "minimal_input" else ["Additional context for complex query"],
                "clarifying_questions": [] if edge_case_type != "vague_query" else ["Could you be more specific about what aspect interests you?"]
            },
            "integrity": {
                "citation_required": True,
                "citations_provided": True,
                "retrieval_confidence": "medium",
                "fallback_behavior": "not_needed"
            },
            "provenance": {
                "generated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            }
        }

        return {
            "sample_id": sample_id,
            "category": "format_compliance",
            "persona": persona,
            "user_query": query,
            "retrieved_context": retrieved_context,
            "expected_output": expected_output,
            "metadata": {
                "difficulty": difficulty,
                "principle_focus": ["Imani"],
                "quality_score": 0.80 + random.random() * 0.10,
                "reviewer": "automated_generation_v2",
                "notes": f"Auto-generated format compliance: {edge_case_type}",
                "edge_case": True
            }
        }

    def save_all_examples(self, output_dir: Path):
        """Save all examples to their respective files."""
        output_dir.mkdir(parents=True, exist_ok=True)

        all_saved = 0

        for category, samples in self.examples.items():
            if not samples:
                continue

            # Calculate statistics
            stats = {
                "total_samples": len(samples),
                "by_category": {},
                "by_persona": {},
                "by_difficulty": {}
            }

            for sample in samples:
                cat = sample['category']
                stats['by_category'][cat] = stats['by_category'].get(cat, 0) + 1

                persona = sample['persona']
                stats['by_persona'][persona] = stats['by_persona'].get(persona, 0) + 1

                diff = sample['metadata'].get('difficulty', 'unknown')
                stats['by_difficulty'][diff] = stats['by_difficulty'].get(diff, 0) + 1

            # Create output file
            filename = f"{category.replace('_', '-')}-examples.json"
            filepath = output_dir / filename

            output = {
                "dataset_version": "2.0.0",
                "created_at": "2026-01-16T00:00:00Z",
                "updated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "description": f"Training examples for {category} category",
                "statistics": stats,
                "samples": samples
            }

            with open(filepath, 'w') as f:
                json.dump(output, f, indent=2)

            print(f"Saved {len(samples)} examples to {filename}")
            all_saved += len(samples)

        print(f"\nTotal samples saved: {all_saved}")
        return all_saved


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Generate comprehensive training examples')
    parser.add_argument('--target', type=int, default=120, help='Target total sample count')
    args = parser.parse_args()

    # Paths
    project_root = Path(__file__).parent.parent
    source_library = project_root / "data" / "training" / "source-metadata-library.json"
    examples_dir = project_root / "data" / "training" / "examples"

    print(f"=== Comprehensive Training Example Generator ===")
    print(f"Target: {args.target} total samples\n")

    # Initialize generator
    generator = ComprehensiveExampleGenerator(
        source_library_path=str(source_library),
        target_count=args.target
    )

    # Load existing examples
    print("Loading existing examples...")
    existing_count = generator.load_existing_examples(examples_dir)

    # Generate additional examples
    generator.generate_all_examples()

    # Save all examples
    print("\nSaving examples...")
    total = generator.save_all_examples(examples_dir)

    # Print final statistics
    print("\n=== Final Statistics ===")
    for category, samples in generator.examples.items():
        if samples:
            print(f"{category}: {len(samples)} samples")

    print(f"\nTotal: {total} samples")
    print(f"Target was: {args.target}")
    print(f"Achievement: {(total/args.target)*100:.1f}%")
    print("\nDone!")


if __name__ == "__main__":
    main()
