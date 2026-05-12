#
#
# SCHEMA_old = {
#     "stance": {
#         "stance": "support|oppose|mixed/ambiguous|neutral|n/a",
#         "stance_evidence": "string"
#     },
#     "epistemics": {
#         "epistemic_frame": "belief|knowledge|uncertainty|inquiry",
#         "certainty_score": "0.0-1.0 float",
#         "hedging_markers": ["string"]
#     },
#     "argumentation": {
#         "explicitness_level": "explicit|implicit|fragmentary",
#         "explicitness_justification": "string",
#         "argument_depth_score": "1-7 integer",
#
#         "reasoning_steps": [
#             "Prämisse: ...",
#             "Schlussfolgerung: ...",
#             "Gegenbehauptung/Widerlegung: ..."
#         ],
#
#         "argument_scheme_primary": "causal|symptomatic|analogy|authority|pragmatic_consequence|definition|other",
#         "argument_scheme_secondary": ["string"],
#         "rebuttal_present": "boolean"
#     },
#     "affect_rhetoric": {
#         "emotion": "anger|fear|pride|hope|disgust|sadness|neutral|mixed",
#         "emotion_evidence": "string",
#         "rhetorical_devices": [
#             {"device": "string", "example": "string"}
#         ]
#     },
#     "factuality": {
#         "fact_spans": ["string"],
#         "support_type_per_fact": [
#             "empirical|anecdotal|authority_citation|link|none"
#         ],
#         "support_type_per_fact": ["empirical|anecdotal|authority_citation|link|none"],
#         "source_credibility_score": "0.0-1.0 float"
#     },
#     "coherence": {
#         "coherence_internal": "0.0-1.0 float",
#         "coherence_with_interlocutor": "0.0-1.0 float",
#         "deliberation_quality_score": "0.0-1.0 float",
#         "dq_justification": "string"
#     }
# }
#
# SCHEMA_01 = {
#     "argument_id": {
#         "span": "string (≤20 words verbatim)",
#         "stance": "support|oppose|mixed/ambiguous|neutral|n/a",
#         "stance_likert": "1 (negative) - 4 (neutral) - 7 (positive)",
#         "stance_evidence": "string",
#         "stance_referent": "string"
#     }
# }
#
# SCHEMA = {
#     "language": "de",
#     "top_concepts": [
#         {
#             "concept": "<string>",
#             "stance": "pro|contra|neutral|ambivalent",
#             "stance_score": "<float in [-1.0, 1.0]>",
#             "valence": "positiv|negativ|neutral|ambivalent",    # affektive Bewertung des Konzepts
#             "valence_score": "<float in [-1.0, 1.0]>",
#             "evaluation_terms": ["<Wertungen/Adjektive>"],
#             "certainty": "<float in [0.0, 1.0]>",
#             "evidence": ["<exakte Zitatphrase>", "..."],
#             "justification": "string"
#         }
#     ]
# }
#
# sys_msg = f"""Du bist Expert:in für Diskursanalyse und Argument-Mining."""
#
#
#
# N = 8
# user_msg = f"""
# Analysiere die untenstehende REDE. Ziel: Identifiziere die Top {N-2} - {N+2} Kernkonzepte (inhaltlich zentrale, wiederkehrende oder evaluativ markierte Begriffe/Frames) und erfasse die Meinung/Einstellung/Bewertung der Sprecher:in dazu.
#
# Gib AUSSCHLIESSLICH ein JSON-Objekt zurück, das diesem SCHEMA strikt entspricht:
#
# {SCHEMA}
#
# Regeln:
# - Verwende ausschließlich die REDE; bevorzuge Konzepte aus der Kandidatenliste.
# - Wähle sinntragende Konzepte (keine Funktionswörter), ggf. Konzepte zusammenfassen (Singular, konsistente Benennung).
# - Für jedes Konzept: Haltung (pro/contra/neutral/ambivalent), Stance-Score ∈ [-1.0, 1.0], Sicherheit ∈ [0.0, 1.0], 1–3 Belegzitate.
# - Sei konsistent, knapp, logisch.
#
# ---
#
# REDE:
# \"\"\"{speech["text"]}\"\"\"
#
# """

#############################