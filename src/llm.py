"""LLM wrapper with an API-based implementation and a placeholder for local models.
"""
import os
import json
import re
from typing import List, Dict, Tuple
from urllib.parse import quote_plus, quote

from .config import get_settings
from .usage_tracker import check_usage_limit, record_usage

SETTINGS = get_settings()


def generate_library_links(query: str) -> dict:
    """Generate uOttawa library search links based on the query.

    Returns two search links for the uOttawa library system:
    - omni: Searches across OCUL Discovery Network (includes OMNI resources)
    - jstor: Searches specifically within uOttawa's library (which includes JSTOR access)
    """
    encoded_query = quote_plus(query)

    # OCUL Discovery Network search (OMNI and other consortium resources)
    omni_link = f"https://ocul-uo.primo.exlibrisgroup.com/discovery/search?vid=01OCUL_UO:UO_DEFAULT&tab=OCULDiscoveryNetwork&query=any,contains,{encoded_query}"

    # uOttawa library search (includes JSTOR through institutional access)
    jstor_link = f"https://ocul-uo.primo.exlibrisgroup.com/discovery/search?vid=01OCUL_UO:UO_DEFAULT&tab=Everything&query=any,contains,{encoded_query}"

    return {
        "omni": omni_link,
        "jstor": jstor_link,
    }


def extract_book_mentions(text: str) -> List[Tuple[str, str]]:
    """Extract book titles and authors from text.

    Looks for patterns like:
    - "Title" by Author
    - Author in "Title"
    - works such as "Title" by Author

    Returns list of (title, author) tuples.
    """
    books = []

    # Pattern 1: "Book Title" by Author Name OR 'Book Title' by Author Name
    # Captures quoted title (single or double quotes) and author after "by"
    # Stops at punctuation: . , ; ) or newline
    pattern1 = r'["\']([^"\']+)["\']\s+by\s+([A-Z][^.,;\n)]+?)(?:[.,;\n)]|$)'

    matches = re.finditer(pattern1, text)
    for match in matches:
        title = match.group(1).strip()
        author = match.group(2).strip()

        # Clean up author name (remove trailing punctuation and words)
        author = re.sub(r'[)\s]+$', '', author)  # Remove trailing ) and whitespace
        author = re.sub(r'\s+(or|and|These|This|It).*$', '', author, flags=re.IGNORECASE)

        if title and author:
            books.append((title, author))

    # Pattern 2: Author in "Book Title" OR Author in 'Book Title'
    # Captures author before "in" and quoted title after
    pattern2 = r'([A-Z][A-Za-z\.\s]+?)\s+in\s+["\']([^"\']+)["\']'

    matches = re.finditer(pattern2, text)
    for match in matches:
        author = match.group(1).strip()
        title = match.group(2).strip()

        # Clean up author name
        author = re.sub(r'[,\s]+$', '', author)  # Remove trailing comma and whitespace
        author = re.sub(r'\s+(or|and|These|This|It).*$', '', author, flags=re.IGNORECASE)

        if title and author:
            books.append((title, author))

    return books


