from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
import json
import os
import re
from dotenv import load_dotenv

class CodebaseAgent:
    def __init__(self):
        load_dotenv()
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.1,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Get the project root directory (two levels up from this file)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        data_dir = os.path.join(project_root, 'data')
        
        # Load the base prompt and context
        with open(os.path.join(data_dir, 'llm_prompt.txt'), 'r') as f:
            self.base_prompt = f.read()
        
        with open(os.path.join(data_dir, 'llm_context.json'), 'r') as f:
            self.context = json.load(f)
        
        # Create the prompt template
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", self.base_prompt),
            ("human", "Analyze the following codebase:\n\n{codebase}")
        ])
        
        # Create the chain
        self.chain = (
            {
                "codebase": lambda _: json.dumps(self.context, indent=2)
            }
            | self.prompt_template
            | self.llm
            | StrOutputParser()
        )
    
    def _extract_json(self, text: str) -> dict:
        """Extract JSON from the response text."""
        print("Raw response received:")
        print(text[:500] + "..." if len(text) > 500 else text)
        print("\nAttempting to extract JSON...")
        
        # Remove markdown code block if present
        text = re.sub(r'```json\n?', '', text)
        text = re.sub(r'```\n?', '', text)
        
        # Try to find JSON content using regex
        json_pattern = r'\[\s*\{.*\}\s*\]'
        match = re.search(json_pattern, text, re.DOTALL)
        
        if match:
            json_str = match.group(0)
            print("\nFound JSON string:")
            print(json_str[:200] + "..." if len(json_str) > 200 else json_str)
            
            try:
                # Clean up the JSON string
                json_str = json_str.strip()
                # Remove any trailing commas
                json_str = re.sub(r',\s*}', '}', json_str)
                json_str = re.sub(r',\s*]', ']', json_str)
                # Remove any text after the closing bracket
                json_str = re.sub(r'\]\s*.*$', ']', json_str, flags=re.DOTALL)
                
                # Try to parse the JSON
                result = json.loads(json_str)
                print("\nSuccessfully parsed JSON")
                return result
            except json.JSONDecodeError as e:
                print(f"\nJSON parsing error: {str(e)}")
                print(f"Error location: line {e.lineno}, column {e.colno}")
                print(f"Context around error: {json_str[max(0, e.pos-50):e.pos+50]}")
                raise
        
        # If no JSON found, try to parse the entire text
        try:
            print("\nNo JSON pattern found, attempting to parse entire text")
            return json.loads(text)
        except json.JSONDecodeError:
            print("\nCould not parse entire text as JSON")
            raise ValueError("Could not extract valid JSON from response")
    
    def analyze_codebase(self):
        """Run the analysis on the codebase"""
        print("Starting codebase analysis...")
        try:
            result = self.chain.invoke({})
            
            # Save the raw response
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            data_dir = os.path.join(project_root, 'data')
            os.makedirs(data_dir, exist_ok=True)
            
            with open(os.path.join(data_dir, 'raw_response.txt'), 'w') as f:
                f.write(result)
            
            print("Analysis completed and saved to 'data/raw_response.txt'")
            return result
        except Exception as e:
            print(f"Error during analysis: {str(e)}")
            raise

if __name__ == "__main__":
    agent = CodebaseAgent()
    agent.analyze_codebase() 