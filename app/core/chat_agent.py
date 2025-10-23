"""
ChatAgent - AI-powered chat agent for handling booking conversations
Supports: Google Gemini, OpenAI, and custom OpenAI-compatible APIs
"""
import json
from typing import List, Dict, Optional

from config import (
    LLM_PROVIDER,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    OPENAI_BASE_URL,
    GEMINI_API_KEY,
    GEMINI_MODEL
)
from app.core.booking_manager import BookingManager

# Import LLM clients
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAI not installed. Install with: pip install openai")

try:
    from google import genai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: Google Generative AI not installed. Install with: pip install google-generativeai")


class ChatAgent:
    """AI-powered chat agent for handling booking conversations"""
    
    def __init__(self, booking_manager: BookingManager, model: Optional[str] = None):
        self.booking_manager = booking_manager
        self.conversation_history: Dict[str, List[Dict]] = {}
        self.provider = LLM_PROVIDER
        
        # Initialize based on provider
        if self.provider == "gemini":
            if not GEMINI_AVAILABLE:
                raise RuntimeError("Google Generative AI not installed. Install: pip install google-generativeai")
            if not GEMINI_API_KEY:
                raise RuntimeError("GEMINI_API_KEY not set in environment variables")
            
            self.model = model or GEMINI_MODEL
            self.client = genai.Client()
            print(f"✅ Initialized Google Gemini: {self.model}")
        
        elif self.provider == "openai":
            if not OPENAI_AVAILABLE:
                raise RuntimeError("OpenAI not installed. Install: pip install openai")
            if not OPENAI_API_KEY:
                raise RuntimeError("OPENAI_API_KEY not set in environment variables")
            
            self.model = model or OPENAI_MODEL
            client_kwargs = {"api_key": OPENAI_API_KEY}
            if OPENAI_BASE_URL:
                client_kwargs["base_url"] = OPENAI_BASE_URL
            
            self.client = OpenAI(**client_kwargs)
            print(f"✅ Initialized OpenAI: {self.model}")
        
        else:
            raise RuntimeError(f"Unknown LLM provider: {self.provider}. Use 'gemini' or 'openai'")
        
        # System prompt in Mongolian
        self.system_prompt = """Та мэргэжлийн цаг захиалгын туслах ассистент мөн. Таны үүрэг:

1. ХЭРЭГЛЭГЧИЙН ХҮСЭЛТИЙГ ОЙЛГОХ:
   - Шинэ захиалга үүсгэх
   - Захиалга цуцлах
   - Захиалга шалгах
   - Захиалга өөрчлөх

2. МЭДЭЭЛЭЛ ЦУГЛУУЛАХ:
   - Үйлчилгээний төрөл (үс засалт, шүдний үзлэг гэх мэт)
   - Огноо ба цаг
   - Хэрэглэгчийн нэр
   - Утасны дугаар

3. ЗАХИАЛГЫГ ШАЛГАХ:
   - Сул байгаа эсэхийг шалгах
   - Зөрчилдөөн байвал өөр цагийг санал болгох
   - Хэрэглэгчийн зөвшөөрөл авах

4. БАТАЛГААЖУУЛАХ:
   - Амжилттай бол батлагаажуулах мэдээлэл өгөх
   - Захиалгын дугаарыг өгөх

Та үргэлж ээлдэг, тодорхой, Монгол хэлээр хариулна. Хэрэв мэдээлэл дутуу бол асуулт асуух.

Та дараах функцүүдийг ашиглаж болно:
- check_availability: Цаг сул эсэхийг шалгах
- create_booking: Захиалга үүсгэх
- cancel_booking: Захиалга цуцлах
- list_bookings: Захиалгуудыг харах
- suggest_alternatives: Өөр цагийн сонголтуудыг санал болгох"""
        
        # Define available functions for function calling
        self.functions = [
            {
                "name": "check_availability",
                "description": "Check if a time slot is available for booking",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "date": {
                            "type": "string",
                            "description": "Date in YYYY-MM-DD format"
                        },
                        "time": {
                            "type": "string",
                            "description": "Time in HH:MM format (24-hour)"
                        },
                        "duration_minutes": {
                            "type": "integer",
                            "description": "Duration in minutes",
                            "default": 60
                        }
                    },
                    "required": ["date", "time"]
                }
            },
            {
                "name": "create_booking",
                "description": "Create a new booking appointment",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string"},
                        "user_name": {"type": "string"},
                        "phone": {"type": "string"},
                        "service": {"type": "string"},
                        "date": {"type": "string", "description": "YYYY-MM-DD"},
                        "time": {"type": "string", "description": "HH:MM"},
                        "duration_minutes": {"type": "integer", "default": 60}
                    },
                    "required": ["user_id", "user_name", "phone", "service", "date", "time"]
                }
            },
            {
                "name": "cancel_booking",
                "description": "Cancel an existing booking",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "booking_id": {"type": "string"},
                        "user_id": {"type": "string"}
                    }
                }
            },
            {
                "name": "list_bookings",
                "description": "List bookings for a user",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string"},
                        "status": {"type": "string"}
                    }
                }
            },
            {
                "name": "suggest_alternatives",
                "description": "Suggest alternative time slots",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "date": {"type": "string"},
                        "time": {"type": "string"},
                        "duration_minutes": {"type": "integer", "default": 60},
                        "count": {"type": "integer", "default": 3}
                    },
                    "required": ["date", "time"]
                }
            }
        ]
    
    def _execute_function(self, function_name: str, arguments: Dict) -> Dict:
        """
        Execute a function call and return the result
        
        Args:
            function_name: Name of the function to call
            arguments: Function arguments
            
        Returns:
            Function execution result
        """
        try:
            if function_name == "check_availability":
                return self.booking_manager.check_availability(**arguments)
            
            elif function_name == "create_booking":
                return self.booking_manager.create_booking(**arguments)
            
            elif function_name == "cancel_booking":
                return self.booking_manager.cancel_booking(**arguments)
            
            elif function_name == "list_bookings":
                return self.booking_manager.list_bookings(**arguments)
            
            elif function_name == "suggest_alternatives":
                return self.booking_manager.suggest_alternatives(**arguments)
            
            else:
                return {"error": f"Unknown function: {function_name}"}
        
        except Exception as e:
            return {"error": str(e)}
    
    def _call_llm(self, messages: List[Dict], use_functions: bool = True) -> Dict:
        """
        Call the LLM based on configured provider
        
        Args:
            messages: List of message dicts
            use_functions: Whether to enable function calling
            
        Returns:
            LLM response
        """
        try:
            if self.provider == "openai":
                return self._call_openai(messages, use_functions)
            elif self.provider == "gemini":
                return self._call_gemini(messages, use_functions)
            else:
                return {
                    'type': 'error',
                    'content': f"Unknown provider: {self.provider}"
                }
        except Exception as e:
            return {
                'type': 'error',
                'content': f"LLM Error ({self.provider}): {str(e)}"
            }
    
    def _call_openai(self, messages: List[Dict], use_functions: bool) -> Dict:
        """
        Call OpenAI API
        """
        try:
            if use_functions:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    functions=self.functions,
                    function_call="auto"
                )
            else:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages
                )
            
            message = response.choices[0].message
            
            # Check for function call
            if hasattr(message, 'function_call') and message.function_call:
                return {
                    'type': 'function_call',
                    'function_name': message.function_call.name,
                    'arguments': json.loads(message.function_call.arguments)
                }
            else:
                return {
                    'type': 'text',
                    'content': message.content
                }
        
        except Exception as e:
            return {
                'type': 'error',
                'content': f"OpenAI Error: {str(e)}"
            }
    
    def _call_gemini(self, messages: List[Dict], use_functions: bool) -> Dict:
        """
        Call Google Gemini API
        
        Note: Gemini doesn't support function calling in the same way as OpenAI,
        so we'll use structured output parsing instead.
        """
        try:
            # Convert messages to Gemini format
            conversation_text = self._convert_messages_to_text(messages)
            
            # Add function calling instructions if enabled
            if use_functions:
                function_instructions = self._get_function_instructions()
                conversation_text = f"{function_instructions}\n\n{conversation_text}"
            
            # Call Gemini
            response = self.client.models.generate_content(contents=conversation_text, model=self.model)
            
            if not response.text:
                return {
                    'type': 'error',
                    'content': "Gemini returned empty response"
                }
            
            # Try to parse function call from response
            if use_functions:
                function_call = self._parse_function_call_from_text(response.text)
                if function_call:
                    return function_call
            
            return {
                'type': 'text',
                'content': response.text
            }
        
        except Exception as e:
            return {
                'type': 'error',
                'content': f"Gemini Error: {str(e)}"
            }
    
    def _convert_messages_to_text(self, messages: List[Dict]) -> str:
        """
        Convert OpenAI-style messages to plain text for Gemini
        """
        text_parts = []
        for msg in messages:
            role = msg.get('role', '')
            content = msg.get('content', '')
            
            if role == 'system':
                text_parts.append(f"System Instructions:\n{content}")
            elif role == 'user':
                text_parts.append(f"User: {content}")
            elif role == 'assistant':
                text_parts.append(f"Assistant: {content}")
            elif role == 'function':
                function_name = msg.get('name', 'unknown')
                text_parts.append(f"Function {function_name} result: {content}")
        
        return "\n\n".join(text_parts)
    
    def _get_function_instructions(self) -> str:
        """
        Generate instructions for function calling for Gemini
        """
        return """
You have access to the following functions. When you need to use them, respond with JSON in this exact format:
{
  "function_call": {
    "name": "function_name",
    "arguments": {"arg1": "value1"}
  }
}

Available functions:
""" + json.dumps(self.functions, indent=2, ensure_ascii=False)
    
    def _parse_function_call_from_text(self, text: str) -> Optional[Dict]:
        """
        Try to extract function call from Gemini's text response
        """
        try:
            # Look for JSON block in response
            import re
            json_match = re.search(r'\{[^{}]*"function_call"[^{}]*\{[^{}]*\}[^{}]*\}', text, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group(0))
                if 'function_call' in parsed:
                    fc = parsed['function_call']
                    return {
                        'type': 'function_call',
                        'function_name': fc['name'],
                        'arguments': fc.get('arguments', {})
                    }
            return None
        except:
            return None
    
    def process_message(self, user_message: str, user_id: str = "default_user", 
                       session_id: Optional[str] = None) -> str:
        """
        Process a user message and return a response
        
        Args:
            user_message: The user's message
            user_id: User identifier
            session_id: Session identifier for conversation tracking
            
        Returns:
            Agent's response text
        """
        if session_id is None:
            session_id = user_id
        
        # Initialize conversation history for new sessions
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = [
                {"role": "system", "content": self.system_prompt}
            ]
        
        # Add user message to history
        self.conversation_history[session_id].append({
            "role": "user",
            "content": user_message
        })
        
        # Call LLM with conversation history
        max_iterations = 5  # Prevent infinite loops
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            llm_response = self._call_llm(
                self.conversation_history[session_id],
                use_functions=True  # Enable function calling for all providers
            )
            
            if llm_response['type'] == 'function_call':
                # Execute the function
                function_name = llm_response['function_name']
                arguments = llm_response['arguments']
                
                # Inject user_id if needed
                if 'user_id' in arguments and not arguments.get('user_id'):
                    arguments['user_id'] = user_id
                
                function_result = self._execute_function(function_name, arguments)
                
                # Add function call and result to conversation
                self.conversation_history[session_id].append({
                    "role": "assistant",
                    "content": None,
                    "function_call": {
                        "name": function_name,
                        "arguments": json.dumps(arguments, ensure_ascii=False)
                    }
                })
                
                self.conversation_history[session_id].append({
                    "role": "function",
                    "name": function_name,
                    "content": json.dumps(function_result, ensure_ascii=False)
                })
                
                # Continue to get the final text response
                continue
            
            elif llm_response['type'] == 'text':
                # Got a text response, return it
                response_text = llm_response['content']
                
                # Add to conversation history
                self.conversation_history[session_id].append({
                    "role": "assistant",
                    "content": response_text
                })
                
                return response_text
            
            else:  # error
                return llm_response['content']
        
        return "Уучлаарай, би таны хүсэлтийг боловсруулж чадсангүй. Дахин оролдоно уу."
    
    def clear_history(self, session_id: str):
        """Clear conversation history for a session"""
        if session_id in self.conversation_history:
            del self.conversation_history[session_id]