def _format_sources(context_docs: List[dict], sources_used: List[int]) -> str:
    """Format sources with proper markdown links based on which sources were used."""
    if not sources_used:
        return ""

    formatted_sources = []
    has_free_pdf = False

    for idx in sources_used:
        # Convert to 0-based index
        i = idx - 1
        if i < 0 or i >= len(context_docs):
            continue

        d = context_docs[i]
        title = d.get('metadata', {}).get('title', 'Untitled')
        doi = d.get('metadata', {}).get('doi', '')
        free_pdf = d.get('metadata', {}).get('free_pdf')

        if free_pdf:
            has_free_pdf = True

        # Build DOI link
        doi_link = None
        if doi and doi.strip() and doi != 'N/A':
            if not doi.startswith('http'):
                doi_link = f"https://doi.org/{doi}"
            else:
                doi_link = doi

        # Build uOttawa link
        uottawa_link = None
        if doi and doi.strip() and doi != 'N/A':
            # Has DOI - use resolver
            doi_id = doi.replace('https://doi.org/', '') if doi.startswith('https://doi.org/') else doi
            doi_encoded = quote(doi_id, safe='')
            uottawa_link = f"https://uottawa.primo.exlibrisgroup.com/discovery/openurl?institution=01UOTTAWA_INST&vid=01UOTTAWA_INST:UOTTAWA&doi={doi_encoded}"
        elif title:
            # No DOI - use title-based search
            title_encoded = quote_plus(title)
            uottawa_link = f"https://ocul-uo.primo.exlibrisgroup.com/discovery/search?vid=01OCUL_UO:UO_DEFAULT&tab=OCULDiscoveryNetwork&query=any,contains,{title_encoded}"

        # Build source line with markdown links
        link_parts = []
        if doi_link:
            link_parts.append(f"[{title}]({doi_link})")
        elif uottawa_link:
            link_parts.append(f"[{title}]({uottawa_link})")
        else:
            link_parts.append(title)

        if uottawa_link and doi_link:
            link_parts.append(f"[uOttawa Library]({uottawa_link})")

        if free_pdf:
            link_parts.append(f"[Free PDF]({free_pdf})")

        formatted_sources.append("- " + " | ".join(link_parts))

    result = "\n".join(formatted_sources)

    # Add no PDF message if applicable
    if not has_free_pdf:
        result += "\n\nSorry, no free PDFs to these sources were found."

    return result


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
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1024,
                temperature=0.2,
                response_format={"type": "json_object"}
            )

            # Record token usage
            if resp.usage:
                record_usage("gpt-4o-mini-input", resp.usage.prompt_tokens)
                record_usage("gpt-4o-mini-output", resp.usage.completion_tokens)

            # Parse JSON response
            raw_response = resp.choices[0].message.content.strip()
            print(f"DEBUG: Raw LLM response:\n{raw_response}\n")
            try:
                response_data = json.loads(raw_response)
                answer = response_data.get("answer", "")
                sources_used = response_data.get("sources_used", [])
                have_you_considered = response_data.get("have_you_considered", "")

                # DEBUG: Print what we received
                print(f"DEBUG: LLM returned sources_used: {sources_used}")
                print(f"DEBUG: Available context_docs count: {len(context_docs)}")

                # Return clean answer without embedded sources
                # Sources will be displayed separately by the frontend
                final_response = answer

                if have_you_considered:
                    final_response += f"\n\n**Have you considered?** {have_you_considered}"

                return final_response

            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return raw_response

        except Exception as e:
            return f"Error calling OpenAI: {e}"

    def _build_prompt(self, question: str, context_docs: List[dict]) -> str:
        ctx_parts = []
        for d in context_docs:
            title = d.get('metadata', {}).get('title', d.get('id'))
            doi = d.get('metadata', {}).get('doi', d.get('metadata', {}).get('url', ''))
            free_pdf = d.get('metadata', {}).get('free_pdf')

            # Normalize DOI to full URL format if needed
            doi_link = 'Not available'
            if doi and doi != 'N/A' and doi.strip():
                if not doi.startswith('http'):
                    # DOI is just the ID (e.g., "10.1234/example"), convert to full URL
                    doi_link = f"https://doi.org/{doi}"
                else:
                    doi_link = doi

            # Generate uOttawa library link
            # If DOI exists: use resolver link (finds paper across all databases)
            # If no DOI: use title-based search link (helps user find it manually)
            uottawa_link = 'Not available'
            if doi and doi != 'N/A' and doi.strip():
                # Has DOI - use resolver for direct access
                doi_id = doi.replace('https://doi.org/', '') if doi.startswith('https://doi.org/') else doi
                doi_encoded = quote(doi_id, safe='')
                uottawa_link = f"https://uottawa.primo.exlibrisgroup.com/discovery/openurl?institution=01UOTTAWA_INST&vid=01UOTTAWA_INST:UOTTAWA&doi={doi_encoded}"
            elif title:
                # No DOI - use title-based search link
                title_encoded = quote_plus(title)
                uottawa_link = f"https://ocul-uo.primo.exlibrisgroup.com/discovery/search?vid=01OCUL_UO:UO_DEFAULT&tab=OCULDiscoveryNetwork&query=any,contains,{title_encoded}"

            ctx_parts.append(
                f"Source: {title}\n"
                f"DOI Link: {doi_link}\n"
                f"uOttawa Library Link: {uottawa_link}\n"
                f"Free PDF: {free_pdf if free_pdf else 'Not available'}\n"
                f"{d.get('document')[:1500]}"
            )
        ctx = "\n\n".join(ctx_parts)

        # Build numbered source list for easy reference
        source_list = "\n".join([f"{i+1}. {ctx_parts[i]}" for i in range(len(ctx_parts))])

        prompt = f"""You are GRAYSON, a scholarly research assistant who analyzes theological concepts and their relationships to biblical texts.

CONTEXT FROM RETRIEVED SOURCES:
{source_list}

USER QUESTION: {question}

INSTRUCTIONS:
1. When the user asks how a concept relates to specific verses, explain the theological/scholarly connection between them, not just summarize each verse.
2. ALWAYS ANSWER THE ACTUAL QUESTION BEING ASKED. Provide a concise, helpful answer based on the context above.
3. Offer detailed explanations concerning multiple scholars' perspectives on the topic.
4. In your answer, reference sources by mentioning their titles naturally.
5. After your answer, indicate which source numbers (1, 2, 3, etc.) you used from the list above.
6. Suggest ONE related topic, resource, or research direction the user might find valuable for further exploration.

Return your response as JSON with this structure:
{{
    "answer": "Your detailed answer to the question with inline source title references",
    "sources_used": [1, 2, 3],
    "have_you_considered": "A suggestion for related exploration"
}}"""
        return prompt

    def _generate_placeholder(self, question: str, context_docs: List[dict]) -> str:
        # Lightweight fallback for local testing when no API key is available
        if not context_docs:
            return "No sources found for your query."

        # Simple answer based on source titles
        titles = [d.get('metadata', {}).get('title', 'Untitled') for d in context_docs[:3]]
        answer = f"Based on the available research, relevant sources for your query include: {', '.join(titles[:2])}, and others. For detailed analysis, please configure your OpenAI API key."

        # Suggest first relevant paper
        first_title = context_docs[0].get('metadata', {}).get('title', 'exploring related research')

        return f"""{answer}

**Have you considered?** Exploring "{first_title}" for additional context on your question."""
