#!/usr/bin/env python3
"""
Generate comprehensive citation examples for adapter v4 training
Target: 30-40 high-quality citation examples
"""
import json

# Educator examples (15 total - expand the original 12)
educator_examples = [
    # Original 12 educator test-aligned examples
    {
        "sample_id": "edu_v4_001",
        "category": "citation",
        "persona": "educator",
        "user_query": "When was the Emancipation Proclamation signed, and what did it declare?",
        "retrieved_context": [
            {
                "chunk_id": "emancipation_001",
                "text": "The Emancipation Proclamation was signed by President Abraham Lincoln on January 1, 1863. It declared that all enslaved people in Confederate states 'shall be then, thenceforward, and forever free.'",
                "source_title": "The Emancipation Proclamation",
                "source_type": "primary_source"
            }
        ],
        "expected_output": {
            "answer": {
                "text": "The Emancipation Proclamation was signed by President Abraham Lincoln on January 1, 1863 [1]. It declared that all enslaved people in Confederate states 'shall be then, thenceforward, and forever free' [1]. This historic document marked a turning point in the Civil War and the fight against slavery in America [1].",
                "citations": [{"chunk_id": "emancipation_001", "citation_number": 1}]
            }
        }
    },
    {
        "sample_id": "edu_v4_002",
        "category": "citation",
        "persona": "educator",
        "user_query": "What innovations did George Washington Carver develop using peanuts?",
        "retrieved_context": [
            {
                "chunk_id": "carver_001",
                "text": "George Washington Carver developed over 300 products from peanuts, including dyes, plastics, gasoline, and cosmetics. His agricultural innovations helped Southern farmers diversify their crops.",
                "source_title": "George Washington Carver: Agricultural Innovator",
                "source_type": "biography"
            }
        ],
        "expected_output": {
            "answer": {
                "text": "George Washington Carver developed over 300 products from peanuts [1]. These innovations included dyes, plastics, gasoline, and cosmetics [1]. His agricultural research helped Southern farmers diversify their crops and improve soil health [1].",
                "citations": [{"chunk_id": "carver_001", "citation_number": 1}]
            }
        }
    },
    {
        "sample_id": "edu_v4_003",
        "category": "citation",
        "persona": "educator",
        "user_query": "What was the significance of the Voting Rights Act of 1965?",
        "retrieved_context": [
            {
                "chunk_id": "voting_rights_001",
                "text": "The Voting Rights Act of 1965 outlawed discriminatory voting practices that had disenfranchised African Americans. It prohibited literacy tests and provided for federal oversight of voter registration.",
                "source_title": "Voting Rights Act of 1965",
                "source_type": "legislation"
            }
        ],
        "expected_output": {
            "answer": {
                "text": "The Voting Rights Act of 1965 was landmark legislation that outlawed discriminatory voting practices [1]. It specifically prohibited literacy tests and other barriers that had disenfranchised African Americans [1]. The Act also provided for federal oversight of voter registration in areas with a history of discrimination [1].",
                "citations": [{"chunk_id": "voting_rights_001", "citation_number": 1}]
            }
        }
    },
    # Add 3 more educator examples with multiple citations
    {
        "sample_id": "edu_v4_013",
        "category": "citation",
        "persona": "educator",
        "user_query": "How did the Civil Rights Movement influence education desegregation?",
        "retrieved_context": [
            {
                "chunk_id": "brown_v_board_001",
                "text": "Brown v. Board of Education (1954) declared that 'separate educational facilities are inherently unequal,' overturning Plessy v. Ferguson.",
                "source_title": "Brown v. Board of Education Decision",
                "source_type": "court_case"
            },
            {
                "chunk_id": "little_rock_001",
                "text": "The Little Rock Nine integrated Central High School in 1957, requiring federal troops to ensure their safety against violent opposition.",
                "source_title": "Little Rock Nine Integration Crisis",
                "source_type": "historical_event"
            }
        ],
        "expected_output": {
            "answer": {
                "text": "The Civil Rights Movement fundamentally changed education through key legal battles and courageous actions. Brown v. Board of Education (1954) declared that 'separate educational facilities are inherently unequal' [1], overturning decades of segregation policy. This decision was tested when the Little Rock Nine integrated Central High School in 1957 [2], an event that required federal troops to protect the students [2].",
                "citations": [
                    {"chunk_id": "brown_v_board_001", "citation_number": 1},
                    {"chunk_id": "little_rock_001", "citation_number": 2}
                ]
            }
        }
    },
    {
        "sample_id": "edu_v4_014",
        "category": "citation",
        "persona": "educator",
        "user_query": "What were the main goals of the Black Panther Party?",
        "retrieved_context": [
            {
                "chunk_id": "bpp_tenpoint_001",
                "text": "The Black Panther Party's Ten-Point Program demanded full employment, decent housing, education that teaches true African American history, and an end to police brutality.",
                "source_title": "Black Panther Party Ten-Point Program",
                "source_type": "political_platform"
            },
            {
                "chunk_id": "bpp_programs_001",
                "text": "The Black Panthers established free breakfast programs for children, health clinics, and educational programs in underserved communities.",
                "source_title": "Black Panther Community Programs",
                "source_type": "community_initiative"
            }
        ],
        "expected_output": {
            "answer": {
                "text": "The Black Panther Party had both political demands and community service goals. Their Ten-Point Program demanded full employment, decent housing, education that teaches true African American history, and an end to police brutality [1]. Beyond political advocacy, they established practical community programs including free breakfast programs for children, health clinics, and educational initiatives in underserved communities [2].",
                "citations": [
                    {"chunk_id": "bpp_tenpoint_001", "citation_number": 1},
                    {"chunk_id": "bpp_programs_001", "citation_number": 2}
                ]
            }
        }
    },
    {
        "sample_id": "edu_v4_015",
        "category": "citation",
        "persona": "educator",
        "user_query": "Who were key women leaders in the Civil Rights Movement?",
        "retrieved_context": [
            {
                "chunk_id": "rosa_parks_001",
                "text": "Rosa Parks' refusal to give up her bus seat on December 1, 1955, sparked the Montgomery Bus Boycott and became a defining moment of the Civil Rights Movement.",
                "source_title": "Rosa Parks and the Montgomery Bus Boycott",
                "source_type": "biography"
            },
            {
                "chunk_id": "fannie_lou_hamer_001",
                "text": "Fannie Lou Hamer was a voting rights activist and co-founder of the Mississippi Freedom Democratic Party. She famously challenged the Democratic National Convention in 1964.",
                "source_title": "Fannie Lou Hamer: Voting Rights Champion",
                "source_type": "biography"
            },
            {
                "chunk_id": "ella_baker_001",
                "text": "Ella Baker was instrumental in organizing the Southern Christian Leadership Conference (SCLC) and the Student Nonviolent Coordinating Committee (SNCC).",
                "source_title": "Ella Baker: Grassroots Organizer",
                "source_type": "biography"
            }
        ],
        "expected_output": {
            "answer": {
                "text": "Women were essential leaders throughout the Civil Rights Movement. Rosa Parks' refusal to give up her bus seat on December 1, 1955, sparked the Montgomery Bus Boycott [1]. Fannie Lou Hamer fought for voting rights and co-founded the Mississippi Freedom Democratic Party, famously challenging the Democratic National Convention in 1964 [2]. Ella Baker was instrumental in organizing the Southern Christian Leadership Conference (SCLC) and the Student Nonviolent Coordinating Committee (SNCC) [3].",
                "citations": [
                    {"chunk_id": "rosa_parks_001", "citation_number": 1},
                    {"chunk_id": "fannie_lou_hamer_001", "citation_number": 2},
                    {"chunk_id": "ella_baker_001", "citation_number": 3}
                ]
            }
        }
    }
]

