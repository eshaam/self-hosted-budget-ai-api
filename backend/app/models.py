import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import logging
from app.config import settings
from typing import Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set environment variable to avoid tokenizer warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"

class AIModel:
    def __init__(self, model_name: str = "google/gemma-2-2b-it"):
        self.model = None
        self.tokenizer = None
        self.device = "cpu"  # Force CPU usage for compatibility
        self.model_name = model_name
        self.available_models = {
            "gemma": "google/gemma-2-2b-it",
            "qwen": "Qwen/Qwen2-0.5B-Instruct"
        }
        logger.info(f"Initializing model {model_name} on device: {self.device}")
        
    def load_model(self, model_name: Optional[str] = None) -> bool:
        """Load the specified model and tokenizer"""
        try:
            if model_name:
                self.model_name = model_name
            
            logger.info(f"Loading model: {self.model_name}...")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )
            
            # Load model with CPU optimization
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float32,  # Use float32 for CPU
                device_map=None,  # Don't use device_map for CPU
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )
            
            # Move to CPU explicitly
            if self.model:
                self.model = self.model.to(self.device)
            
            logger.info(f"Model {self.model_name} loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model {self.model_name}: {str(e)}")
            return False
    
    def generate_response(self, prompt: str, model_name: Optional[str] = None) -> str:
        """Generate response using the loaded model with CPU optimization"""
        try:
            # Switch model if requested
            if model_name and model_name != self.model_name:
                logger.info(f"Switching to model: {model_name}")
                if not self.load_model(model_name):
                    return f"Error: Failed to load model {model_name}"
            
            logger.info(f"Starting response generation for prompt: {prompt[:50]}...")
            
            if not self.model or not self.tokenizer:
                logger.info("Model not loaded, attempting to load...")
                if not self.load_model():
                    return "Error: Model failed to load"
            
            logger.info("Model loaded successfully, generating response...")
            
            # Format prompt based on model type
            if "gemma" in self.model_name.lower():
                formatted_prompt = f"<start_of_turn>user\n{prompt}<end_of_turn>\n<start_of_turn>model\n"
            else:  # Qwen format
                formatted_prompt = f"<|im_start|>system\nYou are a helpful AI assistant.<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"
            
            # Tokenize input with increased max length
            inputs = self.tokenizer(
                formatted_prompt, 
                return_tensors="pt", 
                truncation=True, 
                max_length=2048
            )
            
            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            logger.info("Starting model generation...")
            
            # CPU-optimized generation settings
            with torch.no_grad():
                # Set number of threads for CPU efficiency
                torch.set_num_threads(2)  # Limit CPU threads
                
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=min(settings.MAX_NEW_TOKENS, 200),  # Increased for better responses
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    repetition_penalty=1.1,
                    num_beams=1,
                    early_stopping=True,
                    use_cache=True
                )
            
            logger.info("Model generation completed, decoding response...")
            
            # Decode response
            response = self.tokenizer.decode(
                outputs[0][inputs['input_ids'].shape[1]:], 
                skip_special_tokens=True
            ).strip()
            
            logger.info(f"Response generated successfully: {response[:50]}...")
            return response if response else "I'm sorry, I couldn't generate a response."
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return f"Error generating response: {str(e)}"
    

# Global model instance - Default to Gemma
ai_model = AIModel("google/gemma-2-2b-it")

def generate_response(prompt: str, model_name: Optional[str] = None) -> str:
    """Public function to generate response"""
    return ai_model.generate_response(prompt, model_name)

def get_available_models() -> Dict[str, str]:
    """Get list of available models"""
    return ai_model.available_models

def get_current_model() -> str:
    """Get current model name"""
    return ai_model.model_name