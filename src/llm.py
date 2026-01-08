"""LLM wrapper with an API-based implementation and a placeholder for local models.
"""
import os
from typing import List
from urllib.parse import quote_plus

from .config import get_settings
from .usage_tracker import check_usage_limit, record_usage

SETTINGS = get_settings()


def generate_library_links(query: str) -> dict:
    """Generate search links for OMNI and JSTOR based on the query."""
    encoded_query = quote_plus(query)
    return {
        "omni": f"https://omni.scholarsportal.info/search?q={encoded_query}",
        "jstor": f"https://www.jstor.org/action/doBasicSearch?Query={encoded_query}",
    }


class LLMClient:
    def __init__(self):
        self.mode = SETTINGS.llm_mode
        self.model = SETTINGS.model_name

    def generate(self, question: str, context_docs: List[dict]) -> str:
        """Generate an answer from question + retrieved context.

        Uses OpenAI if `mode` is `api` and `OPENAI_API_KEY` is set. For local models, implement
        the `LocalLLM` class and swap this implementation.
        """
        if self.mode == "api":
            return self._generate_with_openai(question, context_docs)
        else:
            return self._generate_placeholder(question, context_docs)

    def _generate_with_openai(self, question: str, context_docs: List[dict]) -> str:
        try:
            # Check usage limit before making API call
            is_allowed, remaining, limit_message = check_usage_limit()
            if not is_allowed:
                return limit_message

            from openai import OpenAI

            api_key = SETTINGS.openai_api_key
            print(f"DEBUG: API key loaded: {bool(api_key)}")  # DEBUG LINE
            if not api_key:
                print("DEBUG: No API key, using placeholder")  # DEBUG LINE
                return self._generate_placeholder(question, context_docs)

            client = OpenAI(api_key=api_key)
            prompt = self._build_prompt(question, context_docs)
            resp = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=512,
                temperature=0.2,
            )

            # Record token usage
            if resp.usage:
                record_usage("gpt-3.5-turbo-input", resp.usage.prompt_tokens)
                record_usage("gpt-3.5-turbo-output", resp.usage.completion_tokens)

            return resp.choices[0].message.content.strip()
        except Exception as e:
            return f"Error calling OpenAI: {e}"

    def _build_prompt(self, question: str, context_docs: List[dict]) -> str:
        ctx_parts = []
        for d in context_docs:
            title = d.get('metadata', {}).get('title', d.get('id'))
            doi = d.get('metadata', {}).get('doi', d.get('metadata', {}).get('url', 'N/A'))
            free_pdf = d.get('metadata', {}).get('free_pdf')
            lib_links = generate_library_links(title) if title else {"omni": "", "jstor": ""}
            ctx_parts.append(
                f"Source: {title}\n"
                f"Original URL: {doi}\n"
                f"OMNI Link: {lib_links['omni']}\n"
                f"JSTOR Link: {lib_links['jstor']}\n"
                f"Free PDF: {free_pdf if free_pdf else 'Not available'}\n"
                f"{d.get('document')[:1500]}"
            )
        ctx = "\n\n".join(ctx_parts)
        prompt = f""" "You are GRAYSON, a scholarly research assistant who analyzes theological concepts and their relationships to biblical texts. In every output, answer the question the user asks before making a reccomendation of source material.

CONTEXT FROM RETRIEVED SOURCES:
{ctx}

USER QUESTION: {question}

INSTRUCTIONS:
1. When the user asks how a concept relates to specific verses, explain the theological/scholarly connection between them, not just summarize each verse.
2. ALWAYS ANSWER THE ACTUAL QUESTION BEING ASKED. Provide a concise, helpful answer based on the context above and offer detailed explanations concerning multiple scholars perspectives on the topic.
3. Always cite your sources using the OMNI and JSTOR links provided in the context (not the original URL). Use the FULL URL starting with https://.
4. Format source links as clickable markdown links with the ACTUAL URLs.
5. Provide multiple sources when possible to give a well-rounded answer.
6. End your response with a "Have you considered?" section that suggests ONE highly related topic, resource, or research direction the user might find valuable. This should be genuinely useful and directly related to their query.
7. When a Free PDF link is available for a source (not "Not available"), ALWAYS include it in your Sources section. Free PDFs are valuable for researchers who may not have institutional access.

FORMAT YOUR RESPONSE AS:
[Your answer with inline citations]

**Sources:**
- [Source Title](https://omni.scholarsportal.info/search?q=...) | [JSTOR](https://www.jstor.org/action/doBasicSearch?Query=...) | [Free PDF](actual_free_pdf_url_if_available)

**Have you considered?** [Your suggestion for a related topic or resource to explore]

IMPORTANT: Replace the "..." with the actual encoded query from the OMNI Link and JSTOR Link URLs provided in each source's context above. If a Free PDF URL is available, include it. If Free PDF says "Not available", omit the Free PDF link for that source. Do NOT use placeholder text."""
        return prompt

    def _generate_placeholder(self, question: str, context_docs: List[dict]) -> str:
        # Lightweight fallback for local testing: concatenate top context snippets.
        snippets = []
        for d in context_docs[:3]:
            title = d.get('metadata', {}).get('title', '')
            url = d.get('metadata', {}).get('doi', d.get('metadata', {}).get('url', ''))
            snippets.append(f"- [{title}]({url})\n  {d.get('document')[:300]}...")

        sources_text = "\n".join(snippets) if snippets else "No sources found."

        # Set defaults in case no docs found
        first_title = ""
        links_1 = {"omni": "", "jstor": ""}
        second_title = ""
        links_2 = {"omni": "", "jstor": ""}

        # searching context docs (#1 and 2 most relevant resources to what the user just asked about)
        # providing their titles to include in the "Have you considered?" section.
        if context_docs:
            first_title = context_docs[0].get('metadata', {}).get('title', '')
            links_1 = generate_library_links(first_title)
            if len(context_docs) > 1: # >1 prevents crash if only one doc was retreived 
                second_title = context_docs[1].get('metadata', {}).get('title', '')
                links_2 = generate_library_links(second_title)

        return f"""Based on the available research, here are relevant sources for your query:

{sources_text}

**Have you considered?**
- [{first_title}]({links_1['omni']}) (OMNI)
- [{first_title}]({links_1['jstor']}) (JSTOR)
- [{second_title}]({links_2['omni']}) (OMNI)
- [{second_title}]({links_2['jstor']}) (JSTOR)"""