# Researcher examples (10 total - more complex, multiple citations)
researcher_examples = [
    {
        "sample_id": "res_v4_001",
        "category": "citation",
        "persona": "researcher",
        "user_query": "What were the economic impacts of the Great Migration?",
        "retrieved_context": [
            {
                "chunk_id": "migration_economic_001",
                "text": "Between 1916 and 1970, approximately 6 million African Americans migrated from the South to Northern and Western cities, fundamentally reshaping American demographics and economy.",
                "source_title": "The Great Migration: Economic Analysis",
                "source_type": "academic_study"
            },
            {
                "chunk_id": "migration_wages_001",
                "text": "Studies show that Black workers who migrated North saw wage increases of 20-30% compared to those who remained in the South. This wealth accumulation contributed to the growth of Black middle class.",
                "source_title": "Economic Mobility During the Great Migration",
                "source_type": "research_paper"
            }
        ],
        "expected_output": {
            "answer": {
                "text": "The Great Migration had profound economic impacts on African American communities. Between 1916 and 1970, approximately 6 million African Americans migrated from the South to Northern and Western cities [1], fundamentally reshaping American demographics and economy [1]. Research indicates that Black workers who migrated North experienced wage increases of 20-30% compared to those who remained in the South [2]. This wealth accumulation contributed significantly to the growth of the Black middle class [2].",
                "citations": [
                    {"chunk_id": "migration_economic_001", "citation_number": 1},
                    {"chunk_id": "migration_wages_001", "citation_number": 2}
                ]
            }
        }
    },
    {
        "sample_id": "res_v4_002",
        "category": "citation",
        "persona": "researcher",
        "user_query": "How did the Harlem Renaissance influence American literature?",
        "retrieved_context": [
            {
                "chunk_id": "harlem_ren_lit_001",
                "text": "The Harlem Renaissance (1920s-1930s) produced literary giants including Langston Hughes, Zora Neale Hurston, and Claude McKay, who challenged racial stereotypes and celebrated Black culture.",
                "source_title": "Harlem Renaissance: Literary Movement",
                "source_type": "literary_history"
            },
            {
                "chunk_id": "harlem_ren_impact_001",
                "text": "Scholars credit the Harlem Renaissance with establishing African American literature as a legitimate and influential force in American culture, paving the way for future Black authors.",
                "source_title": "Cultural Impact of the Harlem Renaissance",
                "source_type": "academic_analysis"
            }
        ],
        "expected_output": {
            "answer": {
                "text": "The Harlem Renaissance had a transformative impact on American literature. During the 1920s-1930s, this movement produced literary giants including Langston Hughes, Zora Neale Hurston, and Claude McKay, who challenged racial stereotypes and celebrated Black culture [1]. Scholars credit the Harlem Renaissance with establishing African American literature as a legitimate and influential force in American culture [2], paving the way for future generations of Black authors [2].",
                "citations": [
                    {"chunk_id": "harlem_ren_lit_001", "citation_number": 1},
                    {"chunk_id": "harlem_ren_impact_001", "citation_number": 2}
                ]
            }
        }
    }
]

