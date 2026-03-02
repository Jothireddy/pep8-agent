from openai import OpenAI
from dotenv import load_dotenv
import os
from rag import PEP8RAG
import json

load_dotenv()

class PEP8Agent:
    """
    PEP 8 Code Review Agent - Generates comment insertion instructions
    """
    
    def __init__(self):
        """Initialize the agent with OpenAI client and RAG system"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in .env file")
        
        self.client = OpenAI(api_key=api_key)
        self.rag = PEP8RAG()
        self.model = "gpt-4o-mini"
        
        print("✅ PEP 8 Agent initialized successfully")
    
    def add_inline_comments_streaming(self, code, filename="unknown.py"):
        """
        Generate comment insertion instructions line by line
        
        Yields:
            dict with 'line_number' and 'comment' for each violation
        """
        
        print(f"🔍 Analyzing {filename}...")
        
        # Get relevant PEP 8 rules from RAG
        relevant_rules = self.rag.query_rules(code, n_results=5)
        
        # Number the lines for reference
        code_lines = code.split('\n')
        numbered_code = '\n'.join([f"{i+1}: {line}" for i, line in enumerate(code_lines)])
        
        # Create prompt that asks for LINE NUMBERS and COMMENTS
        prompt = f"""You are a PEP 8 code reviewer. Analyze this code and identify PEP 8 violations.

For each violation, output ONLY:
LINE <number>: <comment about violation>

RELEVANT PEP 8 RULES:
{chr(10).join(['---' + rule[:300] + '---' for rule in relevant_rules])}

CODE TO REVIEW (with line numbers):
{numbered_code}

OUTPUT FORMAT (one per line):
LINE 1: Function name should be 'calculate_total' (snake_case)
LINE 1: Missing docstring
LINE 2: Add spaces around '=' operator (should be 'total = 0')

If a line has no violations, don't output anything for it.
Output ONLY the violations in the format above. NO explanations, NO code, NO markdown.
"""
        
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You output ONLY lines in format: LINE <number>: <violation comment>. Nothing else."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.0,
                max_tokens=2000,
                stream=True
            )
            
            buffer = ""
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    buffer += content
                    
                    # Check if we have complete lines
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        line = line.strip()
                        
                        if line.startswith('LINE '):
                            # Parse: "LINE 5: Some comment"
                            try:
                                parts = line.split(':', 1)
                                line_num = int(parts[0].replace('LINE', '').strip())
                                comment = parts[1].strip()
                                
                                # Yield this comment insertion
                                yield {
                                    'type': 'comment',
                                    'line_number': line_num,
                                    'comment': f"# PEP8: {comment}"
                                }
                            except:
                                continue
            
            # Process any remaining buffer
            if buffer.strip().startswith('LINE '):
                try:
                    parts = buffer.strip().split(':', 1)
                    line_num = int(parts[0].replace('LINE', '').strip())
                    comment = parts[1].strip()
                    
                    yield {
                        'type': 'comment',
                        'line_number': line_num,
                        'comment': f"# PEP8: {comment}"
                    }
                except:
                    pass
            
            # Signal completion
            yield {'type': 'complete'}
            
        except Exception as e:
            yield {
                'type': 'error',
                'error': str(e)
            }
    
    def add_inline_comments(self, code, filename="unknown.py"):
        """
        Non-streaming version - builds final commented code
        """
        code_lines = code.split('\n')
        comments_to_insert = {}  # {line_number: [list of comments]}
        
        # Collect all comments
        for chunk in self.add_inline_comments_streaming(code, filename):
            if chunk['type'] == 'comment':
                line_num = chunk['line_number']
                if line_num not in comments_to_insert:
                    comments_to_insert[line_num] = []
                comments_to_insert[line_num].append(chunk['comment'])
        
        # Build final code with comments inserted
        result_lines = []
        for i, line in enumerate(code_lines, 1):
            # Add any comments for this line
            if i in comments_to_insert:
                for comment in comments_to_insert[i]:
                    result_lines.append(comment)
            # Add the original line
            result_lines.append(line)
        
        commented_code = '\n'.join(result_lines)
        violation_count = sum(len(comments) for comments in comments_to_insert.values())
        
        return {
            'original_code': code,
            'commented_code': commented_code,
            'violation_count': violation_count,
            'is_clean': violation_count == 0,
            'filename': filename
        }
    
    def generate_summary(self, results):
        """Generate summary of all processed files"""
        clean_files = []
        files_with_comments = []
        
        for filename, result in results.items():
            if result['is_clean']:
                clean_files.append(filename)
            else:
                files_with_comments.append((filename, result['violation_count']))
        
        summary = "=" * 60 + "\n"
        summary += "PEP 8 CODE REVIEW SUMMARY\n"
        summary += "=" * 60 + "\n\n"
        
        summary += f"📊 OVERVIEW:\n"
        summary += f"   • Total files reviewed: {len(results)}\n"
        summary += f"   • Clean files: {len(clean_files)}\n"
        summary += f"   • Files with violations: {len(files_with_comments)}\n"
        
        total_violations = sum(count for _, count in files_with_comments)
        summary += f"   • Total violations found: {total_violations}\n\n"
        
        if clean_files:
            summary += "✅ CLEAN FILES:\n"
            for filename in clean_files:
                summary += f"   • {filename}\n"
            summary += "\n"
        
        if files_with_comments:
            summary += "⚠️  FILES WITH VIOLATIONS:\n"
            for filename, count in sorted(files_with_comments, key=lambda x: x[1], reverse=True):
                summary += f"   • {filename}: {count} violations\n"
            summary += "\n"
        
        summary += "=" * 60 + "\n"
        
        return summary