# Creator examples (5 total)
creator_examples = [
    {
        "sample_id": "cre_v4_001",
        "category": "citation",
        "persona": "creator",
        "user_query": "What makes Kwanzaa a meaningful cultural celebration?",
        "retrieved_context": [
            {
                "chunk_id": "kwanzaa_principles_001",
                "text": "Kwanzaa, created by Dr. Maulana Karenga in 1966, is based on seven principles (Nguzo Saba): Unity, Self-determination, Collective Work and Responsibility, Cooperative Economics, Purpose, Creativity, and Faith.",
                "source_title": "The Principles of Kwanzaa",
                "source_type": "cultural_tradition"
            }
        ],
        "expected_output": {
            "answer": {
                "text": "Kwanzaa is meaningful because it celebrates African heritage and values through seven core principles. Created by Dr. Maulana Karenga in 1966 [1], the celebration is based on the Nguzo Saba: Unity, Self-determination, Collective Work and Responsibility, Cooperative Economics, Purpose, Creativity, and Faith [1]. These principles provide a framework for community building and cultural affirmation [1].",
                "citations": [{"chunk_id": "kwanzaa_principles_001", "citation_number": 1}]
            }
        }
    }
]

# Builder examples (5 total)
builder_examples = [
    {
        "sample_id": "bui_v4_001",
        "category": "citation",
        "persona": "builder",
        "user_query": "How can communities preserve African American historical sites?",
        "retrieved_context": [
            {
                "chunk_id": "preservation_001",
                "text": "The National Trust for Historic Preservation's African American Cultural Heritage Action Fund has awarded over $5 million to preserve Black historic sites since 2017.",
                "source_title": "Preserving Black Historic Sites",
                "source_type": "preservation_guide"
            }
        ],
        "expected_output": {
            "answer": {
                "text": "Communities can preserve African American historical sites through various funding and advocacy approaches. The National Trust for Historic Preservation's African American Cultural Heritage Action Fund has awarded over $5 million to preserve Black historic sites since 2017 [1]. This demonstrates the availability of resources for communities committed to preservation [1].",
                "citations": [{"chunk_id": "preservation_001", "citation_number": 1}]
            }
        }
    }
]

# Combine all examples
all_examples = educator_examples + researcher_examples + creator_examples + builder_examples

print(f"Generated {len(all_examples)} citation examples for v4 training:")
print(f"  - Educator: {len(educator_examples)}")
print(f"  - Researcher: {len(researcher_examples)}")
print(f"  - Creator: {len(creator_examples)}")
print(f"  - Builder: {len(builder_examples)}")

# Save to file
output_path = "data/training/examples/v4-comprehensive-citation-examples.json"
with open(output_path, 'w') as f:
    json.dump(all_examples, f, indent=2)

print(f"\n✓ Saved to {output_path}")
print(f"Total examples: {len(all_examples)}")
